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
        for i in range(pixels.n):
            twinkle = random.uniform(0.5, 1.5)
            pixels[i] = (min(int(r * twinkle), 255), min(int(g * twinkle), 255), min(int(b * twinkle), 255))
        pixels.show()

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

def select_spell(initial_acceleration, current_acceleration):
    # x = pointing up or down. Up = -1, Down = 1
    # z, y = rotation. Flat = abs(z)=1, y=0. On edge = abs(z)=0,abs(y)=1
    vert_dir = initial_acceleration[0]
    if vert_dir < -0.75:
        return LightSpell()
    elif vert_dir < -0.25:
        return WindSpell()
    elif vert_dir < 0.25:
        return FireSpell()
    elif vert_dir < 0.75:
        return WaterSpell()

    return EarthSpell()

