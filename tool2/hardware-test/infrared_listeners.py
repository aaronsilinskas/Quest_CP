from event_listeners import EventListeners
from infrared import Infrared


class InfraredListeners(object):
    def __init__(self, infrared: Infrared):
        super().__init__()
        self._infrared = infrared
        self._on_receive = EventListeners()

    @property
    def on_receive(self) -> EventListeners:
        return self._on_receive

    def update(self) -> None:
        received = self._infrared.receive()
        if received is not None:
            data, strength = received
            self._on_receive.notify((data, strength))
