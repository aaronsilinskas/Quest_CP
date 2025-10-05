import player
from spell.aura import ActiveSpell, Aura, SpellCast, SpellHit
from spell.primary import PrimaryElementLevels
from spell.spell import SpellShape, SpellPurpose


class AuraCaster:
    def cast(self, cast: SpellCast, aura: Aura, friendly: bool):
        pass


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


class AuraShapeModifier:
    def apply(self, hit: SpellHit, aura: Aura, caster: AuraCaster):
        pass


class ImmediateAuraModifier(AuraShapeModifier):
    def apply(self, hit: SpellHit, aura: Aura, caster: AuraCaster):
        apply_purpose_to_aura(hit.spell.purpose, hit.levels, aura)


class AreaOfEffectAuraModifier(AuraShapeModifier):
    def apply(self, hit: SpellHit, aura: Aura, caster: AuraCaster):
        reduced_levels = PrimaryElementLevels()
        reduced_levels.water = max(0, hit.levels.water / 2)
        reduced_levels.earth = max(0, hit.levels.earth / 2)
        reduced_levels.fire = max(0, hit.levels.fire / 2)

        apply_purpose_to_aura(hit.spell.purpose, reduced_levels, aura)

        if (
            reduced_levels.water <= 10
            and reduced_levels.earth <= 10
            and reduced_levels.fire <= 10
        ):
            return  # don't distribute an AOE if levels are too low

        print(f"Distributing AOE spell hit with reduced levels: {reduced_levels}")
        cast = SpellCast(hit.spell, reduced_levels)
        caster.cast(cast, aura, hit.friendly)


class OverShortTimeActiveSpell(ActiveSpell):
    def __init__(self, hit: SpellHit):
        self.hit = hit
        self.duration = 10.0  # total duration of the effect
        self.elapsed_since_tick = 0.0
        self.tick_levels = PrimaryElementLevels()
        self.tick_levels.water = hit.levels.water / self.duration
        self.tick_levels.earth = hit.levels.earth / self.duration
        self.tick_levels.fire = hit.levels.fire / self.duration

    def update(self, elapsed_time: float, aura: Aura) -> bool:
        self.elapsed_since_tick += elapsed_time
        if self.elapsed_since_tick >= 1.0:  # apply effect every
            self.elapsed_since_tick -= 1.0

            print(f"Applying over short time tick: {self.tick_levels} to aura.")
            apply_purpose_to_aura(self.hit.spell.purpose, self.tick_levels, aura)

            self.duration -= 1.0
            if self.duration <= 0:
                print("Over time effect completed.")
                return True
        return False


class OverShortTimeAuraModifier(AuraShapeModifier):
    def apply(self, hit: SpellHit, aura: Aura, caster: AuraCaster):
        aura.active_spells.append(OverShortTimeActiveSpell(hit))


AURA_SHAPE_MODIFIERS = {
    SpellShape.AREA_OF_EFFECT: AreaOfEffectAuraModifier(),
    SpellShape.OVER_SHORT_TIME: OverShortTimeAuraModifier(),
    SpellShape.IMMEDIATE: ImmediateAuraModifier(),
    # OVER_LONG_TIME: int = const(4)
    # REPEAT: int = const(5)
    # BLOCK_OVER_SHORT_TIME = const(6)
    SpellShape.AREA_OF_EFFECT_ON_TARGET: AreaOfEffectAuraModifier(),
    # CHAIN = const(8)
    # DELAYED = const(9)
    # DELAYED_AREA_OF_EFFECT = const(10)
}


def modify_aura(hit: SpellHit, aura: Aura, caster: AuraCaster):
    spell_friendly = SpellPurpose.is_friendly(hit.spell.purpose)
    if hit.friendly != spell_friendly:
        # ignore spell hits where the spell and caster purpose don't match
        return

    # apply any buffs and debuffs from active spells
    aura.modify_hit(hit)

    shape = hit.spell.shape
    modifier = AURA_SHAPE_MODIFIERS.get(shape)
    if modifier:
        modifier.apply(hit, aura, caster)
    else:
        raise ValueError(f"No shape modifier found for shape: {shape}")
