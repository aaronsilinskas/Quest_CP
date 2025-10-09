# SPDX-FileCopyrightText: Copyright (c) 2024 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT
"""
`state_of_things.state_of_things`
================================================================================

Base classes used to implement complex state machines. Each `Thing`
starts in an initial `State`, and then updates to the thing's state
execute logic and determine whether or not to change to another state.

See examples directory for ideas on usage.

* Author(s): Aaron Silinskas

"""

import time
from .observers import Observers


class State:
    """
    Represents a state that a `Thing` can enter and exit. The state can
    transition a `Thing` into another state when it is updated.
    """

    @property
    def name(self):
        """The state's name, defaulting to the class name."""
        return type(self).__name__

    def enter(self, thing: "Thing"):
        """
        Called when a `Thing` enters this state. Typically used for
        one-time setup where state-specific context is added to the
        Thing.

        Args:
            thing (Thing): the `Thing` that entered this state.
        """
        pass

    def exit(self, thing: "Thing"):
        """
        Called when a `Thing` exists this state. Typically used to clean
        up resources initialized when the state is entered.

        Args:
            thing (Thing): the `Thing` that exited this state.
        """
        pass

    def update(self, thing: "Thing") -> "State":
        """
        Called periodically while a `Thing` is in this state. This
        function determines whether the `Thing` should remain in this
        state or change to another state.

        Often :attr:`Thing.time_elapsed` and :attr:`Thing.time_active`
        are referenced when a `Thing` should transition to another state
        after a given amount of time.

        Args:
            thing (Thing): the `Thing` to update in this state.

        Returns:
            State: the next state for the Thing, or this state if the
            `Thing` should remain unchanged.
        """
        return self


class ThingObserver:
    """
    Implement the :attr:`state_changed` function of this class to receive
    notifications when a `Thing` changes state. All `Thing` observers
    should inherited from this class.

    Logging state changes to stdout is common for debugging purposes.
    """

    def state_changed(self, thing: "Thing", old_state: State, new_state: State):
        """
        Notified when a `Thing` changes from one `State` to another.

        Args:
            thing (Thing): the `Thing` that changed state.
            old_state (State): the `State` that the `Thing` exited.
            new_state (State): the `State` that the `Thing` entered.
        """
        pass


class Thing:
    """
    Represents an object that can only be in one `State` at a time. It
    holds all global and state-specific context needed by `State`
    implementations to update and transition between states.
    """

    def __init__(self, initial_state: State, name: str = None):
        """
        Constructor that stores the initial `State` but does not change
        to it until :attr:`update` is called.

        Args:
            initial_state (State): the initial `State` for this thing
            name (str, optional): the name of this thing, usually for
            logging. Defaults to the class name.
        """
        assert initial_state, "initial_state is required"
        self.__initial_state = initial_state
        self.__name = name if name is not None else type(self).__name__

        self.__observers = Observers()

        self.__current_state: State = None
        self.__previous_state: State = None
        self.__time_last_update: float = 0
        self.__time_elapsed: float = 0
        self.__time_active: float = 0

    def __go_to_state(self, new_state: State):
        """
        Change this thing to a new `State`. Notifies all observers of the
        state change if moving from a previous `State`.

        Args:
            new_state (State): the target `State` for this thing.
        """
        assert new_state, "new_state can not be None"

        # if changing from a previous State, exit it
        if self.__current_state:
            self.__current_state.exit(self)

        # update the thing's state
        self.__previous_state = self.__current_state
        self.__current_state = new_state

        # only notify for change from initial state
        if self.__previous_state:
            self.observers.notify(
                "state_changed", self, self.__previous_state, self.__current_state
            )

        # reset time tracking properties
        self.__time_last_update = time.monotonic()
        self.__time_elapsed = 0
        self.__time_active = 0

        # enter the new State
        self.__current_state.enter(self)

    def update(self):
        """
        Updates :attr:`time_elapsed` and :attr:`time_active` of this
        thing, and then updates the `State` by calling
        :attr:`State.update` of :attr:`current_state`. If
        :attr:`State.update` returns a different `State` than the
        current one, then this thing will transition to the returned
        `State`.
        """
        # if the Thing is not in it's initial State, change to it
        if self.__current_state is None:
            self.__go_to_state(self.__initial_state)

        # update time tracking properties
        now = time.monotonic()
        self.__time_elapsed = now - self.__time_last_update
        self.__time_last_update = now
        self.__time_active += self.__time_elapsed

        # update the current State
        next_state = self.__current_state.update(self)
        if next_state != self.__current_state:
            self.__go_to_state(next_state)

    @property
    def name(self) -> str:
        """
        Name of this thing, defaulting to class name but can be
        manually set via the constructor.

        Returns:
            str: the name of this thing.
        """
        return self.__name

    @property
    def current_state(self) -> State:
        """
        The current `State` of this thing.

        Returns:
            State: the current `State`, or None if it does not have one.
        """
        return self.__current_state

    @property
    def previous_state(self) -> State:
        """
        The previous `State` of this thing.

        Returns:
            State: the previous `State`, or None if it has not changed
            States.
        """
        return self.__previous_state

    @property
    def time_elapsed(self) -> float:
        """
        The amount of time that has elapsed since this thing's last
        update call.

        Returns:
            float: the amount of elapsed time, in seconds.
        """
        return self.__time_elapsed

    @property
    def time_active(self) -> float:
        """
        The total amount of time that this thing has been in the current
        `State`.

        Returns:
            float: the amount of time active in the current `State`, in
            seconds.
        """
        return self.__time_active

    @property
    def observers(self) -> Observers:
        """
        The observers that will be notified by this `Thing`. For instance,
        all observers that implement `ThingObserver` will be notified when
        this `Thing` changes `State`.

        Things can have custom observers that it's `State` implementations
        can notify as needed. For instance, a button `Thing` may have an
        observer that is notified when the button is pressed or
        released.

        Returns:
            Observers: this `Thing`'s observers.
        """
        return self.__observers
