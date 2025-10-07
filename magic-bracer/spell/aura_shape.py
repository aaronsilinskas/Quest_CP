import player
from spell.aura import ActiveSpell, Aura, SpellCast, SpellHit
from spell.aura_purpose import apply_purpose_to_aura
from spell.primary import PrimaryElementLevels
from spell.spell import SpellShape, SpellPurpose


class AuraCaster:
    def cast(self, cast: SpellCast, aura: Aura, friendly: bool):
        pass


class AuraShapeModifier:
    def apply(self, hit: SpellHit, aura: Aura, caster: AuraCaster):
        pass


class ImmediateAuraModifier(AuraShapeModifier):
    def apply(self, hit: SpellHit, aura: Aura, caster: AuraCaster):
        apply_purpose_to_aura(hit.spell.purpose, hit.levels, aura)


class AreaOfEffectAuraModifier(AuraShapeModifier):
    def apply(self, hit: SpellHit, aura: Aura, caster: AuraCaster):
        reduced_levels = PrimaryElementLevels(
            water=max(0, hit.levels.water / 2),
            earth=max(0, hit.levels.earth / 2),
            fire=max(0, hit.levels.fire / 2),
        )

        apply_purpose_to_aura(hit.spell.purpose, reduced_levels, aura)

        if (
            reduced_levels.water <= 10
            and reduced_levels.earth <= 10
            and reduced_levels.fire <= 10
        ):
            return  # don't distribute an AOE if levels are too low

        print(
            f"Distributing AOE spell hit with reduced levels: {reduced_levels}: ", hit
        )
        cast = SpellCast(hit.spell, reduced_levels)
        caster.cast(cast, aura, hit.friendly)


class DelayedModifierActiveSpell(ActiveSpell):
    def __init__(
        self,
        hit: SpellHit,
        delay: float,
        modifier: AuraShapeModifier,
        caster: AuraCaster,
    ):
        self.hit = hit
        self.delay = delay
        self.modifier = modifier
        self.caster = caster
        self.elapsed_time = 0.0

    def update(self, elapsed_time: float, aura: Aura) -> bool:
        self.elapsed_time += elapsed_time
        if self.elapsed_time >= self.delay:
            print(f"Applying delayed spell hit after {self.delay} seconds: ", self.hit)
            self.modifier.apply(self.hit, aura, self.caster)
            return True
        return False


class DelayedAuraModifier(AuraShapeModifier):
    def __init__(self, delay: float, modifier: AuraShapeModifier):
        self.delay = delay
        self.modifier = modifier

    def apply(self, hit: SpellHit, aura: Aura, caster: AuraCaster):
        print(f"Delaying spell hit by {self.delay} seconds: ", hit)
        aura.active_spells.append(
            DelayedModifierActiveSpell(hit, self.delay, self.modifier, caster)
        )


class OverTimeActiveSpell(ActiveSpell):
    def __init__(self, hit: SpellHit, ticks: int, tick_delay: float):
        self.hit = hit
        self.ticks = ticks
        self.tick_delay = tick_delay
        self.elapsed_since_tick = 0.0
        self.tick_levels = PrimaryElementLevels(
            water=hit.levels.water / self.ticks,
            earth=hit.levels.earth / self.ticks,
            fire=hit.levels.fire / self.ticks,
        )

    def update(self, elapsed_time: float, aura: Aura) -> bool:
        self.elapsed_since_tick += elapsed_time
        if self.elapsed_since_tick >= self.tick_delay:  # apply effect every tick_delay
            self.elapsed_since_tick -= self.tick_delay

            print(f"Applying over time tick: {self.tick_levels} to aura: ", self.hit)
            apply_purpose_to_aura(self.hit.spell.purpose, self.tick_levels, aura)

            self.ticks -= 1
            if self.ticks <= 0:
                print("Over time effect completed.")
                return True
        return False


class OverTimeAuraModifier(AuraShapeModifier):
    def __init__(self, ticks: int, tick_delay: float):
        self.ticks = ticks
        self.tick_delay = tick_delay

    def apply(self, hit: SpellHit, aura: Aura, caster: AuraCaster):
        aura.active_spells.append(OverTimeActiveSpell(hit, self.ticks, self.tick_delay))


AURA_SHAPE_MODIFIERS = {
    SpellShape.AREA_OF_EFFECT: AreaOfEffectAuraModifier(),
    SpellShape.OVER_SHORT_TIME: OverTimeAuraModifier(ticks=10, tick_delay=1.0),
    SpellShape.IMMEDIATE: ImmediateAuraModifier(),
    SpellShape.OVER_LONG_TIME: OverTimeAuraModifier(ticks=10, tick_delay=3.0),
    SpellShape.REPEAT: OverTimeAuraModifier(ticks=4, tick_delay=0.5),
    # BLOCK_OVER_SHORT_TIME = const(6)
    SpellShape.AREA_OF_EFFECT_ON_TARGET: AreaOfEffectAuraModifier(),
    SpellShape.CHAIN: DelayedAuraModifier(2.0, AreaOfEffectAuraModifier()),
    SpellShape.DELAYED: DelayedAuraModifier(5.0, ImmediateAuraModifier()),
    SpellShape.DELAYED_AREA_OF_EFFECT: DelayedAuraModifier(
        5.0, AreaOfEffectAuraModifier()
    ),
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
