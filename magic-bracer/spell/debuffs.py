from spell.aura import Aura, ActiveSpell
from spell.spell import Spell

class ApplyOverTime(ActiveSpell):
    def __init__(self, spell: Spell, duration: float):
        self.spell = spell
        self.duration = duration

    def update(self, ellapsed_time: float, aura: "Aura"):
        if self.spell.element in aura.levels.__annotations__:
            setattr(aura.levels, self.spell.element, getattr(aura.levels, self.spell.element) + self.spell.rate * ellapsed_time)


# | Area of Effect on Player        |                                    |
# | ------------------------------- | ---------------------------------- |
# | Apply Over Short Time (DoT/HoT) | Recharge - Defensive               |
# | Apply Immediately               | Damage - Offensive                 |
# | Apply Over Long Time (Aura)     | Invest (transfer/heal) - Defensive |
# | Fast Repeat Apply               | Resistance - Defensive             |
# | Block Element Over Short Time   |                                    |
# | Area of Effect on Target        | Weaken - Offensive                 |
# | Chain                           | Strengthen - Defensive             |
# | Apply After a Delay             |                                    |
# | Area of Effect After a Delay    | Nullify - Offensive                |
# | *Area of Effect on Target*      | *Weaken - Offensive*               |
# | *Chain*                         | *Strengthen - Defensive*           |
# |                                 |                                    |
# | *Area of Effect on Target*      | *Weaken - Offensive*               |
# | *Chain*                         | *Strengthen - Defensive*           |