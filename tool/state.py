import time

# State Machine
class State(object):

    def __init__(self):
        pass

    @property
    def name(self):
        return ''

    def enter(self):
        print("Entering state: {}".format(self.name))

    def exit(self):
        print("Exiting state: {}".format(self.name))

    def update(self, ellapsed):
        return self.name

class StateMachine(object):

    def __init__(self):
        self.state = None
        self.states = {}
        self.last_update = None

    def add_state(self, state):
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            self.state.exit()
        self.state = self.states[state_name]
        self.state.enter()
        self.last_update = time.monotonic()

    def update(self):
        if self.state:
            current_time = time.monotonic()
            next_state = self.state.update(current_time - self.last_update)
            self.last_update = current_time
            if next_state != self.state.name:
                self.go_to_state(next_state)