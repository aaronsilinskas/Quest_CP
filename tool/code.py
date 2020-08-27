import time
import math
import board
from digitalio import DigitalInOut, Direction, Pull
import busio
import adafruit_lis3dh
from state import State, StateMachine

# Use the CircuitPlayground built-in accelerometer if available,
# otherwise check I2C pins.
if hasattr(board, "ACCELEROMETER_SCL"):
    i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
    int1 = DigitalInOut(board.ACCELEROMETER_INTERRUPT)
    lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19, int1=int1)
else:
    i2c = busio.I2C(board.SCL, board.SDA)
    int1 = DigitalInOut(board.D6)  # Set to correct pin for interrupt!
    lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
lis3dh.range = adafruit_lis3dh.RANGE_2_G

# Trigger
trigger = DigitalInOut(board.A3)
trigger.direction = Direction.INPUT
trigger.pull = Pull.UP

# States
state_machine = StateMachine()

class TestState1(State):

    def __init__(self):
        self.some_var = 123
        self.time_remaining = None

    @property
    def name(self):
        return 'test1'

    def enter(self):
        State.enter(self)
        self.time_remaining = 2

    def exit(self):
        State.exit(self)

    def update(self, ellapsed):
        print("Test 1 Remaining: {}, Ellapsed: {}".format(self.time_remaining, ellapsed))

        self.time_remaining -= ellapsed
        if self.time_remaining <= 0:
            return 'test2'
        return self.name

state_machine.add_state(TestState1())

class TestState2(State):

    def __init__(self):
        self.time_remaining = None

    @property
    def name(self):
        return 'test2'

    def enter(self):
        State.enter(self)
        self.time_remaining = 3

    def exit(self):
        State.exit(self)

    def update(self, ellapsed):
        print("Test 2 Remaining: {}, Ellapsed: {}".format(self.time_remaining, ellapsed))

        self.time_remaining -= ellapsed
        if self.time_remaining <= 0:
            return 'test1'
        return self.name

state_machine.add_state(TestState2())

state_machine.go_to_state('test1')

while True:

    # Terms
    # - Spell slot - an array of weaved spells that are stored until they
    #   are cast or decay
    # - Cast - the most recent spell is taken from a spell slot and transmitted
    # - Weave - a set of gestures is weaving a spell that is stored in a
    #   spell slot

    # Main states
    # - Spell slot being cast
    # - Spell weaving
    #   - If click less than 1/2 second, cast the last spell slot
    #   - Within 1-2 seconds, a spell is selected
    #   - Until click ends, weave spell
    #   - Spell is stored in spell slots
    # - Idle
    # Global
    # - spell modifiers
    # - spell slot updates
    # - LED updates
    # - sound updates

    # If trigger is pulled, casting state starts
    #   If trigger is let go, casting finishes
    # If casting less than 1/2 second, consider it a spell use

    # For each active spell, update the spell state

    # Apply LED updates for casting
    # Apply LED updates for active spells
    # Play casting sound

    # Read accelerometer values (in m / s ^ 2).  Returns a 3-tuple of x, y,
    # z axis values.  Divide them by 9.806 to convert to Gs.
    x, y, z = [
        value / adafruit_lis3dh.STANDARD_GRAVITY for value in lis3dh.acceleration
    ]

    print("(%0.3f,%0.3f,%0.3f)" % (x, y, z))

    # x = pointing up or down. Up = -1, Down = 1
    # z, y = rotation. Flat = abs(z)=1, y=0. On edge = abs(z)=0,abs(y)=1

    if trigger.value == 0:
        print("trigger held")

    state_machine.update()

    time.sleep(0.1)