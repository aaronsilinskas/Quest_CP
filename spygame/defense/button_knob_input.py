from event_listeners import EventListeners

class ButtonKnobInput:
    # Simulates a knob turned by a left and right button.
    # Adjust max_speed, acceleration, and deceleration to desired feel
    def __init__(self, left, right, max_speed: float, acceleration: float, deceleration: float) -> None:
        self._left = left
        self._right = right
        self._max_speed: float = max_speed
        self._acceleration: float = acceleration
        self._deceleration: float = deceleration

        self._on_move = EventListeners()

        self._speed = 0.0
        self._value: float = 0.0

    @property
    def on_move(self) -> EventListeners:
        return self._on_move

    def update(self, ellapsed_time: float) -> None:
        left_down = self._left()
        right_down = self._right()
        if left_down and not right_down:
            self._speed -= self._acceleration * ellapsed_time
            self._speed = max(self._speed, -self._max_speed)
        elif right_down and not left_down:
            self._speed += self._acceleration * ellapsed_time
            self._speed = min(self._speed, self._max_speed)
        elif self._speed > 0:
            self._speed -= self._deceleration * ellapsed_time
            self._speed = max(self._speed, 0)
        elif self._speed < 0:
            self._speed += self._deceleration * ellapsed_time
            self._speed = min(self._speed, 0)

        last_value = self._value
        self._value = self._value + self._speed * ellapsed_time
        while self._value < 0:
            self._value += 1
        while self._value > 1:
            self._value -= 1
        if self._value != last_value:
            self._on_move.notify((last_value, self._value))
