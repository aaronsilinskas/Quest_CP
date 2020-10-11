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
    weaving_state = None
    active_spell_states = []

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
        if (not gs.trigger_down) and (len(gs.active_spell_states) > 0):
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
        spell = gs.active_spell_states.pop(0)

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
        gs.weaving_state = SpellState(spell)

    def update(self, ellapsed_time):
        self.ellapsed_total += ellapsed_time

        spell = select_spell(gs.initial_acceleration, gs.current_acceleration)
        if spell.name == gs.weaving_state.name:
            gs.weaving_state.power = min(self.ellapsed_total / 4, 1.0)
        else:
            loss = ellapsed_time / 2  # fade over 2 seconds
            gs.weaving_state.power = max(gs.weaving_state.power - loss, 0)
            if gs.weaving_state.power == 0:
                gs.weaving_state = SpellState(spell)
                self.ellapsed_total = 0

        print("Weave power ", gs.weaving_state.power)

        # print_xyz("Current acceleration", gs.current_acceleration)

        self.min_acceleration = list(map(min, gs.current_acceleration, self.min_acceleration))
        self.max_acceleration = list(map(max, gs.current_acceleration, self.max_acceleration))
        # print_xyz("Min", self.min_acceleration)
        # print_xyz("Max", self.max_acceleration)

        if not gs.trigger_down:
            gs.active_spell_states.insert(0, gs.weaving_state)
            gs.weaving_state = None

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

def draw_spell(spell_state, pixels, ellapsed_time):
    # print("Power: ", spell_state.power)
    spell_state.spell.draw(pixels, spell_state, ellapsed_time)

while True:
    current_time = time.monotonic()
    ellapsed_time = current_time - last_update_time
    last_update_time = time.monotonic()

    gs.trigger_down = is_trigger_down()
    gs.current_acceleration = measure_acceleration()

    state_machine.update(ellapsed_time)

    for spell in gs.active_spell_states:
        spell.lifespan = max(spell.lifespan - ellapsed_time, 0)
        if spell.lifespan <= 1:
            spell.power = max(spell.max_power * spell.lifespan, 0)

    gs.active_spell_states = [spell for spell in gs.active_spell_states if spell.lifespan > 0]

    if gs.weaving_state:
        draw_spell(gs.weaving_state, pixels, ellapsed_time)
    elif len(gs.active_spell_states) > 0:
        draw_spell(gs.active_spell_states[0], pixels, ellapsed_time)
    else:
        pixels.fill((0, 0, 0))
        pixels.show()

    if ellapsed_time < 0.05:
        time.sleep(0.05 - ellapsed_time)