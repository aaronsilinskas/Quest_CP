import time

from hardware import measure_acceleration, is_trigger_down, pixels
from state import State, StateMachine
from spell import select_spell, SpellState

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
    current_acceleration = [None, None, None]
    weaving_spell = None
    active_spells = []

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
        if (not gs.trigger_down) and (len(gs.active_spells) > 0):
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
        spell = gs.active_spells.pop(0)

        print("Casting: {} at power {}".format(spell.name, spell.power))

        return 'Idle'

state_machine.add_state(Casting())

class Weaving(State):

    def enter(self):
        State.enter(self)

        print_xyz("Weaving Enter Initial", gs.initial_acceleration)
        self.ellapsed_total = 0
        self.min_acceleration = gs.initial_acceleration.copy()
        self.max_acceleration = gs.initial_acceleration.copy()

        spell = select_spell(gs.initial_acceleration, gs.current_acceleration)
        gs.weaving_spell = SpellState(spell, 0, 10)

    def update(self, ellapsed_time):
        self.ellapsed_total += ellapsed_time

        # print_xyz("Current acceleration", gs.current_acceleration)

        self.min_acceleration = list(map(min, gs.current_acceleration, self.min_acceleration))
        self.max_acceleration = list(map(max, gs.current_acceleration, self.max_acceleration))
        # print_xyz("Min", self.min_acceleration)
        # print_xyz("Max", self.max_acceleration)

        gs.weaving_spell.power = min(self.ellapsed_total / 4, 1.0)
        print("Weave power ", gs.weaving_spell.power)

        if not gs.trigger_down:
            gs.active_spells.insert(0, gs.weaving_spell)
            gs.weaving_spell = None

            print("Trigger Up!")
            print_xyz("Initial", gs.initial_acceleration)
            print_xyz("Min", self.min_acceleration)
            print_xyz("Max", self.max_acceleration)

            diffMax = diff_xyz(gs.initial_acceleration, self.max_acceleration)
            print_xyz("DiffMax", diffMax)

            return 'Idle'
        return 'Weaving'


state_machine.add_state(Weaving())

state_machine.go_to_state('Idle')

last_update_time = time.monotonic()

def draw_spell(spell_state, pixels):
    print("Power: ", spell_state.power)

    color = int(255 * spell_state.power)
    pixels.fill((color, color, color))
    pixels.show()

while True:
    current_time = time.monotonic()
    ellapsed_time = current_time - last_update_time
    last_update_time = time.monotonic()

    gs.trigger_down = is_trigger_down()
    gs.current_acceleration = measure_acceleration()

    # x = pointing up or down. Up = -1, Down = 1
    # z, y = rotation. Flat = abs(z)=1, y=0. On edge = abs(z)=0,abs(y)=1

    state_machine.update(ellapsed_time)

    for spell in gs.active_spells:
        spell.lifespan = max(spell.lifespan - ellapsed_time, 0)
        if spell.lifespan <= 1:
            spell.power = max(spell.max_power * spell.lifespan, 0)

    gs.active_spells = [spell for spell in gs.active_spells if spell.lifespan > 0]

    if gs.weaving_spell:
        draw_spell(gs.weaving_spell, pixels)
    elif len(gs.active_spells) > 0:
        draw_spell(gs.active_spells[0], pixels)
    else:
        pixels.fill((0, 0, 0))
        pixels.show()

    if ellapsed_time < 0.05:
        time.sleep(0.05 - ellapsed_time)