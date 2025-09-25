from spell.spell import Spell, match_position
from state_of_things import State, Thing, ThingObserver


class WeavingStates:
    waiting: State
    cast_or_weave: State
    cast_spell: State
    select_spell: State
    spell_selected: State
    select_shape: State
    shape_selected: State
    select_purpose: State
    spell_ready: State


class WeavingThing(Thing):

    def __init__(self, name=None, starting_level: int = 1):
        super().__init__(WeavingStates.waiting, name)
        self._trigger_pressed: bool = False
        self._start_position: int = 0
        self._current_position: int = 0
        self._spell: Spell = Spell()
        self._level: int = starting_level

    def reset(self):
        self._spell = Spell()

    @property
    def trigger_pressed(self) -> bool:
        return self._trigger_pressed

    @trigger_pressed.setter
    def trigger_pressed(self, value: bool):
        self._trigger_pressed = value

    @property
    def start_position(self) -> int:
        return self._start_position

    @start_position.setter
    def start_position(self, value: int):
        self._start_position = value

    @property
    def current_position(self) -> int:
        return self._current_position

    @current_position.setter
    def current_position(self, value: int):
        self._current_position = value

    @property
    def spell(self) -> Spell:
        return self._spell

    @property
    def level(self) -> int:
        return self._level


class WeavingObserver(ThingObserver):
    def spell_selected(self, thing: WeavingThing, spell: Spell):
        pass

    def shape_selected(self, thing: WeavingThing, spell: Spell):
        pass

    def spell_ready(self, thing: WeavingThing, spell: Spell):
        pass

    def spell_cast(self, thing: WeavingThing, spell: Spell):
        pass


class WaitingState(State):
    def update(self, thing: WeavingThing):
        if thing.trigger_pressed:
            return WeavingStates.cast_or_weave

        return self


WeavingStates.waiting = WaitingState()


class CastOrWeaveState(State):
    def enter(self, thing: WeavingThing):
        thing.start_position = thing.current_position

    def update(self, thing: WeavingThing):
        if not thing.trigger_pressed:
            if thing.time_active < 0.25:
                return WeavingStates.cast_spell

            return WeavingStates.select_spell

        return self


WeavingStates.cast_or_weave = CastOrWeaveState()


class CastSpellState(State):
    def update(self, thing: WeavingThing):
        thing.observers.notify("spell_cast", thing, thing.spell)
        return WeavingStates.waiting


WeavingStates.cast_spell = CastSpellState()


class SelectSpellState(State):
    def update(self, thing: WeavingThing):
        thing.reset()

        thing.spell.element = match_position(
            thing.start_position, thing.current_position
        ).element
        return WeavingStates.spell_selected


WeavingStates.select_spell = SelectSpellState()


class SpellSelectedState(State):
    def enter(self, thing: WeavingThing):
        thing.observers.notify("spell_selected", thing, thing.spell)

    def update(self, thing: WeavingThing):
        if thing.level == 1:
            return WeavingStates.spell_ready

        if thing.trigger_pressed:
            return WeavingStates.select_shape

        if thing.time_active > 2:
            return WeavingStates.spell_ready

        return self


WeavingStates.spell_selected = SpellSelectedState()


class SelectShapeState(State):
    def enter(self, thing: WeavingThing):
        thing.start_position = thing.current_position

    def update(self, thing: WeavingThing):
        if not thing.trigger_pressed:
            thing.spell.shape = match_position(
                thing.start_position, thing.current_position
            ).shape
            return WeavingStates.shape_selected

        return self


WeavingStates.select_shape = SelectShapeState()


class ShapeSelectedState(State):
    def enter(self, thing: WeavingThing):
        thing.observers.notify("shape_selected", thing, thing.spell)

    def update(self, thing: WeavingThing):
        if thing.level == 2:
            return WeavingStates.spell_ready

        if thing.trigger_pressed:
            return WeavingStates.select_purpose

        if thing.time_active > 2:
            return WeavingStates.spell_ready

        return self


WeavingStates.shape_selected = ShapeSelectedState()


class SelectPurposeState(State):
    def enter(self, thing: WeavingThing):
        thing.start_position = thing.current_position

    def update(self, thing: WeavingThing):
        if not thing.trigger_pressed:
            thing.spell.purpose = match_position(
                thing.start_position, thing.current_position
            ).purpose
            return WeavingStates.spell_ready

        return self


WeavingStates.select_purpose = SelectPurposeState()


class SpellReadyState(State):
    def update(self, thing: WeavingThing):
        thing.observers.notify("spell_ready", self, thing.spell)

        return WeavingStates.waiting


WeavingStates.spell_ready = SpellReadyState()
