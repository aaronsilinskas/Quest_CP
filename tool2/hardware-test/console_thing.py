from state import Thing, State
from digitalio import DigitalInOut
from button_thing import ButtonThing
from adafruit_led_animation.animation.grid_rain import MatrixRain
from adafruit_led_animation.grid import PixelGrid


class ConsoleThing(Thing):
    def __init__(self, pixel_grid: PixelGrid, button_a: DigitalInOut, button_b: DigitalInOut, logging=False):
        super().__init__(logging)
        self.pixel_grid = pixel_grid
        self.button_a = ButtonThing(lambda: button_a.value == 0)
        self.button_a.on_press.add(lambda: print("Console A Pressed"))
        self.button_b = ButtonThing(lambda: button_b.value == 0)
        self.button_b.on_press.add(lambda: print("Console B Pressed"))
        self.animation = None

        self.go_to_state(ConsoleStates.idle)

    def update(self):
        super().update()
        self.button_a.update()
        self.button_b.update()


class ConsoleStates:
    idle: State


class IdleState(State):
    def enter(self, thing: ConsoleThing):
        thing.animation = MatrixRain(
            thing.pixel_grid, speed=0.1, color=(0, 64, 0), background=(0, 0, 0), count=4, length=4)

    def update(self, thing: ConsoleThing) -> State:
        thing.animation.draw()

        return ConsoleStates.idle


ConsoleStates.idle = IdleState()
