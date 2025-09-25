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


class WeavingPurpose:
    UNDEF_1: int = const(1)
    RECHARGE: int = const(2)
    DAMAGE: int = const(3)
    INVEST: int = const(4)
    RESISTANCE: int = const(5)
    UNDEF_3: int = const(6)
    WEAKEN: int = const(7)
    STRENGTHEN: int = const(8)
    UNDEF_4: int = const(9)
    NULLIFY: int = const(10)


class WeavingPositionEntry:

    def __init__(
        self,
        start_position: int,
        end_position: int,
        element: int,
        shape: int,
        purpose: int,
        color,
    ):
        self._start_position = start_position
        self._end_position = end_position
        self._element = element
        self._shape = shape
        self._purpose = purpose
        self._color = color

    @property
    def start_position(self) -> int:
        return self._start_position

    @property
    def end_position(self) -> int:
        return self._end_position

    @property
    def element(self) -> int:
        return self._element

    @property
    def shape(self) -> int:
        return self._shape

    @property
    def purpose(self) -> int:
        return self._purpose

    @property
    def color(self) -> int:
        return self._color


WEAVING_POSITIONS = [
    WeavingPositionEntry(
        start_position=WeavingPosition.UP,
        end_position=WeavingPosition.UP,
        element=WeavingElement.WATER,
        shape=WeavingShape.AREA_OF_EFFECT,
        purpose=WeavingPurpose.DAMAGE,
        color=(0, 0, 255),
    ),
    WeavingPositionEntry(
        start_position=WeavingPosition.DOWN,
        end_position=WeavingPosition.DOWN,
        element=WeavingElement.EARTH,
        shape=WeavingShape.OVER_SHORT_TIME,
        purpose=WeavingPurpose.RECHARGE,
        color=(255, 255, 0),
    ),
    WeavingPositionEntry(
        start_position=WeavingPosition.HORIZ_SIDE,
        end_position=WeavingPosition.HORIZ_SIDE,
        element=WeavingElement.FIRE,
        shape=WeavingShape.IMMEDIATE,
        purpose=WeavingPurpose.DAMAGE,
        color=(255, 0, 0),
    ),
    WeavingPositionEntry(
        start_position=WeavingPosition.HORIZ_UP,
        end_position=WeavingPosition.HORIZ_UP,
        element=WeavingElement.LIGHT,
        shape=WeavingShape.OVER_LONG_TIME,
        purpose=WeavingPurpose.INVEST,
        color=(255, 255, 255),
    ),
    WeavingPositionEntry(
        start_position=WeavingPosition.HORIZ_DOWN,
        end_position=WeavingPosition.HORIZ_DOWN,
        element=WeavingElement.DARK,
        shape=WeavingShape.REPEAT,
        purpose=WeavingPurpose.RESISTANCE,
        color=(0, 0, 0),
    ),
    WeavingPositionEntry(
        start_position=WeavingPosition.DOWN,
        end_position=WeavingPosition.UP,
        element=WeavingElement.ICE,
        shape=WeavingShape.BLOCK_OVER_SHORT_TIME,
        purpose=WeavingPurpose.DAMAGE,
        color=(0, 255, 0),
    ),
    WeavingPositionEntry(
        start_position=WeavingPosition.HORIZ_SIDE,
        end_position=WeavingPosition.UP,
        element=WeavingElement.AIR,
        shape=WeavingShape.AREA_OF_EFFECT_ON_TARGET,
        purpose=WeavingPurpose.WEAKEN,
        color=(255, 0, 255),
    ),
    WeavingPositionEntry(
        start_position=WeavingPosition.HORIZ_SIDE,
        end_position=WeavingPosition.DOWN,
        element=WeavingElement.LIGHTNING,
        shape=WeavingShape.CHAIN,
        purpose=WeavingPurpose.STRENGTHEN,
        color=(255, 128, 0),
    ),
    WeavingPositionEntry(
        start_position=WeavingPosition.HORIZ_SIDE,
        end_position=WeavingPosition.HORIZ_UP,
        element=WeavingElement.TIME,
        shape=WeavingShape.DELAYED,
        purpose=WeavingPurpose.DAMAGE,
        color=(128, 128, 128),
    ),
    WeavingPositionEntry(
        start_position=WeavingPosition.HORIZ_SIDE,
        end_position=WeavingPosition.HORIZ_DOWN,
        element=WeavingElement.GRAVITY,
        shape=WeavingShape.DELAYED_AREA_OF_EFFECT,
        purpose=WeavingPurpose.NULLIFY,
        color=(64, 64, 64),
    ),
    WeavingPositionEntry(
        start_position=WeavingPosition.HORIZ_UP,
        end_position=WeavingPosition.UP,
        element=WeavingElement.AIR,
        shape=WeavingShape.AREA_OF_EFFECT_ON_TARGET,
        purpose=WeavingPurpose.WEAKEN,
        color=(255, 0, 255),
    ),
    WeavingPositionEntry(
        start_position=WeavingPosition.HORIZ_UP,
        end_position=WeavingPosition.DOWN,
        element=WeavingElement.LIGHTNING,
        shape=WeavingShape.CHAIN,
        purpose=WeavingPurpose.STRENGTHEN,
        color=(255, 128, 0),
    ),
    WeavingPositionEntry(
        start_position=WeavingPosition.HORIZ_DOWN,
        end_position=WeavingPosition.UP,
        element=WeavingElement.AIR,
        shape=WeavingShape.AREA_OF_EFFECT_ON_TARGET,
        purpose=WeavingPurpose.WEAKEN,
        color=(255, 0, 255),
    ),
    WeavingPositionEntry(
        start_position=WeavingPosition.HORIZ_DOWN,
        end_position=WeavingPosition.DOWN,
        element=WeavingElement.LIGHTNING,
        shape=WeavingShape.CHAIN,
        purpose=WeavingPurpose.STRENGTHEN,
        color=(255, 128, 0),
    ),
]


def match_position(start: int, end: int) -> WeavingPositionEntry:
    for entry in WEAVING_POSITIONS:
        if entry.start_position == start and entry.end_position == end:
            return entry
        if entry.start_position == end and entry.end_position == start:
            return entry
    return WEAVING_POSITIONS[2]  # Default to FIRE/IMMEDIATE/DAMAGE


def match_element(element: int) -> WeavingPositionEntry:
    for entry in WEAVING_POSITIONS:
        if entry.element == element:
            return entry
    return WEAVING_POSITIONS[2]  # Default to FIRE/IMMEDIATE/DAMAGE


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
