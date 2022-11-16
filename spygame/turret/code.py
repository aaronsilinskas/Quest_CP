#

"""
Laser Turret - Capture IR data to button A or B, then play it back in transmit mode
Switch Off - Configuration mode (currently no functions)
Switch On - Start countdown to enter Sentry mode

States:
Sentry - Waits to be hit before switching to Active
Active - Shoot one or more times with random delays. Green LEDs indicate hit points remaining
Neutralized - When hit points is reduced to 0, the turret is out of the game until the switch is toggled or power is cycled 
"""

import pulseio
import pwmio
import board
import array
import random
from digitalio import DigitalInOut, Direction, Pull
from simpleio import map_range
from neopixel import NeoPixel
from audiocore import WaveFile
try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!
from adafruit_irremote import GenericDecode
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.sparklepulse import SparklePulse

from state import Thing, State, StateMachine

# CONFIGURATION
import config

# HARDWARE INITIALIZATION
switch = DigitalInOut(board.SLIDE_SWITCH)
switch.direction = Direction.INPUT
switch.pull = Pull.UP
# Optional external switch on pin A1
switch_external = DigitalInOut(board.A1)
switch_external.direction = Direction.INPUT
switch_external.pull = Pull.UP

button_a = DigitalInOut(board.BUTTON_A)
button_a.direction = Direction.INPUT
button_a.pull = Pull.DOWN
# Optional external button A on pin A2
button_a_external = DigitalInOut(board.A2)
button_a_external.direction = Direction.INPUT
button_a_external.pull = Pull.DOWN

button_b = DigitalInOut(board.BUTTON_B)
button_b.direction = Direction.INPUT
button_b.pull = Pull.DOWN
# Optional external button B on pin A3
button_b_external = DigitalInOut(board.A3)
button_b_external.direction = Direction.INPUT
button_b_external.pull = Pull.DOWN

pixels = NeoPixel(board.NEOPIXEL, 10, auto_write=False, brightness=0.05)

audio = AudioOut(board.AUDIO)
speaker_enable = DigitalInOut(board.SPEAKER_ENABLE)
speaker_enable.direction = Direction.OUTPUT
speaker_enable.value = config.SOUND_ENABLED

pulse_in = pulseio.PulseIn(board.RX, maxlen=120, idle_state=True)
pulse_in.clear()
ir_decoder = GenericDecode()

pwm_out = pwmio.PWMOut(board.TX, frequency=38000, duty_cycle=2 ** 15)
pulse_out = pulseio.PulseOut(pwm_out)

# ANIMATIONS
configure_animation = Comet(
    pixels, speed=0.2, color=config.WHITE, tail_length=7, bounce=True)
sentry_animation = Comet(pixels, speed=0.1, color=config.WHITE,
                         tail_length=4, bounce=True)
neutralized_animation = SparklePulse(
    pixels, 0.01, config.COLOR_NEUTRALIZED, period=0.5, min_intensity=0, max_intensity=0.1)

# STATE MACHINE


class Turret(Thing):
    def __init__(self):
        super().__init__()

        self.reset(config.STARTING_TEAM)

    def reset(self, team):
        # Turret threat tracking
        self.active_time_remaining = 0
        self.shoot_delay = 0
        self.shots_to_take = 0
        self.shot_charge = 0

        # Hit points
        self.hit_point_max = random.randint(
            config.HIT_POINT_MIN, config.HIT_POINT_MAX)
        self.hit_points = self.hit_point_max
        print("Hit points reset: ", self. hit_points)

        # Team
        self.setup_team(team)

    def setup_team(self, team):
        self.team = team
        if self.team == 1:
            self.team_color = config.TEAM_1_COLOR
            self.shoot_pulse = config.TEAM_1_SHOOT_PULSE
            self.hit_pulse = config.TEAM_2_SHOOT_PULSE
        elif self.team == 2:
            self.team_color = config.TEAM_2_COLOR
            self.shoot_pulse = config.TEAM_2_SHOOT_PULSE
            self.hit_pulse = config.TEAM_1_SHOOT_PULSE
        else:
            self.team_color = config.WHITE
            self.shoot_pulse = []
            self.hit_pulse = []


def configure_mode():
    return switch.value ^ switch_external.value


