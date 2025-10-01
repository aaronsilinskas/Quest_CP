from spell.spell import SpellElement, SpellShape, SpellPurpose


class SpellColorEntry:
    def __init__(
        self, element: int, shape: int, purpose: int, color: tuple[int, int, int]
    ):
        self.element = element
        self.shape = shape
        self.purpose = purpose
        self.color = color


SPELL_COLORS = [
    SpellColorEntry(
        element=SpellElement.WATER,
        shape=SpellShape.AREA_OF_EFFECT,
        purpose=SpellPurpose.DAMAGE,
        color=(0, 0, 255),
    ),
    SpellColorEntry(
        element=SpellElement.EARTH,
        shape=SpellShape.OVER_SHORT_TIME,
        purpose=SpellPurpose.RECHARGE,
        color=(255, 255, 0),
    ),
    SpellColorEntry(
        element=SpellElement.FIRE,
        shape=SpellShape.IMMEDIATE,
        purpose=SpellPurpose.DAMAGE,
        color=(255, 0, 0),
    ),
    SpellColorEntry(
        element=SpellElement.LIGHT,
        shape=SpellShape.OVER_LONG_TIME,
        purpose=SpellPurpose.INVEST,
        color=(255, 255, 255),
    ),
    SpellColorEntry(
        element=SpellElement.DARK,
        shape=SpellShape.REPEAT,
        purpose=SpellPurpose.RESISTANCE,
        color=(0, 0, 0),
    ),
    SpellColorEntry(
        element=SpellElement.ICE,
        shape=SpellShape.BLOCK_OVER_SHORT_TIME,
        purpose=SpellPurpose.DAMAGE,
        color=(0, 255, 0),
    ),
    SpellColorEntry(
        element=SpellElement.AIR,
        shape=SpellShape.AREA_OF_EFFECT_ON_TARGET,
        purpose=SpellPurpose.WEAKEN,
        color=(255, 0, 255),
    ),
    SpellColorEntry(
        element=SpellElement.LIGHTNING,
        shape=SpellShape.CHAIN,
        purpose=SpellPurpose.STRENGTHEN,
        color=(255, 128, 0),
    ),
    SpellColorEntry(
        element=SpellElement.TIME,
        shape=SpellShape.DELAYED,
        purpose=SpellPurpose.DAMAGE,
        color=(128, 128, 128),
    ),
    SpellColorEntry(
        element=SpellElement.GRAVITY,
        shape=SpellShape.DELAYED_AREA_OF_EFFECT,
        purpose=SpellPurpose.NULLIFY,
        color=(64, 64, 64),
    ),
    SpellColorEntry(
        element=SpellElement.AIR,
        shape=SpellShape.AREA_OF_EFFECT_ON_TARGET,
        purpose=SpellPurpose.WEAKEN,
        color=(255, 0, 255),
    ),
    SpellColorEntry(
        element=SpellElement.LIGHTNING,
        shape=SpellShape.CHAIN,
        purpose=SpellPurpose.STRENGTHEN,
        color=(255, 128, 0),
    ),
    SpellColorEntry(
        element=SpellElement.AIR,
        shape=SpellShape.AREA_OF_EFFECT_ON_TARGET,
        purpose=SpellPurpose.WEAKEN,
        color=(255, 0, 255),
    ),
    SpellColorEntry(
        element=SpellElement.LIGHTNING,
        shape=SpellShape.CHAIN,
        purpose=SpellPurpose.STRENGTHEN,
        color=(255, 128, 0),
    ),
]


def color_for_element(element: int) -> tuple[int, int, int]:
    for entry in SPELL_COLORS:
        if entry.element == element:
            return entry
    raise ValueError(f"No color found for element {element}")


def color_for_shape(shape: int) -> tuple[int, int, int]:
    for entry in SPELL_COLORS:
        if entry.shape == shape:
            return entry
    raise ValueError(f"No color found for shape {shape}")


def color_for_purpose(purpose: int) -> tuple[int, int, int]:
    for entry in SPELL_COLORS:
        if entry.purpose == purpose:
            return entry
    raise ValueError(f"No color found for purpose {purpose}")
