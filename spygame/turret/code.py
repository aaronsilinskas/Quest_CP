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

buttonA = DigitalInOut(board.BUTTON_A)
buttonA.direction = Direction.INPUT
buttonA.pull = Pull.DOWN

buttonB = DigitalInOut(board.BUTTON_B)
buttonB.direction = Direction.INPUT
buttonB.pull = Pull.DOWN

pixels = NeoPixel(board.NEOPIXEL, 10, auto_write=False, brightness=0.1)

pulse_in = pulseio.PulseIn(board.RX, maxlen=120, idle_state=True)
pulse_in.clear()
ir_decoder = GenericDecode()

pwm_out = pwmio.PWMOut(board.TX, frequency=38000, duty_cycle=2 ** 15)
pulse_out = pulseio.PulseOut(pwm_out)

# ANIMATIONS
sentryAnimation = Comet(pixels, 0.1, config.COLOR_SENTRY,
                        tail_length=4, bounce=True)
neutralizedAnimation = SparklePulse(
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


def check_hit(context: TurretContext):
    pulses = ir_decoder.read_pulses(pulse_in, max_pulse=10000, blocking=False)
    # TODO will need to compare each pulse to within a threshold of the target value, can't just compare the values
    if pulses:
        print(pulses)
        return True

    return False


def fill_pixel_range(x, x_min, x_max, color):
    pixels_on = map_range(x, x_min, x_max, 0, pixels.n)
    pixels.fill(0)
    for i in range(0, pixels_on):
        pixels[i] = color


class States:
    configure: State
    countdown: State
    sentry: State
    active: State
    charge_shot: State
    shoot: State
    hit: State
    neutralized: State


class Configure(State):
    def enter(self, context: TurretContext):
        pixels.fill(0)
        pixels.show()

    def update(self, context: TurretContext):
        if switch.value:
            return States.countdown

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
            return States.sentry

        fill_pixel_range(context.time_active, 0,
                         config.COUNTDOWN_SECONDS, config.COLOR_COUNTDOWN)
        pixels.show()

        return self


States.countdown = Countdown()


class Sentry(State):
    def enter(self, context: TurretContext):
        pixels.fill(0)
        pixels.show()

    def update(self, context: TurretContext):
        if not switch.value:
            return States.configure

        if check_hit(context):
            return States.hit

        sentryAnimation.animate()
        pixels.show()

        return self


States.sentry = Sentry()


class Active(State):
    def update(self, context: TurretContext):
        if not switch.value:
            return States.configure

        context.active_time_remaining -= context.time_ellapsed
        if context.active_time_remaining <= 0:
            return States.sentry

        if check_hit(context):
            return States.hit

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
            context.shoot_delay = random.randint(
                config.SHOOT_DELAY_MIN, config.SHOOT_DELAY_MAX)

        fill_pixel_range(context.hit_points, 0,
                         context.hit_point_max, config.COLOR_HITPOINTS)
        pixels.show()

        return self


States.active = Active()


class ChargeShot(State):
    def enter(self, context: TurretContext):
        print("Charging shot")
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
        pulses = array.array("H", config.IR_PULSE_SHOOT)
        print(pulses)
        pulse_out.send(pulses)

        pulse_in.resume()
        pulse_in.clear()

        return States.active


States.shoot = Shoot()


class Hit(State):
    def enter(self, context: TurretContext):
        context.hit_points -= 1
        context.active_time_remaining = random.randint(
            config.ACTIVE_TIME_MIN, config.ACTIVE_TIME_MAX)
        print("Hit! ", context.hit_points)

    def update(self, context: TurretContext):
        if context.hit_points <= 0:
            return States.neutralized

        context.threat_level = 2
        return States.active


States.hit = Hit()


class Neutralized(State):
    def enter(self, context: TurretContext):
        print("Disabled!")
        pixels.fill(0)
        pixels.show()

    def update(self, context: TurretContext):
        if not switch.value:
            return States.configure
        
        neutralizedAnimation.animate()
        pixels.show()

        return self


States.neutralized = Neutralized()


# MAIN LOOP
state_context = TurretContext()
state_machine = StateMachine()

if switch.value:
    state_machine.go_to_state(States.countdown, state_context)
else:
    state_machine.go_to_state(States.configure, state_context)

while True:
    state_machine.update(state_context)
