from micropython import const
from util import get_constant_name


class SpellElement:
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


class SpellShape:
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


class SpellPurpose:
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

    @staticmethod
    def is_friendly(purpose: int) -> bool:
        return purpose in {SpellPurpose.RECHARGE, SpellPurpose.INVEST, SpellPurpose.RESISTANCE, SpellPurpose.STRENGTHEN}


class Spell:
    def __init__(
        self,
        element: int = SpellElement.FIRE,
        shape: int = SpellShape.IMMEDIATE,
        purpose: int = SpellPurpose.DAMAGE,
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
        element_name = get_constant_name(SpellElement, self._element)
        shape_name = get_constant_name(SpellShape, self._shape)
        purpose_name = get_constant_name(SpellPurpose, self._purpose)
        return (
            f"Spell(element={element_name}, shape={shape_name}, purpose={purpose_name})"
        )
