from encoder import BitDecoder, BitEncoder
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
    AREA_OF_EFFECT: int = const(1)  # instant cast to surrounding targets
    OVER_SHORT_TIME: int = const(2)  # a cast that applies its effect over a short time
    IMMEDIATE: int = const(3)  # a cast that applies its effect instantly
    OVER_LONG_TIME: int = const(4)  # a cast that applies its effect over a long time
    REPEAT: int = const(5)  # a divide a cast over several short bursts
    BLOCK_OVER_SHORT_TIME = const(6)
    AREA_OF_EFFECT_ON_TARGET = const(7)  # instant cast to surrounding targets
    CHAIN = const(8)  # delayed cast to surrounding targets
    DELAYED = const(9)  # cast is applied after a delay
    DELAYED_AREA_OF_EFFECT = const(10)  # AOE is applied after a delay


class SpellPurpose:
    UNDEF_1: int = const(1)
    UNDEF_2: int = const(2)
    DAMAGE: int = const(3)  # reduce levels of an aura
    INVEST: int = const(4)  # increase levels of an aura
    RESISTANCE: int = const(5)  # temporarily reduce levels of a hit
    UNDEF_3: int = const(6)
    WEAKEN: int = const(7)  # temporarily reduce levels of a a cast
    STRENGTHEN: int = const(8)  # temporarily increase levels of a cast
    UNDEF_4: int = const(9)
    UNDEF_5: int = const(10)

    @staticmethod
    def is_friendly(purpose: int) -> bool:
        return purpose in {
            SpellPurpose.INVEST,
            SpellPurpose.RESISTANCE,
            SpellPurpose.STRENGTHEN,
        }


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

    def encode(self, encoder: BitEncoder):
        encoder.write_bits(self._element, 4)
        encoder.write_bits(self._shape, 4)
        encoder.write_bits(self._purpose, 4)

    @staticmethod
    def decode(decoder: BitDecoder) -> "Spell":
        element = decoder.read_bits(4)
        shape = decoder.read_bits(4)
        purpose = decoder.read_bits(4)
        return Spell(element, shape, purpose)
    
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
    