def team_1_button_down():
    return button_a.value or button_a_external.value


def team_2_button_down():
    return button_b.value or button_b_external.value


def randfloat(start, end):
    return (end - start) * random.random() + start


def check_pulses(hit_pulse):
    pulses = ir_decoder.read_pulses(pulse_in, max_pulse=10000, blocking=False)
    if pulses:
        print("Pulses: ", pulses)
        if len(pulses) < 2:
            return None

        if len(pulses) != len(hit_pulse):
            return States.active

        for expected_pulse in hit_pulse:
            pulse_delta = abs(expected_pulse - pulses.pop(0))
            if pulse_delta > 150:
                return States.active

        return States.hit

    return None


def fill_pixel_range(x, x_min, x_max, color):
    pixels_on = int(map_range(x, x_min, x_max, 0, pixels.n))
    pixels.fill(0)
    for i in range(0, pixels_on):
        pixels[i] = color

    return pixels_on


last_sound_file = None
last_wave = None


def play_sound(sound_file):
    if not config.SOUND_ENABLED:
        return

    global last_sound_file
    global last_wave

    if sound_file != last_sound_file:
        print("Loading wave file: ", sound_file)
        last_sound_file = sound_file
        wave_file = open(sound_file, "rb")
        last_wave = WaveFile(wave_file)
    print("Playing wave file: ", sound_file)
    audio.play(last_wave)


class States:
    configure: State
    countdown: State
    sentry: State
    active: State
    charge_shot: State
    shoot: State
    hit: State
    neutralized: State
    capturing: State


class Configure(State):
    def enter(self, thing: Turret):
        pixels.fill(0)
        pixels.show()

    def update(self, thing: Turret):
        if not configure_mode():
            return States.countdown

        pulses = ir_decoder.read_pulses(
            pulse_in, max_pulse=10000, blocking=False)
        if pulses:
            print("Pulses: ", pulses)
            print("Rounded: [", end="")
            for idx, pulse in enumerate(pulses):
                end = ", " if idx < len(pulses) - 1 else ""
                print(int(round(pulse / 100)) * 100, end=end)
            print("]")
            print()

        if team_1_button_down():
            next_team = thing.team + 1 if thing.team < 2 else 0
            print("Starting team: ", next_team)
            thing.setup_team(next_team)
            configure_animation.color = thing.team_color

            while team_1_button_down():
                True
        if team_2_button_down():
            print("Test")

            # add test code here

            while team_2_button_down():
                True

        configure_animation.animate()
        pixels.show()

        return self


States.configure = Configure()


class Countdown(State):
    def enter(self, thing: Turret):
        thing.reset(thing.team)

        thing.next_sound_pixel_count = 0

        pixels.fill(0)
        pixels.show()

    def update(self, thing: Turret):
        if configure_mode():
            return States.configure

        if int(thing.time_active) == config.COUNTDOWN_SECONDS:
            play_sound("sounds\countdown-done.wav")
            if (thing.team == 0):
                return States.neutralized
            return States.sentry

        current_pixels = fill_pixel_range(thing.time_active, 0,
                                          config.COUNTDOWN_SECONDS, thing.team_color)

        if current_pixels >= thing.next_sound_pixel_count:
            play_sound("sounds\countdown-tick.wav")
            thing.next_sound_pixel_count = current_pixels + 2

        pixels.show()

        return self


States.countdown = Countdown()


class Sentry(State):
    def enter(self, thing: Turret):
        sentry_animation.color = thing.team_color

        pixels.fill(0)
        pixels.show()

    def update(self, thing: Turret):
        if configure_mode():
            return States.configure

        pulses_state = check_pulses(thing.hit_pulse)
        if pulses_state:
            return pulses_state

        sentry_animation.animate()
        pixels.show()

        return self


States.sentry = Sentry()


