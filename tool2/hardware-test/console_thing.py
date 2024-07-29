from state_of_things import Thing, State
from digitalio import DigitalInOut
from button_thing import ButtonThing, ButtonObserver
from adafruit_led_animation.animation.grid_rain import RainbowRain
from adafruit_led_animation.grid import PixelGrid


class ConsoleButtonObserver(ButtonObserver):
    def on_press(self, button: Thing):
        print(f"{button.name} pressed")
        
    
class ConsoleThing(Thing):
    def __init__(self, pixel_grid: PixelGrid, button_a: DigitalInOut, button_b: DigitalInOut):
        super().__init__(ConsoleStates.idle)
        self.pixel_grid = pixel_grid
        self.button_a = ButtonThing(lambda: button_a.value == 0, name="Console A")
        self.button_a.observers.attach(ConsoleButtonObserver())
        self.button_b = ButtonThing(lambda: button_b.value == 0, name="Console B")
        self.button_b.observers.attach(ConsoleButtonObserver())        
        self.animation = None

    def update(self):
        super().update()
        self.button_a.update()
        self.button_b.update()


class ConsoleStates:
    idle: State


class IdleState(State):
    def enter(self, thing: ConsoleThing):
        thing.animation = RainbowRain(
            thing.pixel_grid, speed=0.1, background=(0, 0, 0), count=4, length=4)

    def update(self, thing: ConsoleThing) -> State:
        thing.animation.draw()

        return ConsoleStates.idle


ConsoleStates.idle = IdleState()
