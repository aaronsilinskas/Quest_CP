# SPDX-FileCopyrightText: Copyright (c) 2024 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT
"""
`state_of_things.observers`
================================================================================

Maintain and notify a list of observers (see
https://en.wikipedia.org/wiki/Observer_pattern).

Define a class that has all observable events, which will serve as a
contract to let users easily see what events can occur and what data
will be available.

Below is an example observer contract for key press and release:

.. code-block:: python

    class KeyObserver:
        def on_press(self, key_code: str):
            pass

        def on_release(self, key_code: str, seconds_pressed: float):
            pass


Observer implementations would then subclass the observer:

.. code-block:: python

    class LoggingObserver(KeyObserver):
        def on_press(self, key_code: str):
            print(f"Key pressed: {key_code}")

        def on_release(self, key_code: str, seconds_pressed: float):
            print(f"Key released: {key_code} after {seconds_pressed} seconds")

Observers are maintained and notified via an `Observers` instance:

.. code-block:: python

    observers = Observers()
    observers.attach(LoggingObserver())

    # trigger an on_press event for the 'w' key
    observers.notify("on_press", "w")

    # trigger an on_release event for the 'w' key that was held for 1.2
    # seconds
    observers.notify("on_release", "w", 1.2)

* Author(s): Aaron Silinskas

"""

try:
    from typing import List
except ImportError:  # pragma: no cover
    pass


class Observers:
    """
    Maintain a list of observers that will be notified when an event
    occurs.
    """

    def __init__(self) -> None:
        self.__observers: List = []

    def attach(self, observer: object):
        """
        Attach an observer that will be notified of events that it
        supports.

        Args:
            observer (object): the observer to attach.
        """
        self.__observers.append(observer)

    def detach(self, observer: object):
        """
        Detach an observer so that it will no longer be notified when
        events occur.

        Args:
            observer (object): the observer to detach.
        """
        self.__observers.remove(observer)

    def notify(self, event_name: str, *params: object):
        """
        Notify all observers that an event has occurred. Each attached
        observer with a defined function that matches the event name
        will called with the passed in event's params.

        Args:
            event_name (str): event that has occurred.
            *params (object): optional event data.
        """
        for observer in self.__observers:
            handler = getattr(observer, event_name, None)
            if callable(handler):
                handler(*params)
