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
        aura.levels.subtract(levels)
        print("Aura after damage: ", aura.levels)


AURA_PURPOSE_MODIFIERS = {
    # RECHARGE: int = const(2)
    SpellPurpose.DAMAGE: DamageAuraPurposeModifier(),
    # INVEST: int = const(4)
    # RESISTANCE: int = const(5)
    # WEAKEN: int = const(7)
    # STRENGTHEN: int = const(8)
    # NULLIFY: int = const(10)
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
        self.ellapsed_since_tick = 0.0
        self.tick_levels = PrimaryElementLevels()
        self.tick_levels.water = hit.levels.water / self.duration
        self.tick_levels.earth = hit.levels.earth / self.duration
        self.tick_levels.fire = hit.levels.fire / self.duration

    def update(self, ellapsed_time: float, aura: Aura) -> bool:
        self.ellapsed_since_tick += ellapsed_time
        if self.ellapsed_since_tick >= 1.0:  # apply effect every
            self.ellapsed_since_tick -= 1.0

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
        raise ValueError(f"No modifier found for shape: {shape}")
