import time
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

class Idle(State):

    @property
    def name(self):
        return 'idle'

    def update(self, ellapsed):
        if trigger.value == 0:
            return 'triggered'
        return self.name

state_machine.add_state(Idle())

class Triggered(State):

    def __init__(self):
        self.time_remaining = None

    @property
    def name(self):
        return 'triggered'

    def enter(self):
        State.enter(self)
        self.time_remaining = 0.5

    def update(self, ellapsed):
        if trigger.value == 1:
            return 'casting'

        self.time_remaining -= ellapsed
        if self.time_remaining <= 0:
            return 'weaving'
        return self.name

state_machine.add_state(Triggered())

class Casting(State):

    def __init__(self):
        self.spell = None

    @property
    def name(self):
        return 'casting'

    def enter(self):
        State.enter(self)

        self.spell = 'Fireball!!!!'
        # Need to get last spell from spell slots

    def update(self, ellapsed):
        print("Casting: {}".format(self.spell))

        return 'idle'

state_machine.add_state(Casting())

class Weaving(State):

    def __init__(self):
        self.spell = None
        self.initial_acceleration = [None, None, None]
        self.min_acceleration = [None, None, None]
        self.max_acceleration = [None, None, None]

    @property
    def name(self):
        return 'weaving'

    def enter(self):
        State.enter(self)

        self.initial_acceleration = self.measure()
        self.min_acceleration = self.initial_acceleration.copy()
        self.max_acceleration = self.initial_acceleration.copy()

    def update(self, ellapsed):
        sample = self.measure()

        self.min_acceleration = list(map(min, sample, self.min_acceleration))
        self.max_acceleration = list(map(max, sample, self.max_acceleration))

        self.print_xyz("Sample", sample)

        if trigger.value == 1:
            print("Trigger Up!")
            self.print_xyz("Initial", self.initial_acceleration)
            self.print_xyz("Min", self.min_acceleration)
            self.print_xyz("Max", self.max_acceleration)

            diffMax = list(map(lambda x, y: x - y, self.initial_acceleration, self.max_acceleration))
            self.print_xyz("DiffMax", diffMax)

            return 'idle'
        return 'weaving'

    def measure(self):
        return [
            value / adafruit_lis3dh.STANDARD_GRAVITY for value in lis3dh.acceleration
        ]

    def print_xyz(self, name, measurement):
        x, y, z = measurement
        print("(%0.3f,%0.3f,%0.3f) %s" % (x, y, z, name))

state_machine.add_state(Weaving())

state_machine.go_to_state('idle')

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
    # x, y, z = [
    #     value / adafruit_lis3dh.STANDARD_GRAVITY for value in lis3dh.acceleration
    # ]

    # print("(%0.3f,%0.3f,%0.3f)" % (x, y, z))

    # x = pointing up or down. Up = -1, Down = 1
    # z, y = rotation. Flat = abs(z)=1, y=0. On edge = abs(z)=0,abs(y)=1

    state_machine.update()

    time.sleep(0.1)