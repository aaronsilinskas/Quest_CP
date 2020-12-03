import board
import time
from hardware import Hardware
from sound import Sound
from state import State, StateMachine
from spell import select_spell, SpellState, age_spells
from lights import draw_casting, draw_spell, draw_weaved, PixelEdge
from infrared import Infrared


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

hw = Hardware(board.A2, ir_pin=board.D1)
hw.setup_pixels_dotstar(board.A3, board.A1, 14, 0.2)

left_edge = PixelEdge(hw.pixels, range(0, 7))
right_edge = PixelEdge(hw.pixels, range(13, 7, -1))

sound = Sound(hw.audio)
sound.volume(0.5)

infrared = Infrared(hw.ir_pulseout)

# == Global Functions ==
def play_cast():
    sound.play_file("hit.wav")


def play_weaved():
    sound.play_file("on.wav")


def play_active():
    sound.play_file("idle.wav", loop=True)


def print_xyz(name, measurement):
    x, y, z = measurement
    print("(%0.3f,%0.3f,%0.3f) %s" % (x, y, z, name))


def diff_iterable(it1, it2):
    return list(map(lambda v1, v2: v1 - v2, it1, it2))


# == States ==
class GlobalState:
    initial_acceleration = [None, None, None]
    active_spell_states = []
    casting_spell = None
    casting_progress = 0
    weaved_spell = None
    weaved_progress = 0


gs = GlobalState()

state_machine = StateMachine()


class Idle(State):
    def update(self, ellapsed_time):
        if hw.trigger_down:
            return "Triggered"
        return self.name


state_machine.add_state(Idle())


class Triggered(State):
    def enter(self):
        State.enter(self)
        self.time_remaining = 0.5

        gs.initial_acceleration = hw.current_acceleration

    def update(self, ellapsed_time):
        if (not hw.trigger_down) and (len(gs.active_spell_states) > 0):
            return "Casting"

        self.time_remaining -= ellapsed_time
        if self.time_remaining <= 0:
            if not hw.trigger_down:
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
            map(min, hw.current_acceleration, self.min_acceleration)
        )
        self.max_acceleration = list(
            map(max, hw.current_acceleration, self.max_acceleration)
        )
        # print_xyz("Min", self.min_acceleration)
        # print_xyz("Max", self.max_acceleration)

        if not hw.trigger_down:
            print("Trigger Up!")
            print_xyz("Initial", gs.initial_acceleration)
            print_xyz("Min", self.min_acceleration)
            print_xyz("Max", self.max_acceleration)

            diffMax = diff_iterable(gs.initial_acceleration, self.max_acceleration)
            print_xyz("DiffMax", diffMax)

            spell = select_spell(gs.initial_acceleration, hw.current_acceleration)
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
        play_weaved()
        print(
            "Weaved: {} at power {}".format(gs.weaved_spell.name, gs.weaved_spell.power)
        )

    def update(self, ellapsed_time):
        self.ellapsed_total += ellapsed_time
        gs.weaved_progress = min(self.ellapsed_total / 1, 1)
        if gs.weaved_progress == 1:
            gs.weaved_spell = None
            play_active()
            return "Idle"
        return self.name


state_machine.add_state(Weaved())


state_machine.go_to_state("Idle")

while True:
    hw.update()

    ellapsed_time = hw.ellapsed_time

    state_machine.update(ellapsed_time)

    spell_was_active = len(gs.active_spell_states)
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
        if spell_was_active:
            sound.off()
        hw.pixels.fill((0, 0, 0))

    hw.pixels.show()

    if hw.button_a_down:
        infrared.send([0b11111111, 0b01010101, 0b11001100, 0b00000000])
        time.sleep(0.5)

    sound.cleanup()