class Active(State):
    def enter(self, thing: Turret):
        if thing.active_time_remaining <= 0:
            print("Resetting active time")
            thing.active_time_remaining = randfloat(
                config.ACTIVE_TIME_MIN, config.ACTIVE_TIME_MAX)

    def update(self, thing: Turret):
        thing.active_time_remaining -= thing.time_ellapsed
        if thing.active_time_remaining <= 0:
            return States.sentry

        if thing.shots_to_take > 0:
            thing.shots_to_take -= 1
            return States.charge_shot
        elif thing.shoot_delay > 0:
            thing.shoot_delay -= thing.time_ellapsed
            if thing.shoot_delay <= 0:
                thing.shots_to_take = random.randint(
                    0, config.MAX_SHOT_BURST)
                return States.charge_shot
        else:
            thing.shoot_delay = randfloat(
                config.SHOOT_DELAY_MIN, config.SHOOT_DELAY_MAX)

        pulses_state = check_pulses(thing.hit_pulse)
        if pulses_state:
            return pulses_state

        fill_pixel_range(thing.hit_points, 0,
                         thing.hit_point_max, config.COLOR_HITPOINTS)
        if thing.hit_points != thing.hit_point_max:
            # Fade last pixel if it's a partial hit point
            last_pixel = pixels.n * \
                (thing.hit_points / thing.hit_point_max)

            partial_hitpoint = last_pixel % 1
            hp_red = config.COLOR_HITPOINTS >> 16
            hp_green = (config.COLOR_HITPOINTS >> 8) & 0xFF
            hp_blue = config.COLOR_HITPOINTS & 0xFF

            pixels[int(last_pixel)] = (hp_red * partial_hitpoint,
                                       hp_green * partial_hitpoint, hp_blue * partial_hitpoint)

        pixels.show()

        return self


States.active = Active()


class ChargeShot(State):
    def enter(self, thing: Turret):
        print("Charging shot")
        play_sound("sounds\charging.wav")

        thing.shot_charge = 0
        pass

    def update(self, thing: Turret):
        thing.shot_charge += thing.time_ellapsed
        if thing.shot_charge > config.SHOT_CHARGE_TIME:
            return States.shoot

        fill_pixel_range(thing.shot_charge, 0,
                         config.SHOT_CHARGE_TIME, config.COLOR_SHOT_CHARGE)
        pixels.show()

        return self


States.charge_shot = ChargeShot()


class Shoot(State):
    def enter(self, thing: Turret):
        print("Shooting!")

    def update(self, thing: Turret):
        pixels.fill(config.COLOR_SHOOTING)
        pixels.show()

        pulse_in.pause()
        pulses = array.array("H", thing.shoot_pulse)
        print(pulses)
        pulse_out.send(pulses)

        pulse_in.resume()
        pulse_in.clear()

        play_sound("sounds\shoot.wav")
        while audio.playing:
            True

        return States.active


States.shoot = Shoot()


class Hit(State):
    def enter(self, thing: Turret):
        thing.hit_points -= 1
        print("Hit! ", thing.hit_points)
        play_sound("sounds\hit.wav")

    def update(self, thing: Turret):
        if thing.hit_points <= 0:
            return States.neutralized

        thing.active_time_remaining = 0  # causes a refresh on active time
        return States.active


States.hit = Hit()


class Neutralized(State):
    def enter(self, thing: Turret):
        print("Neutralized!")
        pixels.fill(0)
        pixels.show()

    def update(self, thing: Turret):
        if team_1_button_down() or team_2_button_down():
            return States.capturing

        neutralized_animation.animate()
        pixels.show()

        return self


States.neutralized = Neutralized()


class Capturing(State):
    def _button_team(self):
        if team_1_button_down():
            return 1
        if team_2_button_down():
            return 2
        return 0

    def enter(self, thing: Turret):
        thing.setup_team(self._button_team())

        pixels.fill(0)
        pixels.show()

    def update(self, thing: Turret):
        current_team = self._button_team()
        if current_team != thing.team or current_team == 0:
            return States.neutralized

        if int(thing.time_active) > config.CAPTURE_SECONDS:
            print("Captured: ", thing.team)
            thing.reset(thing.team)
            return States.sentry

        fill_pixel_range(thing.time_active, 0,
                         config.CAPTURE_SECONDS, thing.team_color)
        pixels.show()

        return self


States.capturing = Capturing()


# MAIN LOOP
turret = Turret()
state_machine = StateMachine()

if configure_mode():
    state_machine.go_to_state(States.configure, turret)
else:
    state_machine.go_to_state(States.countdown, turret)

while True:
    if configure_mode() and turret.state != States.configure:
        state_machine.go_to_state(States.configure, turret)

    state_machine.update(turret)
