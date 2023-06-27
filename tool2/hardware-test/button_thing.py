from state import Thing, State
from event_listeners import EventListeners

try:
    from typing import Callable, TypeAlias

    Callback: TypeAlias = Callable[[], None]
except ImportError:
    pass


class ButtonThing(Thing):
    def __init__(self, predicate: Callback[[], bool], enable_logging=False):
        super().__init__(enable_logging)

        self._predicate = predicate
        self._on_press = EventListeners()
        self._on_release = EventListeners()

        self.go_to_state(ButtonStates.released)

    @property
    def value(self) -> bool:
        return self._predicate()

    @property
    def on_press(self) -> EventListeners:
        return self._on_press

    @property
    def on_release(self) -> EventListeners:
        return self._on_release


class ButtonStates:
    released: State
    pressed: State


class ReleasedState(State):
    def enter(self, thing: ButtonThing):
        thing.on_release.notify()

    def update(self, thing: ButtonThing) -> State:
        if thing.value:
            return ButtonStates.pressed

        return ButtonStates.released


ButtonStates.released = ReleasedState()


class PressedState(State):
    def enter(self, thing: ButtonThing):
        thing.on_press.notify()

    def update(self, thing: ButtonThing) -> State:
        if not thing.value:
            return ButtonStates.released

        return ButtonStates.pressed


ButtonStates.pressed = PressedState()
