import time

from hardware import measure_acceleration, is_trigger_down, pixels
from state import State, StateMachine
from spell import select_spell, SpellState, age_spells
from sound import play_cast
from lights import draw_casting, draw_spell, draw_weaved, PixelEdge

# Spell States
# States
# Idle (waiting for user input, can do random funny things)
# - if trigger down -> Triggered
# Triggered (trigger is down, determine cast or weave)
# - if trigger up
#   - if < 500ms && active spell -> Casting
#   - else -> Idle
# - if ellapsed time > 500ms -> Weaving
# Casting (the active spell has been cast)
# - if done casting -> Idle
# Weaving (motion will select a spell)
# - if trigger up
#   - if spell selected -> Weaved
#   - else -> Idle
# Weaved (a spell was weaved, activate it)
# - if done activating -> Idle

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
    active_spell_states = []
    casting_spell = None
    casting_progress = 0
    weaved_spell = None
    weaved_progress = 0


gs = GlobalState()

state_machine = StateMachine()


class Idle(State):
    def update(self, ellapsed_time):
        if gs.trigger_down:
            return "Triggered"
        return self.name


state_machine.add_state(Idle())


class Triggered(State):
    def enter(self):
        State.enter(self)
        self.time_remaining = 0.5

        gs.initial_acceleration = measure_acceleration()

    def update(self, ellapsed_time):
        if (not gs.trigger_down) and (len(gs.active_spell_states) > 0):
            return "Casting"

        self.time_remaining -= ellapsed_time
        if self.time_remaining <= 0:
            if not gs.trigger_down:
                return "Idle"
            else:
                return "Weaving"
        return self.name


state_machine.add_state(Triggered())


class Casting(State):
    def enter(self):
        State.enter(self)
        self.ellapsed_total = 0
        gs.casting_spell = gs.active_spell_states.pop(0)
        gs.casting_progress = 0

        print(
            "Casting: {} at power {}".format(
                gs.casting_spell.name, gs.casting_spell.power
            )
        )

        play_cast()

    def update(self, ellapsed_time):
        self.ellapsed_total += ellapsed_time
        gs.casting_progress = min(self.ellapsed_total / 0.25, 1)
        if gs.casting_progress == 1:
            gs.casting_spell = None
            return "Idle"
        return self.name


state_machine.add_state(Casting())


class Weaving(State):
    def enter(self):
        State.enter(self)

        print_xyz("Weaving Enter Initial", gs.initial_acceleration)
        self.ellapsed_total = 0
        self.min_acceleration = gs.initial_acceleration.copy()
        self.max_acceleration = gs.initial_acceleration.copy()

    def update(self, ellapsed_time):
        self.ellapsed_total += ellapsed_time

        # print_xyz("Current acceleration", gs.current_acceleration)

        self.min_acceleration = list(
            map(min, gs.current_acceleration, self.min_acceleration)
        )
        self.max_acceleration = list(
            map(max, gs.current_acceleration, self.max_acceleration)
        )
        # print_xyz("Min", self.min_acceleration)
        # print_xyz("Max", self.max_acceleration)

        if not gs.trigger_down:
            print("Trigger Up!")
            print_xyz("Initial", gs.initial_acceleration)
            print_xyz("Min", self.min_acceleration)
            print_xyz("Max", self.max_acceleration)

            diffMax = diff_xyz(gs.initial_acceleration, self.max_acceleration)
            print_xyz("DiffMax", diffMax)

            spell = select_spell(gs.initial_acceleration, gs.current_acceleration)
            if spell is None:
                return "Idle"

            spell_state = SpellState(spell, 1)
            gs.active_spell_states.insert(0, spell_state)
            return "Weaved"
        return self.name


state_machine.add_state(Weaving())


class Weaved(State):
    def enter(self):
        State.enter(self)
        self.ellapsed_total = 0
        gs.weaved_spell = gs.active_spell_states[0]
        gs.weaved_progress = 0

        print(
            "Weaved: {} at power {}".format(gs.weaved_spell.name, gs.weaved_spell.power)
        )

    def update(self, ellapsed_time):
        self.ellapsed_total += ellapsed_time
        gs.weaved_progress = min(self.ellapsed_total / 0.5, 1)
        if gs.weaved_progress == 1:
            gs.weaved_spell = None
            return "Idle"
        return self.name


state_machine.add_state(Weaved())


state_machine.go_to_state("Idle")
last_update_time = time.monotonic()


def read_hardware():
    gs.trigger_down = is_trigger_down()
    gs.current_acceleration = measure_acceleration()

left_edge = PixelEdge(pixels, range(0, 7))
right_edge = PixelEdge(pixels, range(13, 7, -1))

while True:
    current_time = time.monotonic()
    ellapsed_time = current_time - last_update_time
    last_update_time = time.monotonic()

    read_hardware()

    state_machine.update(ellapsed_time)

    gs.active_spell_states = age_spells(gs.active_spell_states, ellapsed_time)

    if gs.casting_spell:
        draw_casting(gs.casting_spell, left_edge, ellapsed_time, gs.casting_progress)
        draw_casting(gs.casting_spell, right_edge, ellapsed_time, gs.casting_progress)
    elif gs.weaved_spell:
        draw_weaved(gs.weaved_spell, left_edge, ellapsed_time, gs.weaved_progress)
        draw_weaved(gs.weaved_spell, right_edge, ellapsed_time, gs.weaved_progress)
    elif len(gs.active_spell_states) > 0:
        active_spell = gs.active_spell_states[0]
        draw_spell(active_spell, left_edge, ellapsed_time)
        draw_spell(active_spell, right_edge, ellapsed_time)
    else:
        pixels.fill((0, 0, 0))

    pixels.show()

    if ellapsed_time < 0.05:
        time.sleep(0.05 - ellapsed_time)
