"""
SpyGame - Base Defense Turret
"""

import board
import touchio

from adafruit_debouncer import Debouncer
import neopixel

from turret_thing import TurretThing

# Design

# - Enemy Transport Thing
#     - [ ]  Spawn (speed, distance, size, hp) → Moving → (Damaged → Destroyed) || Landed
# - Enemy Fighter Thing
#     - [ ]  Spawn (speed, distance, size, hp) → Moving → (Damaged → Destroyed) || Attacking
#     - Missile Thing
# - Enemy Destroyer Thing
#     - [ ]  Spawn (speed, distance, size, hp) → Moving → (Damaged → Shield Down → Shield Up → Destroyed) || Attacking


def log(message: str):
    print(message)


# HARDWARE
log("Hardware Setup")

log("..Pixels")
pixels = neopixel.NeoPixel(
    board.NEOPIXEL, 10, brightness=0.05, auto_write=False)

log("..Buttons")
turn_right_in = touchio.TouchIn(board.A6)
turn_right_button = Debouncer(lambda: turn_right_in.value, interval=0.01)
turn_left_in = touchio.TouchIn(board.A1)
turn_left_button = Debouncer(lambda: turn_left_in.value, interval=0.01)
trigger_in = touchio.TouchIn(board.A3)
trigger_button = Debouncer(lambda: trigger_in.value, interval=0.01)

# THINGS

turret = TurretThing(pixels,
                     turn_left_button=turn_left_button,
                     turn_right_button=turn_right_button,
                     trigger_button=trigger_button)

# MAIN LOOP

while True:
    turn_right_button.update()
    turn_left_button.update()
    trigger_button.update()

    pixels.fill(0)

    turret.update()

    pixels.show()
