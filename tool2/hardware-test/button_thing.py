from state_of_things import Thing, State, ThingObserver

try:
    from typing import Callable, TypeAlias

    Callback: TypeAlias = Callable[[], None]
except ImportError:
    pass

class ButtonObserver(ThingObserver):
    def on_press(self, button:Thing):
        pass
    
    def on_release(self, button:Thing):
        pass


class ButtonThing(Thing):
    def __init__(self, predicate: Callback[[], bool], name: str = None):
        super().__init__(ButtonStates.released, name=name)

        self._predicate = predicate

    @property
    def value(self) -> bool:
        return self._predicate()


class ButtonStates:
    released: State
    pressed: State


class ReleasedState(State):
    def enter(self, thing: ButtonThing):
        thing.observers.notify("on_release", thing)

    def update(self, thing: ButtonThing) -> State:
        if thing.value:
            return ButtonStates.pressed

        return ButtonStates.released


ButtonStates.released = ReleasedState()


class PressedState(State):
    def enter(self, thing: ButtonThing):
        thing.observers.notify("on_press", thing)

    def update(self, thing: ButtonThing) -> State:
        if not thing.value:
            return ButtonStates.released

        return ButtonStates.pressed


ButtonStates.pressed = PressedState()
