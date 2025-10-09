from encoder import BitDecoder, BitEncoder
from spell.spell import SpellElement


class PrimaryElementLevels:
    def __init__(self, water: float = 100, earth: float = 100, fire: float = 100):        
        self._water = water
        self._earth = earth
        self._fire = fire

    @staticmethod
    def from_element(element: SpellElement) -> "PrimaryElementLevels":
        if element == SpellElement.WATER:
            return PrimaryElementLevels(water=1, earth=0, fire=0)
        elif element == SpellElement.EARTH:
            return PrimaryElementLevels(water=0, earth=1, fire=0)
        elif element == SpellElement.FIRE:
            return PrimaryElementLevels(water=0, earth=0, fire=1)
        elif element == SpellElement.LIGHT:
            return PrimaryElementLevels(water=0.25, earth=0.25, fire=0.5)
        elif element == SpellElement.DARK:
            return PrimaryElementLevels(water=0.5, earth=0.5, fire=0)
        elif element == SpellElement.ICE:
            return PrimaryElementLevels(water=0.5, earth=0.5, fire=0)
        elif element == SpellElement.AIR:
            return PrimaryElementLevels(water=0.5, earth=0, fire=0.5)
        elif element == SpellElement.LIGHTNING:
            return PrimaryElementLevels(water=0, earth=0.5, fire=0.5)
        elif element == SpellElement.TIME or element == SpellElement.GRAVITY:
            return PrimaryElementLevels(water=0.33, earth=0.34, fire=0.33)
        else:
            raise ValueError(f"Unknown element: {element}")

    def reduce(
        self, amount: "PrimaryElementLevels", distribute: bool = False
    ) -> "PrimaryElementLevels":
        """Reduce levels by the given amount, returning amount of left over. If distribute is True,
        distribute excess reduction evenly across other non-zero elements."""
        water_delta: float = self.water - amount.water
        self.water = max(0, water_delta)
        earth_delta: float = self.earth - amount.earth
        self.earth = max(0, earth_delta)
        fire_delta: float = self.fire - amount.fire
        self.fire = max(0, fire_delta)

        remainder = PrimaryElementLevels()
        if distribute:
            if water_delta < 0:
                water_to_fire = self.fire + water_delta
                self.fire = max(0, water_to_fire)
                if water_to_fire < 0:
                    water_to_earth = self.earth + water_to_fire
                    self.earth = max(0, water_to_earth)
                    remainder.water = abs(water_to_earth) if water_to_earth < 0 else 0
            if earth_delta < 0:
                earth_to_water = self.water + earth_delta
                self.water = max(0, earth_to_water)
                if earth_to_water < 0:
                    earth_to_fire = self.fire + earth_to_water
                    self.fire = max(0, earth_to_fire)
                    remainder.earth = abs(earth_to_fire) if earth_to_fire < 0 else 0
            if fire_delta < 0:
                fire_to_earth = self.earth + fire_delta
                self.earth = max(0, fire_to_earth)
                if fire_to_earth < 0:
                    fire_to_water = self.water + fire_to_earth
                    self.water = max(0, fire_to_water)
                    remainder.fire = abs(fire_to_water) if fire_to_water < 0 else 0
        else:
            remainder.water = abs(water_delta) if water_delta < 0 else 0
            remainder.earth = abs(earth_delta) if earth_delta < 0 else 0
            remainder.fire = abs(fire_delta) if fire_delta < 0 else 0

        # consider very small values as zero
        if self.water < 1:
            self.water = 0
        if self.earth < 1:
            self.earth = 0
        if self.fire < 1:
            self.fire = 0

        return remainder

    def increase(self, amount: "PrimaryElementLevels") -> "PrimaryElementLevels":
        """Increase levels by the given amount."""
        self.water += amount.water
        self.earth += amount.earth
        self.fire += amount.fire

        remainder = PrimaryElementLevels()
        if self.water > 100:
            remainder.water = self.water - 100
            self.water = 100
        if self.earth > 100:
            remainder.earth = self.earth - 100
            self.earth = 100
        if self.fire > 100:
            remainder.fire = self.fire - 100
            self.fire = 100

        return remainder

    def encode(self, encoder: BitEncoder):
        encoder.write_bits(int(self._water), 8)
        encoder.write_bits(int(self._earth), 8)
        encoder.write_bits(int(self._fire), 8)        
        
    @staticmethod
    def decode(decoder: BitDecoder) -> "PrimaryElementLevels":        
        water = decoder.read_bits(8)
        earth = decoder.read_bits(8)
        fire = decoder.read_bits(8)
        return PrimaryElementLevels(water, earth, fire)

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
        
    @property
    def fire(self) -> int:
        return self._fire

    @fire.setter
    def fire(self, value: int):
        self._fire = max(0, value)

    @property
    def empty(self) -> bool:
        return self._fire == 0 and self._water == 0 and self._earth == 0

    def __str__(self) -> str:
        return f"Elements(fire={self._fire}, water={self._water}, earth={self._earth})"
