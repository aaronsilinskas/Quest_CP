import time
import hardware
from infrared import Infrared
import adafruit_drv2605
from button_thing import ButtonThing, ButtonObserver
from infrared_observers import InfraredObservers, InfraredObserver
from barrel_thing import BarrelThing
from console_thing import ConsoleThing
from state_of_things import State, Thing, ThingObserver


###########

class StateChangeObserver(ThingObserver):
    def state_changed(self, thing: Thing, old_state: State, new_state: State):
        print(f"Thing {thing.name} changed from {old_state.name} to {new_state.name}")

infrared = Infrared(hardware.ir_pulseout, hardware.ir_pulsein, logging=True)

class InfraredLogger(InfraredObserver):
    def on_receive(self, data: bytearray, strength: float):
        print(f"IR Data Received: {data.decode("utf-8")}, {strength}")
        
infrared_observers = InfraredObservers(infrared)
infrared_observers.observers.attach(InfraredLogger())

class TriggerObserver(ButtonObserver):
    def _shoot_vibration(self):
        hardware.vibrator.sequence[0] = adafruit_drv2605.Effect(85)
        hardware.vibrator.sequence[1] = adafruit_drv2605.Effect(37)
        hardware.vibrator.sequence[2] = adafruit_drv2605.Effect(74)
        hardware.vibrator.play()
        
    def on_press(self, button: Thing):
        print("Trigger")
        infrared.send(b"Hello!")
        hardware.df_player.play_next()
        self._shoot_vibration()
        
trigger = ButtonThing(
    predicate=lambda: hardware.trigger.value, name="Trigger")
trigger.observers.attach(StateChangeObserver())
trigger.observers.attach(TriggerObserver())

barrel = BarrelThing(hardware.barrel_pixels)
console = ConsoleThing(hardware.hud_pixel_grid,
                       button_a=hardware.hud_button_a,
                       button_b=hardware.hud_button_b)

while True:
    hardware.update()

    trigger.update()
    infrared_observers.update()
    barrel.update()
    console.update()

    if hardware.radio.payload_ready():
        radio_received = hardware.radio.receive(keep_listening=True)
        print("Radio Data Received: ",
              radio_received.decode("utf-8"), hardware.radio.last_rssi)

    # x, y, z = hardware.imu.acceleration
    # print(x, y, z)
    if hardware.imu.tapped:
        print("Tapped!")

    time.sleep(0.05)
