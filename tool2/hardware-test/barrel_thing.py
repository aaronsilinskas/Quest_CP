
from state import Thing, State
import neopixel
from adafruit_led_animation.animation.comet import Comet


class BarrelThing(Thing):
    def __init__(self, pixels: neopixel.NeoPixel, logging=False):
        super().__init__(logging)
        self.pixels = pixels
        self.animation = None

        self.go_to_state(BarrelStates.idle)


class BarrelStates:
    idle: State


class IdleState(State):
    def enter(self, thing: BarrelThing):
        thing.animation = Comet(
            thing.pixels, speed=0.05, color=(16, 16, 16), tail_length=round(thing.pixels.n / 3), bounce=True)

    def update(self, thing: BarrelThing) -> State:
        thing.animation.draw()
        return BarrelStates.idle


BarrelStates.idle = IdleState()
