from state_of_things import Thing, State

from adafruit_pixelbuf import PixelBuf
from adafruit_debouncer import Debouncer

from button_knob_input import ButtonKnobInput, ButtonKnobObserver
from spotlight_pixels import SpotlightPixels


class TurretThing(Thing):
    def __init__(self, pixels: PixelBuf, turn_left_button: Debouncer, turn_right_button: Debouncer, trigger_button: Debouncer):
        super().__init__(TurretStates.ready)

        self.position_input = ButtonKnobInput(left=lambda: turn_left_button.value,
                                              right=lambda: turn_right_button.value, max_speed=0.25, acceleration=0.10, deceleration=0.15)
        
        class LoggingKnobObserver(ButtonKnobObserver):
            def knob_moved(self, old_value: float, new_value: float):
                print(f"Turret moved from {old_value} to {new_value}")
        self.position_input.observers.attach(LoggingKnobObserver())
        
        self.trigger_button = trigger_button

        self.turret_reticule = SpotlightPixels(
            pixels, color=(0, 255, 0), width=2, wrap=True)

    def update_inputs(self) -> None:
        self.position_input.update(self.time_ellapsed)


class TurretStates:
    ready: State
    firing: State
    reloading: State
    disabled: State


class TurretReadyState(State):
    def enter(self, thing: TurretThing):
        thing.turret_reticule.color = (0, 255, 0)

    def update(self, thing: TurretThing) -> State:
        if thing.trigger_button.value:
            return TurretStates.firing

        thing.update_inputs()

        thing.turret_reticule.position = thing.position_input.value
        thing.turret_reticule.show()

        return self


TurretStates.ready = TurretReadyState()


class TurretFiringState(State):
    def enter(self, thing: TurretThing):
        print("Pew Pew")
        thing.turret_reticule.color = (255, 255, 255)

    def update(self, thing: TurretThing) -> State:
        thing.turret_reticule.show()

        if thing.time_active > 1:
            return TurretStates.reloading
        return self


TurretStates.firing = TurretFiringState()


class TurretReloadingState(State):
    def enter(self, thing: TurretThing):
        print("Reloading")
        thing.turret_reticule.color = (0, 0, 255)

    def update(self, thing: Thing) -> State:
        thing.turret_reticule.show()

        if thing.time_active > 2:
            return TurretStates.ready
        return self


TurretStates.reloading = TurretReloadingState()
