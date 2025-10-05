from spell.aura import ActiveSpell, Aura, SpellCast, SpellHit
from spell.primary import PrimaryElementLevels
from spell.spell import SpellPurpose


class AuraPurposeModifier:
    def apply(self, levels: PrimaryElementLevels, aura: Aura):
        pass


class DamageAuraPurposeModifier(AuraPurposeModifier):
    def apply(self, levels: PrimaryElementLevels, aura: Aura):
        aura.levels.reduce(levels, distribute=True)
        print("Aura after damage: ", aura.levels)


class InvestAuraPurposeModifier(AuraPurposeModifier):
    def apply(self, levels: PrimaryElementLevels, aura: Aura):
        aura.levels.increase(levels)
        print("Aura after invest: ", aura.levels)


class ResistanceActiveSpell(ActiveSpell):
    def __init__(self, resistance: PrimaryElementLevels):
        self.resistance = resistance
        self.duration = 30.0  # lasts for 30 seconds

    def update(self, elapsed_time: float, aura: Aura) -> bool:
        if self.resistance.empty():
            print("ResistanceActiveSpell completed.")
            return True
        self.duration -= elapsed_time
        if self.duration <= 0:
            print("ResistanceActiveSpell duration ended.")
            return True
        return False

    def modify_hit(self, aura: Aura, hit: SpellHit):
        remainder = hit.levels.reduce(self.resistance)
        self.resistance = remainder
        print(
            f"ResistanceActiveSpell modified hit to: {hit.levels}, remaining resistance: {self.resistance}"
        )


class ResistanceAuraPurposeModifier(AuraPurposeModifier):
    def apply(self, levels: PrimaryElementLevels, aura: Aura):
        print("Applying resistance to aura: ", levels)
        aura.active_spells.append(ResistanceActiveSpell(levels))


class WeakenActiveSpell(ActiveSpell):
    def __init__(self, amount: PrimaryElementLevels):
        self.amount = amount
        self.duration = 30.0  # lasts for 30 seconds

    def update(self, elapsed_time: float, aura: Aura) -> bool:
        self.duration -= elapsed_time
        if self.duration <= 0:
            print("WeakenActiveSpell duration ended.")
            return True
        return False

    def modify_cast(self, aura: Aura, cast: SpellCast):
        cast.levels.reduce(self.amount)
        print(f"WeakenActiveSpell modified cast to: {cast.levels}")


class WeakenAuraPurposeModifier(AuraPurposeModifier):
    def apply(self, levels: PrimaryElementLevels, aura: Aura):
        print("Applying weaken to aura: ", levels)
        aura.active_spells.append(WeakenActiveSpell(levels))


class StrengthenActiveSpell(ActiveSpell):
    def __init__(self, amount: PrimaryElementLevels):
        self.amount = amount
        self.duration = 30.0  # lasts for 30 seconds

    def update(self, elapsed_time: float, aura: Aura) -> bool:
        self.duration -= elapsed_time
        if self.duration <= 0:
            print("StrengthenActiveSpell duration ended.")
            return True
        return False

    def modify_cast(self, aura: Aura, cast: SpellCast):
        cast.levels.increase(self.amount)
        print(f"StrengthenActiveSpell modified cast to: {cast.levels}")


class StrengthenAuraPurposeModifier(AuraPurposeModifier):
    def apply(self, levels: PrimaryElementLevels, aura: Aura):
        print("Applying strengthen to aura: ", levels)
        aura.active_spells.append(StrengthenActiveSpell(levels))


AURA_PURPOSE_MODIFIERS = {
    SpellPurpose.DAMAGE: DamageAuraPurposeModifier(),
    SpellPurpose.INVEST: InvestAuraPurposeModifier(),
    SpellPurpose.RESISTANCE: ResistanceAuraPurposeModifier(),
    SpellPurpose.WEAKEN: WeakenAuraPurposeModifier(),
    SpellPurpose.STRENGTHEN: StrengthenAuraPurposeModifier(),
}


def apply_purpose_to_aura(
    purpose: SpellPurpose, levels: PrimaryElementLevels, aura: Aura
):
    modifier = AURA_PURPOSE_MODIFIERS.get(purpose)
    if modifier:
        modifier.apply(levels, aura)
    else:
        raise ValueError(f"Unsupported purpose for AuraPurposeModifier: {purpose}")