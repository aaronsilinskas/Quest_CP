class Player(object):
    def __init__(self, team):
        self.team = team
        self.max_hitpoints = 255 * 5
        self.hitpoints = self.max_hitpoints
        self.full_heal_time = 90
        self.hitpoints_per_second = self.max_hitpoints / self.full_heal_time
        self.active_spells = []

        print("Player joined team: ", team)

    def update(self, ellapsed_time):
        hitpoints_gained = self.hitpoints_per_second * ellapsed_time
        self.hitpoints = min(self.max_hitpoints, self.hitpoints + hitpoints_gained)

        self.active_spells = self._age_spells(self.active_spells, ellapsed_time)

    def hit_by_spell(self, spell, team):
        if team == self.team:
            print("Hit by spell from same team: ", spell.name, spell.power)
            return

        self.hitpoints = self.hitpoints - spell.power
        print("Hitpoints reduced: ", spell.power, self.hitpoints)

    def _age_spells(self, spells, ellapsed_time):
        for spell in spells:
            spell.lifespan = max(spell.lifespan - ellapsed_time, 0)
            if spell.lifespan <= 1:
                spell.power = max(spell.max_power * spell.lifespan, 0)
        return [spell for spell in spells if spell.lifespan > 0]
