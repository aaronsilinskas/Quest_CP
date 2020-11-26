import random

# Spell
class Spell(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return type(self).__name__

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
        self.__power = power
        self.max_power = power
        self.previous_power = power
        self.lifespan = lifespan

    @property
    def power(self):
        return self.__power

    @property
    def power_increasing(self):
        return self.__power > self.previous_power

    @property
    def power_decreasing(self):
        return self.__power < self.previous_power

    @power.setter
    def power(self, v):
        self.previous_power = self.__power
        self.__power = v
        self.max_power = max(self.__power, v)


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


def map_vert(acceleration):
    x = acceleration[0]
    if x > 0.75:
        return "down"
    if x > 0.25:
        return "low"
    if x > -0.25:
        return "middle"
    if x > -0.75:
        return "high"
    return "up"


def map_horz(acceleration):
    y = acceleration[1]
    if abs(y) < 0.25:
        return "flat"
    if abs(y) < 0.75:
        return "angle"
    return "edge"


def select_spell(initial_acceleration, current_acceleration):
    # x = pointing up or down. Up = -1, Down = 1
    # z, y = rotation. Flat = abs(z)=1, y=0. On edge = abs(z)=0,abs(y)=1
    # vert: Up = -1, Down = 1
    # Horz: Flat = 0, Edge = 1, -1
    initial_vert = map_vert(initial_acceleration)
    initial_horz = map_horz(initial_acceleration)
    current_vert = map_vert(current_acceleration)
    current_horz = map_horz(current_acceleration)

    print(
        "Initial: {} {} -> Current {} {}".format(
            initial_vert, initial_horz, current_vert, current_horz
        )
    )

    if (initial_vert == "up"
        and current_vert == "up"):
        return LightSpell()

    if (
        initial_vert == "middle"
        and current_vert == "middle"
        and initial_horz == "flat"
        and current_horz == "edge"
    ):
        return FireSpell()

    if (initial_vert == "up"
        and current_vert == "middle"
        and current_horz == "flat"):
        return WindSpell()

    if (initial_vert == "down"
        and current_vert == "middle"
        and current_horz == "flat"):
        return WaterSpell()

    if (initial_vert == "down"
        and current_vert == "middle"
        and current_horz == "edge"):
        return EarthSpell()

    return None

    # return EarthSpell()


def age_spells(spell_states, ellapsed_time):
    for spell in spell_states:
        spell.lifespan = max(spell.lifespan - ellapsed_time, 0)
        if spell.lifespan <= 1:
            spell.power = max(spell.max_power * spell.lifespan, 0)

    return [spell for spell in spell_states if spell.lifespan > 0]
