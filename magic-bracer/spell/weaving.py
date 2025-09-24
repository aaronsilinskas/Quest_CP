from micropython import const


class WeavingPosition:
    UP: int = const(1)
    DOWN: int = const(2)
    HORIZ_SIDE: int = const(3)
    HORIZ_UP: int = const(4)
    HORIZ_DOWN: int = const(5)

    @staticmethod
    def from_accelerometer(x: float, y: float, z: float) -> int:
        """Determine the orientation based on accelerometer data."""
        if y > 0.66:
            return WeavingPosition.DOWN
        if y < -0.66:
            return WeavingPosition.UP
        if z > 0.65:
            return WeavingPosition.HORIZ_UP
        if z < -0.65:
            return WeavingPosition.HORIZ_DOWN
        return WeavingPosition.HORIZ_SIDE

    @staticmethod
    def match(start: int, end: int, position_1: int, position_2: int) -> bool:
        return (start == position_1 and end == position_2) or (
            start == position_2 and end == position_1
        )


class WeavingElement:
    WATER: int = const(1)
    EARTH: int = const(2)
    FIRE: int = const(3)
    LIGHT: int = const(4)
    DARK: int = const(5)
    ICE: int = const(6)
    AIR: int = const(7)
    LIGHTNING: int = const(8)
    TIME: int = const(9)
    GRAVITY: int = const(10)

    @staticmethod
    def from_positions(start: int, end: int) -> int:
        if start == end:
            if end == WeavingPosition.UP:
                return WeavingElement.WATER
            elif end == WeavingPosition.DOWN:
                return WeavingElement.EARTH
            elif end == WeavingPosition.HORIZ_SIDE:
                return WeavingElement.FIRE
            elif end == WeavingPosition.HORIZ_UP:
                return WeavingElement.LIGHT
            elif end == WeavingPosition.HORIZ_DOWN:
                return WeavingElement.DARK
            else:
                return WeavingElement.FIRE

        if WeavingPosition.match(start, end, WeavingPosition.DOWN, WeavingPosition.UP):
            return WeavingElement.ICE
        elif WeavingPosition.match(
            start, end, WeavingPosition.HORIZ_SIDE, WeavingPosition.UP
        ):
            return WeavingElement.AIR
        elif WeavingPosition.match(
            start, end, WeavingPosition.HORIZ_SIDE, WeavingPosition.DOWN
        ):
            return WeavingElement.LIGHTNING
        elif WeavingPosition.match(
            start, end, WeavingPosition.HORIZ_SIDE, WeavingPosition.HORIZ_UP
        ):
            return WeavingElement.TIME
        elif WeavingPosition.match(
            start,
            end,
            WeavingPosition.HORIZ_SIDE,
            WeavingPosition.HORIZ_DOWN,
        ):
            return WeavingElement.GRAVITY

        return WeavingElement.FIRE


class WeavingShape:
    AREA_OF_EFFECT: int = const(1)
    OVER_SHORT_TIME: int = const(2)
    IMMEDIATE: int = const(3)
    OVER_LONG_TIME: int = const(4)
    REPEAT: int = const(5)
    BLOCK_OVER_SHORT_TIME = const(6)
    AREA_OF_EFFECT_ON_TARGET = const(7)
    CHAIN = const(8)
    DELAYED = const(9)
    DELAYED_AREA_OF_EFFECT = const(10)

    @staticmethod
    def from_positions(start: int, end: int) -> int:
        if start == end:
            if end == WeavingPosition.UP:
                return WeavingShape.AREA_OF_EFFECT
            elif end == WeavingPosition.DOWN:
                return WeavingShape.OVER_SHORT_TIME
            elif end == WeavingPosition.HORIZ_SIDE:
                return WeavingShape.IMMEDIATE
            elif end == WeavingPosition.HORIZ_UP:
                return WeavingShape.OVER_LONG_TIME
            elif end == WeavingPosition.HORIZ_DOWN:
                return WeavingShape.REPEAT
            else:
                return WeavingShape.IMMEDIATE

        if WeavingPosition.match(start, end, WeavingPosition.DOWN, WeavingPosition.UP):
            return WeavingShape.BLOCK_OVER_SHORT_TIME
        elif WeavingPosition.match(
            start, end, WeavingPosition.HORIZ_SIDE, WeavingPosition.UP
        ):
            return WeavingShape.AREA_OF_EFFECT_ON_TARGET
        elif WeavingPosition.match(
            start, end, WeavingPosition.HORIZ_SIDE, WeavingPosition.DOWN
        ):
            return WeavingShape.CHAIN
        elif WeavingPosition.match(
            start, end, WeavingPosition.HORIZ_SIDE, WeavingPosition.HORIZ_UP
        ):
            return WeavingShape.DELAYED
        elif WeavingPosition.match(
            start,
            end,
            WeavingPosition.HORIZ_SIDE,
            WeavingPosition.HORIZ_DOWN,
        ):
            return WeavingShape.DELAYED_AREA_OF_EFFECT

        return WeavingShape.IMMEDIATE


