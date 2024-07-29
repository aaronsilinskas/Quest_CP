
from state_of_things import Thing, State
import neopixel
from adafruit_led_animation.animation.comet import Comet


class BarrelThing(Thing):
    def __init__(self, pixels: neopixel.NeoPixel):
        super().__init__(BarrelStates.idle)
        self.pixels = pixels
        self.animation = None


class BarrelStates:
    idle: State


class IdleState(State):
    def enter(self, thing: BarrelThing):
        thing.animation = Comet(
            thing.pixels, speed=0.1, color=(16, 16, 16), tail_length=round(thing.pixels.n / 3), bounce=True)

    def update(self, thing: BarrelThing) -> State:
        thing.animation.draw()
        return BarrelStates.idle


BarrelStates.idle = IdleState()
