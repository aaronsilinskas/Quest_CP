
# Spell
class Spell(object):
    def __init__(self):
        pass

    @property
    def name(self):
        return ''


spells = {}

def add_spell(spell):
    spells[spell.name] = spell

class LightSpell(Spell):
    @property
    def name(self):
        return 'light'

add_spell(LightSpell())

def select_spell(initial_acceleration):
    return spells['light']