class WeavingPurpose:
    UNDEF_1: int = const(1)
    UNDEF_2: int = const(2)
    DAMAGE: int = const(3)
    INVEST: int = const(4)
    RESISTANCE: int = const(5)
    UNDEF_3: int = const(6)
    WEAKEN: int = const(7)
    STRENGTHEN: int = const(8)
    UNDEF_4: int = const(9)
    NULLIFY: int = const(10)

    @staticmethod
    def from_positions(start: int, end: int) -> int:
        if start == end:
            if end == WeavingPosition.UP:
                return WeavingPurpose.DAMAGE  # placeholder
            elif end == WeavingPosition.DOWN:
                return WeavingPurpose.DAMAGE  # placeholder
            elif end == WeavingPosition.HORIZ_SIDE:
                return WeavingPurpose.DAMAGE
            elif end == WeavingPosition.HORIZ_UP:
                return WeavingPurpose.INVEST
            elif end == WeavingPosition.HORIZ_DOWN:
                return WeavingPurpose.RESISTANCE
            else:
                return WeavingPurpose.DAMAGE

        if WeavingPosition.match(start, end, WeavingPosition.DOWN, WeavingPosition.UP):
            return WeavingPurpose.DAMAGE  # placeholder
        elif WeavingPosition.match(
            start, end, WeavingPosition.HORIZ_SIDE, WeavingPosition.UP
        ):
            return WeavingPurpose.WEAKEN
        elif WeavingPosition.match(
            start, end, WeavingPosition.HORIZ_SIDE, WeavingPosition.DOWN
        ):
            return WeavingPurpose.STRENGTHEN
        elif WeavingPosition.match(
            start, end, WeavingPosition.HORIZ_SIDE, WeavingPosition.HORIZ_UP
        ):
            return WeavingPurpose.DAMAGE  # placeholder
        elif WeavingPosition.match(
            start,
            end,
            WeavingPosition.HORIZ_SIDE,
            WeavingPosition.HORIZ_DOWN,
        ):
            return WeavingPurpose.NULLIFY

        return WeavingPurpose.DAMAGE


def get_constant_name(cls, value: int) -> str:
    for name in dir(cls):
        if not name.startswith("_"):
            if getattr(cls, name) == value:
                return name
    raise ValueError(f"No constant found with value {value}")


class Spell:
    def __init__(
        self,
        element: int = WeavingElement.FIRE,
        shape: int = WeavingShape.IMMEDIATE,
        purpose: int = WeavingPurpose.DAMAGE,
    ):
        self._element = element
        self._shape = shape
        self._purpose = purpose

    @property
    def element(self) -> int:
        return self._element

    @element.setter
    def element(self, value: int):
        self._element = value

    @property
    def shape(self) -> int:
        return self._shape

    @shape.setter
    def shape(self, value: int):
        self._shape = value

    @property
    def purpose(self) -> int:
        return self._purpose

    @purpose.setter
    def purpose(self, value: int):
        self._purpose = value

    def __str__(self) -> str:
        element_name = get_constant_name(WeavingElement, self._element)
        shape_name = get_constant_name(WeavingShape, self._shape)
        purpose_name = get_constant_name(WeavingPurpose, self._purpose)
        return (
            f"Spell(spell={element_name}, shape={shape_name}, purpose={purpose_name})"
        )

