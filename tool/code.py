import time
import board
from digitalio import DigitalInOut, Direction, Pull
import busio
import adafruit_lis3dh
import adafruit_dotstar
from state import State, StateMachine
from spell import select_spell

# == Todo ==
# charge up
# select spell by initial and current
# charge down if spell doesn't match

# == Hardware ==
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

# LEDs
pixels = adafruit_dotstar.DotStar(board.A2, board.A1, 14, brightness=0.05,
                                  auto_write=False)

# Trigger
trigger = DigitalInOut(board.A3)
trigger.direction = Direction.INPUT
trigger.pull = Pull.UP

# == Global Functions ==
def measure():
    return [
        value / adafruit_lis3dh.STANDARD_GRAVITY for value
        in lis3dh.acceleration
    ]

def print_xyz(name, measurement):
    x, y, z = measurement
    print("(%0.3f,%0.3f,%0.3f) %s" % (x, y, z, name))

def diff_xyz(initial, current):
    return list(map(lambda x, y: x - y, initial, current))

# == States ==
class GlobalState:
    initial_acceleration = [None, None, None]
    weave_spell = None
    weave_progress = 0

gs = GlobalState()

state_machine = StateMachine()

class Idle(State):

    @property
    def name(self):
        return 'idle'

    def enter(self):
        State.enter(self)

    def update(self, ellapsed_time):
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

        gs.initial_acceleration = measure()

    def update(self, ellapsed_time):
        if (trigger.value == 1) and (gs.weave_spell):
            return 'casting'

        self.time_remaining -= ellapsed_time
        if self.time_remaining <= 0:
            if trigger.value == 1:
                return 'idle'
            else:
                return 'weaving'
        return self.name

state_machine.add_state(Triggered())

class Casting(State):
    @property
    def name(self):
        return 'casting'

    def enter(self):
        State.enter(self)

    def update(self, ellapsed_time):
        print("Casting: {}".format(gs.weave_spell.name))

        gs.weave_spell = None
        gs.weave_progress = 0
        return 'idle'

state_machine.add_state(Casting())

class Weaving(State):

    def __init__(self):
        self.ellapsed_total = 0
        self.min_acceleration = [None, None, None]
        self.max_acceleration = [None, None, None]

    @property
    def name(self):
        return 'weaving'

    def enter(self):
        State.enter(self)

        print_xyz("Weaving Enter Initial", gs.initial_acceleration)
        self.ellapsed_total = 0
        self.min_acceleration = gs.initial_acceleration.copy()
        self.max_acceleration = gs.initial_acceleration.copy()

        gs.weave_spell = select_spell(gs.initial_acceleration)

    def update(self, ellapsed_time):
        sample = measure()
        print_xyz("Sample", sample)

        self.min_acceleration = list(map(min, sample, self.min_acceleration))
        self.max_acceleration = list(map(max, sample, self.max_acceleration))
        # print_xyz("Min", self.min_acceleration)
        # print_xyz("Max", self.max_acceleration)

        self.ellapsed_total += ellapsed_time
        gs.weave_progress = min(self.ellapsed_total / 4, 1.0)
        print("Weave progress ", gs.weave_progress)

        if trigger.value == 1:
            print("Trigger Up!")
            print_xyz("Initial", gs.initial_acceleration)
            print_xyz("Min", self.min_acceleration)
            print_xyz("Max", self.max_acceleration)

            diffMax = diff_xyz(gs.initial_acceleration, self.max_acceleration)
            print_xyz("DiffMax", diffMax)

            return 'idle'
        return 'weaving'


state_machine.add_state(Weaving())

state_machine.go_to_state('idle')

last_update_time = time.monotonic()

while True:
    current_time = time.monotonic()
    ellapsed_time = current_time - last_update_time
    last_update_time = time.monotonic()

    # x = pointing up or down. Up = -1, Down = 1
    # z, y = rotation. Flat = abs(z)=1, y=0. On edge = abs(z)=0,abs(y)=1

    state_machine.update(ellapsed_time)

    if (gs.weave_spell):
        color = int(255 * gs.weave_progress)
        pixels.fill((color, color, color))
        pixels.show()
    else:
        pixels.fill((0, 0, 0))
        pixels.show()

    if ellapsed_time < 0.05:
        time.sleep(0.05 - ellapsed_time)