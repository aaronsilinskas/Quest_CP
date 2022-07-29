
import time

class StateContext(object):
    def __init__(self):
        self.state:State = None
        self.time_last_update:float = 0
        self.time_ellapsed:float = 0
        self.time_active:float = 0
    
class State(object):
    @property
    def name(self):
        return type(self).__name__

    def enter(self, context: StateContext):
        pass

    def exit(self, context: StateContext):
        pass

    def update(self, context: StateContext):
        return self.name


class StateMachine(object):

    def __init__(self, disable_logging = False):
        self.disable_logging = disable_logging
    
    def __log(self, message):
        if not self.disable_logging:
            print(message)

    def go_to_state(self, state:State, context: StateContext):
        if context.state:
            self.__log("STATE <- {}".format(context.state.name))
            context.state.exit(context)

        context.state = state
        self.__log("STATE -> {}".format(context.state.name))

        context.time_last_update = time.monotonic()
        context.time_ellapsed = 0
        context.time_active = 0
        context.state.enter(context)

    def update(self, context: StateContext):
        if context.state:
            now = time.monotonic() 
            context.time_ellapsed = now - context.time_last_update
            context.time_last_update = now
            context.time_active += context.time_ellapsed
            
            next_state = context.state.update(context)
            if next_state != context.state:
                self.go_to_state(next_state, context)
