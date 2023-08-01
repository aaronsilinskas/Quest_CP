"""
SpyGame - Base Defense Turret
"""

import time
import board
import touchio

from adafruit_debouncer import Debouncer
import neopixel

from state import Thing, State
from button_knob_input import ButtonKnobInput
from spotlight_pixels import SpotlightPixels

# Design

# - Turret Position
#     - [ ]  ButtonKnobInput - two buttons control rotation, variable speed and acceleration, clamped from 0 → 1
#     - [ ]  CylonPixels - a range of pixels that gradients on both ends, optional wrapping. Background color of black.
# - Turret Thing
#     - [ ]  Ready → Shooting → Reloading
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
    board.NEOPIXEL, 10, brightness=0.1, auto_write=False)

log("..Buttons")
turn_right_in = touchio.TouchIn(board.A1)
turn_right_button = Debouncer(lambda: turn_right_in.value, interval=0.01)
turn_left_in = touchio.TouchIn(board.A6)
turn_left_button = Debouncer(lambda: turn_left_in.value, interval=0.01)
trigger_in = touchio.TouchIn(board.A3)
trigger_button = Debouncer(lambda: trigger_in.value, interval=0.01)


# INPUTS
turret_position = ButtonKnobInput(left=lambda: turn_left_button.value,
                                  right=lambda: turn_right_button.value, max_speed=0.25, acceleration=0.05, deceleration=0.1)
turret_position.on_move.add(lambda event: print("Turret Moved", event))

# OUTPUTS
turret_reticule = SpotlightPixels(
    pixels, color=(0, 255, 0), width=4, wrap=True)

turret_position.on_move.add(lambda event: turret_reticule.update(event[1]))

# MAIN LOOP

last_position: float = 0
last_time = time.monotonic()

while True:
    current_time = time.monotonic()
    ellapsed_time = current_time - last_time
    last_time = current_time

    turn_right_button.update()
    turn_left_button.update()
    trigger_button.update()

    pixels.fill(0)

    turret_position.update(ellapsed_time)

    pixels.show()

    if turn_right_button.rose:
        print("Turn Right Start")
    if turn_right_button.fell:
        print("Turn Right Stop")
    if turn_left_button.rose:
        print("Turn Left Start")
    if turn_left_button.fell:
        print("Turn Left Stop")
    if trigger_button.rose:
        print("Pew Pew")
