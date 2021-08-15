class State(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return type(self).__name__

    def enter(self, context):
        print("STATE -> {}".format(self.name))

    def exit(self, context):
        print("STATE <- {}".format(self.name))

    def update(self, ellapsed, context):
        return self.name


class StateMachine(object):
    def __init__(self):
        self.states = {}

    def add_state(self, state):
        self.states[state.name] = state

    def go_to_state(self, state_name, context):
        if context.state:
            context.state.exit(context)
        context.state = self.states[state_name]
        context.state.enter(context)

    def update(self, context, ellapsed_time):
        if context.state:
            next_state = context.state.update(ellapsed_time, context)
            if next_state != context.state.name:
                self.go_to_state(next_state, context)
