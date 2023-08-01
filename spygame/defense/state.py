
import time


class State:
    @property
    def name(self):
        return type(self).__name__

    def enter(self, thing: Thing):
        pass

    def exit(self, thing: Thing):
        pass

    def update(self, thing: Thing) -> State:
        return self.name


class Thing:
    def __init__(self, logging=False):
        self.logging = logging

        self.state: State = None
        self.previous_state: State = None
        self.time_last_update: float = 0
        self.time_ellapsed: float = 0
        self.time_active: float = 0

    def __log(self, message):
        if self.logging:
            print(message)

    def go_to_state(self, state: State):
        if self.state == state:
            return
        
        if self.state:
            self.__log(f"{self.__class__.__name__} STATE <- {self.state.name}")
            self.state.exit(self)
            self.previous_state = self.state

        self.state = state
        self.__log(f"{self.__class__.__name__} STATE -> {self.state.name}")

        self.time_last_update = time.monotonic()
        self.time_ellapsed = 0
        self.time_active = 0
        self.state.enter(self)

    def update(self):
        if self.state:
            now = time.monotonic()
            self.time_ellapsed = now - self.time_last_update
            self.time_last_update = now
            self.time_active += self.time_ellapsed

            next_state = self.state.update(self)
            if next_state != self.state:
                self.go_to_state(next_state)
