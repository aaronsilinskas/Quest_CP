from spell.spell import Spell
from spell.primary import PrimaryElementLevels


class SpellCast:
    def __init__(self, spell: Spell, levels: PrimaryElementLevels = None):
        self._spell = spell
        self._levels = levels if levels else PrimaryElementLevels.from_element(spell.element)

    @property
    def spell(self) -> Spell:
        return self._spell

    @property
    def levels(self) -> PrimaryElementLevels:
        return self._levels

    def __str__(self) -> str:
        return f"CastSpell(spell={self._spell}, levels={self._levels})"


class SpellHit:
    def __init__(self, spell: Spell, levels: PrimaryElementLevels, friendly: bool):
        self._spell = spell
        self._levels = levels
        self._friendly = friendly

    @property
    def spell(self) -> Spell:
        return self._spell

    @property
    def levels(self) -> PrimaryElementLevels:
        return self._levels

    @property
    def friendly(self) -> bool:
        """True if the spell's origin was caster regarded as friendly"""
        return self._friendly

    def __str__(self) -> str:
        return f"CastSpell(spell={self._spell}, levels={self._levels}, friendly={self._friendly})"


class ActiveSpell:

    def update(self, ellapsed_time: float, aura: "Aura") -> bool:
        return True

    def modify_cast(self, aura: "Aura", cast: SpellCast):
        pass

    def modify_hit(self, aura: "Aura", hit: SpellHit):
        pass


class Aura:

    def __init__(self, ambient_magic: float = 1.0, level_max: float = 100.0):
        self._levels: PrimaryElementLevels = PrimaryElementLevels()
        self._active_spells: list[ActiveSpell] = []
        self._ambient_magic = ambient_magic
        self._level_max = level_max
        self._ellapsed_since_ambient_tick = 0.0

    @property
    def levels(self) -> PrimaryElementLevels:
        return self._levels

    @property
    def active_spells(self) -> list[ActiveSpell]:
        return self._active_spells
    
    @property
    def ambient_magic(self) -> float:
        return self._ambient_magic
    
    @property
    def level_max(self) -> float:
        return self._level_max

    def update(self, ellapsed_time: float):
        self._ellapsed_since_ambient_tick += ellapsed_time
        if self._ellapsed_since_ambient_tick >= 1.0:  # apply ambient magic every second
            self._ellapsed_since_ambient_tick -= 1.0
            
            # apply ambient magic to aura levels
            self._levels.water = min(self._ambient_magic + self._levels.water, self._level_max)
            self._levels.earth = min(self._ambient_magic + self._levels.earth, self._level_max)
            self._levels.fire = min(self._ambient_magic + self._levels.fire, self._level_max)

        for spell in self._active_spells:
            if spell.update(ellapsed_time, self):
                self._active_spells.remove(spell)

    def modify_cast(self, cast: SpellCast):
        # amplify the cast by aura levels
        cast.levels.water *= self.levels.water
        cast.levels.earth *= self.levels.earth
        cast.levels.fire *= self.levels.fire

        for spell in self._active_spells:
            spell.modify_cast(self, cast)

    def modify_hit(self, hit: SpellHit):
        # only resist unfriendly hits
        if not hit.friendly:
            # innately resist the cast by a quarter of aura levels
            hit.levels.water -= max(0, self.levels.water / 4)
            hit.levels.earth -= max(0, self.levels.earth / 4)
            hit.levels.fire -= max(0, self.levels.fire / 4)

        for spell in self._active_spells:
            spell.modify_hit(self, hit)
