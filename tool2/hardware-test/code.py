import time
import hardware
from infrared import Infrared
import adafruit_drv2605
from button_thing import ButtonThing
from infrared_listeners import InfraredListeners
from barrel_thing import BarrelThing
from console_thing import ConsoleThing


###########

infrared = Infrared(hardware.ir_pulseout, hardware.ir_pulsein, logging=True)
infrared_listeners = InfraredListeners(infrared)
infrared_listeners.on_receive.add(lambda event: print(
    "IR Data Received: ", event[0].decode("utf-8"), event[1]))

trigger = ButtonThing(
    predicate=lambda: hardware.trigger.value, enable_logging=True)
trigger.on_press.add(lambda: print("Trigger"))
trigger.on_press.add(lambda: infrared.send(b"Hello!"))
trigger.on_press.add(lambda: hardware.df_player.play_next())


def shoot_vibration():
    hardware.vibrator.sequence[0] = adafruit_drv2605.Effect(83)
    hardware.vibrator.sequence[1] = adafruit_drv2605.Effect(37)
    hardware.vibrator.sequence[2] = adafruit_drv2605.Effect(74)
    hardware.vibrator.play()


trigger.on_press.add(shoot_vibration)

barrel = BarrelThing(hardware.barrel_pixels)
console = ConsoleThing(hardware.hud_pixel_grid,
                       button_a=hardware.hud_button_a, 
                       button_b=hardware.hud_button_b)

while True:
    hardware.update()

    trigger.update()
    infrared_listeners.update()
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

    time.sleep(0.1)
