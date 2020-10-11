
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
        self.power = power
        self.lifespan = lifespan

def add_spell(spell):
    spells[spell.name] = spell

class LightSpell(Spell):
    @property
    def name(self):
        return type(self).__name__

add_spell(LightSpell())

def select_spell(initial_acceleration, current_acceleration):
    return spells['LightSpell']