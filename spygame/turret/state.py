
import time


class Thing:
    def __init__(self):
        self.state: State = None
        self.previous_state: State = None
        self.time_last_update: float = 0
        self.time_ellapsed: float = 0
        self.time_active: float = 0


class State:
    @property
    def name(self):
        return type(self).__name__

    def enter(self, thing: Thing):
        pass

    def exit(self, thing: Thing):
        pass

    def update(self, thing: Thing):
        return self.name


class ThingUpdater:

    def __init__(self, disable_logging=False):
        self.disable_logging = disable_logging

    def __log(self, message):
        if not self.disable_logging:
            print(message)

    def go_to_state(self, thing: Thing, state: State):
        if thing.state:
            self.__log(f"STATE <- {thing.state.name}")
            thing.state.exit(thing)
            thing.previous_state = thing.state

        thing.state = state
        self.__log(f"STATE -> {thing.state.name}")

        thing.time_last_update = time.monotonic()
        thing.time_ellapsed = 0
        thing.time_active = 0
        thing.state.enter(thing)

    def update(self, thing: Thing):
        if thing.state:
            now = time.monotonic()
            thing.time_ellapsed = now - thing.time_last_update
            thing.time_last_update = now
            thing.time_active += thing.time_ellapsed

            next_state = thing.state.update(thing)
            if next_state != thing.state:
                self.go_to_state(thing, next_state)
