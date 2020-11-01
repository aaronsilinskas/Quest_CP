# State Machine
class State(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return type(self).__name__

    def enter(self):
        print("STATE -> {}".format(self.name))

    def exit(self):
        print("STATE <- {}".format(self.name))

    def update(self, ellapsed):
        return self.name


class StateMachine(object):
    def __init__(self):
        self.state = None
        self.states = {}

    def add_state(self, state):
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            self.state.exit()
        self.state = self.states[state_name]
        self.state.enter()

    def update(self, ellapsed_time):
        if self.state:
            next_state = self.state.update(ellapsed_time)
            if next_state != self.state.name:
                self.go_to_state(next_state)
