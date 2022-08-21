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

from state import StateContext, State, StateMachine

# CONFIGURATION
import config

# HARDWARE INITIALIZATION
switch = DigitalInOut(board.SLIDE_SWITCH)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

button_a = DigitalInOut(board.BUTTON_A)
button_a.direction = Direction.INPUT
button_a.pull = Pull.DOWN

button_b = DigitalInOut(board.BUTTON_B)
button_b.direction = Direction.INPUT
button_b.pull = Pull.DOWN

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


class TurretContext(StateContext):
    def __init__(self):
        super().__init__()

        # Turret threat tracking
        self.active_time_remaining = 0
        self.hit_point_max = 0
        self.hit_points = 0
        self.shoot_delay = 0
        self.shots_to_take = 0
        self.shot_charge = 0

        # Team
        self.setup_team(config.STARTING_TEAM)

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


def randfloat(start, end):
    return (end - start) * random.random() + start


def check_pulses(context: TurretContext):
    pulses = ir_decoder.read_pulses(pulse_in, max_pulse=10000, blocking=False)
    if pulses:
        print("Pulses: ", pulses)
        if len(pulses) < 2:
            return None

        if len(pulses) != len(context.hit_pulse):
            return States.active

        for expected_pulse in context.hit_pulse:
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
    def enter(self, context: TurretContext):
        pixels.fill(0)
        pixels.show()

    def update(self, context: TurretContext):
        if switch.value:
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

        if button_a.value:
            next_team = context.team + 1 if context.team < 2 else 0
            context.setup_team(next_team)
            configure_animation.color = context.team_color

            while button_a.value:
                True
        if button_b.value:
            print("Test")

            # add test code here

            while button_b.value:
                True

        configure_animation.animate()
        pixels.show()

        return self


States.configure = Configure()


class Countdown(State):
    def enter(self, context: TurretContext):
        context.hit_point_max = random.randint(
            config.HIT_POINT_MIN, config.HIT_POINT_MAX)
        context.hit_points = context.hit_point_max

        pixels.fill(0)
        pixels.show()

    def update(self, context: TurretContext):
        if not switch.value:
            return States.configure
        if int(context.time_active) > config.COUNTDOWN_SECONDS:
            if (context.team == 0):
                return States.neutralized
            return States.sentry

        fill_pixel_range(context.time_active, 0,
                         config.COUNTDOWN_SECONDS, context.team_color)
        pixels.show()

        return self


States.countdown = Countdown()


class Sentry(State):
    def enter(self, context: TurretContext):
        sentry_animation.color = context.team_color

        pixels.fill(0)
        pixels.show()

    def update(self, context: TurretContext):
        if not switch.value:
            return States.configure

        pulses_state = check_pulses(context)
        if pulses_state:
            return pulses_state

        sentry_animation.animate()
        pixels.show()

        return self


States.sentry = Sentry()


class Active(State):
    def enter(self, context: TurretContext):
        if context.active_time_remaining <= 0:
            print("Resetting active time")
            context.active_time_remaining = randfloat(
                config.ACTIVE_TIME_MIN, config.ACTIVE_TIME_MAX)

    def update(self, context: TurretContext):
        if not switch.value:
            return States.configure

        context.active_time_remaining -= context.time_ellapsed
        if context.active_time_remaining <= 0:
            return States.sentry

        if context.shots_to_take > 0:
            context.shots_to_take -= 1
            return States.charge_shot
        elif context.shoot_delay > 0:
            context.shoot_delay -= context.time_ellapsed
            if context.shoot_delay <= 0:
                context.shots_to_take = random.randint(
                    0, config.MAX_SHOT_BURST)
                return States.charge_shot
        else:
            context.shoot_delay = randfloat(
                config.SHOOT_DELAY_MIN, config.SHOOT_DELAY_MAX)

        pulses_state = check_pulses(context)
        if pulses_state:
            return pulses_state

        fill_pixel_range(context.hit_points, 0,
                         context.hit_point_max, config.COLOR_HITPOINTS)
        pixels.show()

        return self


States.active = Active()


class ChargeShot(State):
    def enter(self, context: TurretContext):
        print("Charging shot")
        play_sound("sounds\charging.wav")

        context.shot_charge = 0
        pass

    def update(self, context: TurretContext):
        context.shot_charge += context.time_ellapsed
        if context.shot_charge > config.SHOT_CHARGE_TIME:
            return States.shoot

        fill_pixel_range(context.shot_charge, 0,
                         config.SHOT_CHARGE_TIME, config.COLOR_SHOT_CHARGE)
        pixels.show()

        return self


States.charge_shot = ChargeShot()


class Shoot(State):
    def enter(self, context: TurretContext):
        print("Shooting!")

    def update(self, context: TurretContext):
        pixels.fill(config.COLOR_SHOOTING)
        pixels.show()

        pulse_in.pause()
        pulses = array.array("H", context.shoot_pulse)
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
    def enter(self, context: TurretContext):
        context.hit_points -= 1
        print("Hit! ", context.hit_points)
        play_sound("sounds\hit.wav")

    def update(self, context: TurretContext):
        if context.hit_points <= 0:
            return States.neutralized

        context.active_time_remaining = 0  # causes a refresh on active time
        return States.active


States.hit = Hit()


class Neutralized(State):
    def enter(self, context: TurretContext):
        print("Neutralized!")
        pixels.fill(0)
        pixels.show()

    def update(self, context: TurretContext):
        if not switch.value:
            return States.configure

        if button_a.value or button_b.value:
            return States.capturing

        neutralized_animation.animate()
        pixels.show()

        return self


States.neutralized = Neutralized()


class Capturing(State):
    def _button_team(self):
        if button_a.value:
            return 1
        if button_b.value:
            return 2
        return 0

    def enter(self, context: TurretContext):
        context.setup_team(self._button_team())

        pixels.fill(0)
        pixels.show()

    def update(self, context: TurretContext):
        current_team = self._button_team()
        if current_team != context.team or current_team == 0:
            return States.neutralized

        if int(context.time_active) > config.CAPTURE_SECONDS:
            print("Captured: ", context.team)
            context.setup_team(context.team)
            return States.sentry

        fill_pixel_range(context.time_active, 0,
                         config.CAPTURE_SECONDS, context.team_color)
        pixels.show()

        return self


States.capturing = Capturing()


# MAIN LOOP
state_context = TurretContext()
state_machine = StateMachine()

if switch.value:
    state_machine.go_to_state(States.countdown, state_context)
else:
    state_machine.go_to_state(States.configure, state_context)

while True:
    state_machine.update(state_context)
