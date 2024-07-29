from state_of_things.observers import Observers
from infrared import Infrared

class InfraredObserver(object):
    def on_receive(self, data: bytearray, strength: float):
        pass

class InfraredObservers(object):
    def __init__(self, infrared: Infrared):
        super().__init__()
        self._infrared = infrared
        self._observers = Observers()

    @property
    def observers(self) -> Observers:
        return self._observers

    def update(self) -> None:
        received = self._infrared.receive()
        if received is not None:
            data, strength = received
            self._observers.notify("on_receive", data, strength)
