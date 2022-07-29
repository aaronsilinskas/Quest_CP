#

"""
Infrared Copier - Capture IR data to button A or B, then play it back in transmit mode
Switch off - Receive - captures IR raw data and assign the pulses to button A or B (whichever is held down)
Switch On - Transmit - transmits captured IR data when the A or B button is pressed
- Button - transmit the last IR data 
"""

import pulseio
import pwmio
import board
import array
from digitalio import DigitalInOut, Direction, Pull
from adafruit_irremote import GenericDecode

from state import StateContext, State, StateMachine

# CONFIGURATION

# NERF Lazer Tag captured pulses
LT_SOLO   = [3000, 6000, 3000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000]
LT_TEAM_1 = [3000, 6000, 3000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 2000, 1000, 2000, 1000]
LT_TEAM_2 = [3000, 6000, 3000, 2000, 1000, 2000, 1000, 2000, 1000, 2000, 2000, 2000, 1000, 2000, 1000, 2000, 1000]


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

pulse_in = pulseio.PulseIn(board.RX, maxlen=120, idle_state=True)
ir_decoder = GenericDecode()

pwm_out = pwmio.PWMOut(board.TX, frequency=38000, duty_cycle=2 ** 15)
pulse_out = pulseio.PulseOut(pwm_out)


# STATE MACHINE

class IRCopierContext(StateContext):
    def __init__(self):
        super().__init__()

        # receiving pulses
        self.button_a_pulses = None
        self.button_b_pulses = None


class States:
    receive: State
    transmit: State


class Receive(State):
    def update(self, context: IRCopierContext):
        if switch.value:
            return States.transmit

        pulses = ir_decoder.read_pulses(
            pulse_in, max_pulse=10000, blocking=False)
        if pulses:
            pulseArray = array.array("H", pulses)
            print("Pulses received:")
            print(pulseArray)

            if buttonA.value == 1:
                context.button_a_pulses = pulseArray
                print("Assigned to Button A")
            if buttonB.value == 1:
                context.button_b_pulses = pulseArray
                print("Assigned to Button B")

        return self


States.receive = Receive()


class Transmit(State):
    def _send_pulses(self, pulses):
        if not pulses:
            print("No pulses recorded")
            return

        pulse_in.pause()
        print("Sending pulses")
        print(pulses)
        pulse_out.send(pulses)

        pulse_in.resume()

    def update(self, context: IRCopierContext):
        if not switch.value:
            return States.receive

        if buttonA.value == 1:
            self._send_pulses(context.button_a_pulses)

            while (buttonA.value == 1):
                True
        elif buttonB.value == 1:
            self._send_pulses(context.button_b_pulses)

            while (buttonB.value == 1):
                True

        return self


States.transmit = Transmit()

# MAIN LOOP
state_context = IRCopierContext()
state_machine = StateMachine()

if switch.value:
    state_machine.go_to_state(States.transmit, state_context)
else:
    state_machine.go_to_state(States.receive, state_context)

while True:
    state_machine.update(state_context)
