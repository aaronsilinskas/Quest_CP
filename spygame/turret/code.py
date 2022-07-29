#

"""
Laser Turret - Capture IR data to button A or B, then play it back in transmit mode
Switch off - Receive - captures IR raw data and assign the pulses to button A or B (whichever is held down)
Switch On - Transmit - transmits captured IR data when the A or B button is pressed
- Button - transmit the last IR data 
"""

import pulseio
import pwmio
import board
import array
from digitalio import DigitalInOut, Direction, Pull
from neopixel import NeoPixel
from adafruit_irremote import GenericDecode
from adafruit_led_animation.animation.comet import Comet

from state import StateContext, State, StateMachine

# CONFIGURATION
from config import COLOR_COUNTDOWN, COLOR_SENTRY

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

pixels = NeoPixel(board.NEOPIXEL, 10, auto_write=False, brightness=0.01)

pulse_in = pulseio.PulseIn(board.RX, maxlen=120, idle_state=True)
ir_decoder = GenericDecode()

pwm_out = pwmio.PWMOut(board.TX, frequency=38000, duty_cycle=2 ** 15)
pulse_out = pulseio.PulseOut(pwm_out)

# ANIMATIONS
sentryAnimation = Comet(pixels, 0.1, COLOR_SENTRY, tail_length=4, bounce=True)

# STATE MACHINE

class TurretContext(StateContext):
    def __init__(self):
        super().__init__()

        # Turret threat tracking
        self.threat_level = 0


class States:
    configure: State
    countdown: State
    sentry: State
    active: State
    shoot: State
    hit: State
    disabled: State

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
        pixels.fill(0)
        pixels.show()

    def update(self, context: TurretContext):
        if not switch.value:
            return States.configure
        if context.time_active >= 11:
            return States.sentry

        for i in range(0, int(context.time_active)):
            pixels[i] = COLOR_COUNTDOWN
        pixels.show()

        return self

States.countdown = Countdown()

class Sentry(State):
    def enter(self, context: TurretContext):
        pixels.fill(0)
        pixels.show()

    def update(self, context: TurretContext):

        sentryAnimation.animate()
        pixels.show()

        return self

States.sentry = Sentry()

# class Receive(State):
#     def update(self, context: IRCopierContext):
#         if switch.value:
#             return States.transmit

#         pulses = ir_decoder.read_pulses(
#             pulse_in, max_pulse=10000, blocking=False)
#         if pulses:
#             pulseArray = array.array("H", pulses)
#             print("Pulses received:")
#             print(pulseArray)

#             if buttonA.value == 1:
#                 context.button_a_pulses = pulseArray
#                 print("Assigned to Button A")
#             if buttonB.value == 1:
#                 context.button_b_pulses = pulseArray
#                 print("Assigned to Button B")

#         return self


# States.receive = Receive()


# class Transmit(State):
#     def _send_pulses(self, pulses):
#         if not pulses:
#             print("No pulses recorded")
#             return

#         pulse_in.pause()
#         print("Sending pulses")
#         print(pulses)
#         pulse_out.send(pulses)

#         pulse_in.resume()

#     def update(self, context: IRCopierContext):
#         if not switch.value:
#             return States.receive

#         if buttonA.value == 1:
#             self._send_pulses(context.button_a_pulses)

#             while (buttonA.value == 1):
#                 True
#         elif buttonB.value == 1:
#             self._send_pulses(context.button_b_pulses)

#             while (buttonB.value == 1):
#                 True

#         return self


# States.transmit = Transmit()

# MAIN LOOP
state_context = TurretContext()
state_machine = StateMachine()

if switch.value:
    state_machine.go_to_state(States.countdown, state_context)
else:
    state_machine.go_to_state(States.configure, state_context)

while True:
    state_machine.update(state_context)
