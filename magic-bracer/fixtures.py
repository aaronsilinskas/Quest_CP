from player import Player
from spell.aura import Aura, SpellCast, SpellHit
from spell.aura_shape import AuraCaster, modify_aura
from spell.primary import PrimaryElementLevels
from spell.spell import Spell, SpellPurpose
from spell.weaving_thing import WeavingThing
from state_of_things.state_of_things import ThingObserver


class HardcodedAuraCaster(AuraCaster):
    def __init__(self, player: Player):
        self.player = player

    def cast(self, cast: SpellCast, aura: Aura, friendly: bool):
        print("HardcodedAuraCaster casting: ", cast)

        hit = SpellHit(cast.spell, cast.levels, friendly)

        print("Aura before hit: ", self.player.aura.levels)
        modify_aura(hit, self.player.aura, self)
        print("Aura after hit: ", self.player.aura.levels)


class HardcodedWeavingObserver(ThingObserver):
    def __init__(self, player: Player):
        self.player = player
        self.caster = HardcodedAuraCaster(player)

    def spell_cast(self, thing: WeavingThing, spell: Spell):
        print("Player aura: ", self.player.aura.levels)
        cast = SpellCast(spell)
        self.player.aura.modify_cast(cast)
        print("Modified cast: ", cast.levels)

        print("Aura before hit: ", self.player.aura.levels)
        # temporarily harcode friendliness to purpose instead of team
        friendly = SpellPurpose.is_friendly(spell.purpose)

        hit = SpellHit(spell, cast.levels, friendly)
        modify_aura(hit, self.player.aura, self.caster)
        print("Aura after hit: ", self.player.aura.levels)


def test_primary_element_distribution():
    elements = PrimaryElementLevels(100, 100, 100)

    elements.subtract(PrimaryElementLevels(0, 50, 0))
    print("Elements after subtract 1: ", elements)
    elements.subtract(PrimaryElementLevels(65, 0, 0))
    print("Elements after subtract 2: ", elements)
    elements.subtract(PrimaryElementLevels(0, 100, 0))
    print("Elements after subtract 3: ", elements)
    elements.subtract(PrimaryElementLevels(0, 100, 0))
    print("Elements after subtract 4: ", elements)
    
class LoggingWeavingObserver(ThingObserver):
    def state_changed(self, thing: WeavingThing, old_state, new_state):
        # print("State changed on ", thing.name, " from ", old_state.name, " to ", new_state.name)
        pass

    def spell_cast(self, thing: WeavingThing, spell: Spell):
        print("CAST: ", spell)

    def spell_selected(self, thing: WeavingThing, spell: Spell):
        print("Spell selected: ", spell)

    def shape_selected(self, thing: WeavingThing, spell: Spell):
        print("Shape selected: ", spell)

    def spell_ready(self, thing: WeavingThing, spell: Spell):
        print("Spell Ready: ", spell)
