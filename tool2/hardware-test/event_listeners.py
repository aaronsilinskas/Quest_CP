try:
    from typing import Callable, TypeAlias

    Callback: TypeAlias = Callable[[], None]
except ImportError:
    pass


class EventListeners(object):
    def __init__(self) -> None:
        self._listeners = []

    def add(self, callback: Callback[[tuple], None]) -> None:
        self._listeners.append(callback)

    def notify(self, event: tuple = ()) -> None:
        for listener in self._listeners:
            if event:
                listener(event)
            else:
                listener()
