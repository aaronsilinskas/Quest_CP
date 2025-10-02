from spell.spell import Spell
from spell.primary import PrimaryElementLevels


class CastSpell:
    def __init__(self, spell: Spell):
        self._spell = spell
        self._levels = PrimaryElementLevels.from_element(spell.element)

    @property
    def spell(self) -> Spell:
        return self._spell

    @property
    def levels(self) -> PrimaryElementLevels:
        return self._levels

    def __str__(self) -> str:
        return f"CastSpell(spell={self._spell}, levels={self._levels})"


class ActiveSpell:

    def update(self, ellapsed_time: float, aura: "Aura") -> bool:
        return True

    def modify_cast(self, aura: "Aura", cast: CastSpell):
        pass

    def modify_hit(self, aura: "Aura", cast: CastSpell):
        pass


class Aura:

    def __init__(self):
        self._levels: PrimaryElementLevels = PrimaryElementLevels()
        self._active_spells: list[ActiveSpell] = []

    @property
    def levels(self) -> PrimaryElementLevels:
        return self._levels

    @property
    def active_spells(self) -> list[ActiveSpell]:
        return self._active_spells

    def update(self, ellapsed_time: float):
        for spell in self._active_spells:
            if spell.update(ellapsed_time, self):
                self._active_spells.remove(spell)

    def modify_cast(self, cast: CastSpell):
        # amplify the cast by aura levels
        cast.levels.water *= self.levels.water
        cast.levels.earth *= self.levels.earth
        cast.levels.fire *= self.levels.fire

        for spell in self._active_spells:
            spell.modify_cast(self, cast)

    def apply_hit(self, cast: CastSpell):
        # innately resist the cast by a quarter of aura levels
        cast.levels.water -= max(0, self.levels.water / 4)
        cast.levels.earth -= max(0, self.levels.earth / 4)
        cast.levels.fire -= max(0, self.levels.fire / 4)

        for spell in self._active_spells:
            spell.modify_hit(self, cast)

        # TODO: get purpose function that will apply to this aura
        # TODO: apply the shape

        # TODO: replace this IMMEDIATE hard-coding
        self.levels.subtract(cast.levels)
