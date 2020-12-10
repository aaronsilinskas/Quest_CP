import random


class Spell(object):
    def __init__(self):
        self._name = type(self).__name__[: -len("Spell")]

    @property
    def name(self):
        return self._name

    def draw(self, pixels, state, ellapsed):
        pass

    def draw_simple(self, pixels, color, power):
        r = color[0] * power
        g = color[1] * power
        b = color[2] * power
        for i in range(len(pixels)):
            twinkle = random.uniform(0.5, 1.5)
            pixels[i] = (
                min(int(r * twinkle), 255),
                min(int(g * twinkle), 255),
                min(int(b * twinkle), 255),
            )


class SpellState:
    def __init__(self, spell, power=0, lifespan=10):
        self.spell = spell
        self.name = spell.name
        self.power = power
        self.lifespan = lifespan


class LightSpell(Spell):
    def draw(self, pixels, state, ellapsed):
        self.draw_simple(pixels, (255, 255, 255), state.power)


class FireSpell(Spell):
    def draw(self, pixels, state, ellapsed):
        self.draw_simple(pixels, (255, 0, 0), state.power)


class WaterSpell(Spell):
    def draw(self, pixels, state, ellapsed):
        self.draw_simple(pixels, (0, 64, 255), state.power)


class EarthSpell(Spell):
    def draw(self, pixels, state, ellapsed):
        self.draw_simple(pixels, (210, 105, 30), state.power)


class WindSpell(Spell):
    def draw(self, pixels, state, ellapsed):
        self.draw_simple(pixels, (255, 0, 255), state.power)


spells = [LightSpell(), FireSpell(), WaterSpell(), EarthSpell(), WindSpell()]

VERT_DOWN = 1
VERT_LOW = 2
VERT_MIDDLE = 3
VERT_HIGH = 4
VERT_UP = 5


def _map_vert(acceleration):
    x = acceleration[0]
    if x > 0.75:
        return VERT_DOWN
    if x > 0.25:
        return VERT_LOW
    if x > -0.25:
        return VERT_MIDDLE
    if x > -0.75:
        return VERT_HIGH
    return VERT_UP


HORZ_FLAT = 1
HORZ_ANGLE = 2
HORZ_EDGE = 3


def _map_horz(acceleration):
    y = abs(acceleration[1])
    if y < 0.35:
        return HORZ_FLAT
    if y < 0.65:
        return HORZ_ANGLE
    return HORZ_EDGE


def select_spell(initial_acceleration, current_acceleration):
    # x = pointing up or down. Up = -1, Down = 1
    # z, y = rotation. Flat = abs(z)=1, y=0. On edge = abs(z)=0,abs(y)=1
    # vert: Up = -1, Down = 1
    # Horz: Flat = 0, Edge = 1, -1
    initial_vert = _map_vert(initial_acceleration)
    initial_horz = _map_horz(initial_acceleration)
    current_vert = _map_vert(current_acceleration)
    current_horz = _map_horz(current_acceleration)

    print(
        "Initial: {} {} -> Current {} {}".format(
            initial_vert, initial_horz, current_vert, current_horz
        )
    )

    if initial_vert == VERT_UP and current_vert == VERT_UP:
        return LightSpell()

    if (
        initial_vert == VERT_MIDDLE
        and initial_horz == HORZ_FLAT
        and current_vert == VERT_MIDDLE
        and current_horz == HORZ_EDGE
    ):
        return FireSpell()

    if (
        initial_vert == VERT_UP
        and current_vert == VERT_MIDDLE
        and current_horz == HORZ_FLAT
    ):
        return WindSpell()

    if (
        initial_vert == VERT_DOWN
        and current_vert == VERT_MIDDLE
        and current_horz == HORZ_FLAT
    ):
        return WaterSpell()

    if (
        initial_vert == VERT_DOWN
        and current_vert == VERT_MIDDLE
        and current_horz == HORZ_EDGE
    ):
        return EarthSpell()

    return None


def age_spells(spell_states, ellapsed_time):
    for spell in spell_states:
        spell.lifespan = max(spell.lifespan - ellapsed_time, 0)
        if spell.lifespan <= 1:
            spell.power = max(spell.max_power * spell.lifespan, 0)

    return [spell for spell in spell_states if spell.lifespan > 0]
