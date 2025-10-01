from spell.spell import SpellElement


class PrimaryElementLevels:
    def __init__(self, fire: float = 100, water: float = 100, earth: float = 100):
        self._fire = fire
        self._water = water
        self._earth = earth

    @staticmethod
    def from_element(element: SpellElement) -> "PrimaryElementLevels":
        if element == SpellElement.WATER:
            return PrimaryElementLevels(fire=0, water=1, earth=0)
        elif element == SpellElement.EARTH:
            return PrimaryElementLevels(fire=0, water=0, earth=1)
        elif element == SpellElement.FIRE:
            return PrimaryElementLevels(fire=1, water=0, earth=0)
        elif element == SpellElement.LIGHT:
            return PrimaryElementLevels(fire=0.5, water=0.25, earth=0.25)
        elif element == SpellElement.DARK:
            return PrimaryElementLevels(fire=0, water=0.5, earth=0.5)
        elif element == SpellElement.ICE:
            return PrimaryElementLevels(fire=0, water=0.5, earth=0.5)
        elif element == SpellElement.AIR:
            return PrimaryElementLevels(fire=0.5, water=0.5, earth=0)
        elif element == SpellElement.LIGHTNING:
            return PrimaryElementLevels(fire=0.5, water=0, earth=0.5)
        elif element == SpellElement.TIME or element == SpellElement.GRAVITY:
            return PrimaryElementLevels(fire=0.33, water=0.33, earth=0.34)
        else:
            raise ValueError(f"Unknown element: {element}")

    def subtract(self, other: "PrimaryElementLevels"):
        fire_delta: float = self.fire - other.fire
        self.fire = max(0, fire_delta)
        water_delta: float = self.water - other.water
        self.water = max(0, water_delta)
        earth_delta: float = self.earth - other.earth
        self.earth = max(0, earth_delta)

        carryover = abs(fire_delta) if fire_delta < 0 else 0
        carryover += abs(water_delta) if water_delta < 0 else 0
        carryover += abs(earth_delta) if earth_delta < 0 else 0

        # distribute elements not yet subtracted evenly across non-zero elements
        # BUG: does not handle carryover that exceeds available power on a remaining element
        while carryover > 0:
            non_zero_elements = sum(
                1 for level in (self.fire, self.water, self.earth) if level > 0
            )
            if non_zero_elements == 0:
                break
            distribute = carryover / non_zero_elements
            if self.fire > 0:
                if self.fire >= distribute:
                    self.fire = self.fire - distribute
                    carryover -= distribute
                else:
                    carryover -= self.fire
                    self.fire = 0
            if self.water > 0 and carryover > 0:
                if self.water >= distribute:
                    self.water = self.water - distribute
                    carryover -= distribute
                else:
                    carryover -= self.water
                    self.water = 0
            if self.earth > 0 and carryover > 0:
                if self.earth >= distribute:
                    self.earth = self.earth - distribute
                    carryover -= distribute
                else:
                    carryover -= self.earth
                    self.earth = 0

    @property
    def fire(self) -> int:
        return self._fire

    @fire.setter
    def fire(self, value: int):
        self._fire = max(0, value)

    @property
    def water(self) -> int:
        return self._water

    @water.setter
    def water(self, value: int):
        self._water = max(0, value)

    @property
    def earth(self) -> int:
        return self._earth

    @earth.setter
    def earth(self, value: int):
        self._earth = max(0, value)

    def __str__(self) -> str:
        return f"Elements(fire={self._fire}, water={self._water}, earth={self._earth})"
