import time

from hardware import measure_acceleration, is_trigger_down, pixels
from state import State, StateMachine
from spell import select_spell

# == Global Functions ==
def print_xyz(name, measurement):
    x, y, z = measurement
    print("(%0.3f,%0.3f,%0.3f) %s" % (x, y, z, name))

def diff_xyz(initial, current):
    return list(map(lambda x, y: x - y, initial, current))

# == States ==
class GlobalState:
    trigger_down = False
    initial_acceleration = [None, None, None]
    weave_spell = None
    weave_power = 0

gs = GlobalState()

state_machine = StateMachine()

class Idle(State):

    def update(self, ellapsed_time):
        if gs.trigger_down:
            return 'Triggered'
        return self.name

state_machine.add_state(Idle())

class Triggered(State):

    def enter(self):
        State.enter(self)
        self.time_remaining = 0.5

        gs.initial_acceleration = measure_acceleration()

    def update(self, ellapsed_time):
        if (not gs.trigger_down) and (gs.weave_spell):
            return 'Casting'

        self.time_remaining -= ellapsed_time
        if self.time_remaining <= 0:
            if not gs.trigger_down:
                return 'Idle'
            else:
                return 'Weaving'
        return self.name

state_machine.add_state(Triggered())

class Casting(State):

    def update(self, ellapsed_time):
        print("Casting: {}".format(gs.weave_spell.name))

        gs.weave_spell = None
        gs.weave_power = 0
        return 'Idle'

state_machine.add_state(Casting())

class Weaving(State):

    def enter(self):
        State.enter(self)

        print_xyz("Weaving Enter Initial", gs.initial_acceleration)
        self.ellapsed_total = 0
        self.min_acceleration = gs.initial_acceleration.copy()
        self.max_acceleration = gs.initial_acceleration.copy()

        gs.weave_spell = select_spell(gs.initial_acceleration)

    def update(self, ellapsed_time):
        sample = measure_acceleration()
        print_xyz("Sample", sample)

        self.min_acceleration = list(map(min, sample, self.min_acceleration))
        self.max_acceleration = list(map(max, sample, self.max_acceleration))
        # print_xyz("Min", self.min_acceleration)
        # print_xyz("Max", self.max_acceleration)

        self.ellapsed_total += ellapsed_time
        gs.weave_power = min(self.ellapsed_total / 4, 1.0)
        print("Weave power ", gs.weave_power)

        if not gs.trigger_down:
            print("Trigger Up!")
            print_xyz("Initial", gs.initial_acceleration)
            print_xyz("Min", self.min_acceleration)
            print_xyz("Max", self.max_acceleration)

            diffMax = diff_xyz(gs.initial_acceleration, self.max_acceleration)
            print_xyz("DiffMax", diffMax)

            return 'Weaved'
        return 'Weaving'


state_machine.add_state(Weaving())

class Weaved(State):

    def enter(self):
        State.enter(self)
        self.ellapsed_total = 0

    def update(self, ellapsed_time):
        self.ellapsed_total += ellapsed_time
        if (self.ellapsed_total > 5):
            gs.weave_power = max(0, 10.0 - self.ellapsed_total) / 5

        if (gs.weave_power == 0):
            gs.weave_spell = None
            return 'Idle'
        if gs.trigger_down:
            return 'Triggered'
        return 'Weaved'

state_machine.add_state(Weaved())

state_machine.go_to_state('Idle')

last_update_time = time.monotonic()

while True:
    current_time = time.monotonic()
    ellapsed_time = current_time - last_update_time
    last_update_time = time.monotonic()

    gs.trigger_down = is_trigger_down()

    # x = pointing up or down. Up = -1, Down = 1
    # z, y = rotation. Flat = abs(z)=1, y=0. On edge = abs(z)=0,abs(y)=1

    state_machine.update(ellapsed_time)

    if (gs.weave_spell):
        print("Power: ", gs.weave_power)
        color = int(255 * gs.weave_power)
        pixels.fill((color, color, color))
        pixels.show()
    else:
        pixels.fill((0, 0, 0))
        pixels.show()

    if ellapsed_time < 0.05:
        time.sleep(0.05 - ellapsed_time)