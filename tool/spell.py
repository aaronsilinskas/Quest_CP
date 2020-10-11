
# Spell
class Spell(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return ''


spells = {}

class SpellState:

    def __init__(self, spell, power, lifespan):
        self.spell = spell
        self.name = spell.name
        self.__power = power
        self.max_power = power
        self.lifespan = lifespan

    @property
    def power(self):
        return self.__power

    @power.setter
    def power(self, v):
        self.__power = v
        self.max_power = max(self.__power, v)

def add_spell(spell):
    spells[spell.name] = spell

class LightSpell(Spell):
    @property
    def name(self):
        return type(self).__name__

add_spell(LightSpell())

def select_spell(initial_acceleration, current_acceleration):
    return spells['LightSpell']