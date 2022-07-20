#

"""
Multi-Key
Search Mode (switch off) - lights up more LEDs as signal from other keys becomes stronger
Transmit Mode (switch on) - broadcasts a signal that Search Mode can detect
- Unlock Mode - (click A and B while switch is on) - Start the unlock sequence
"""

import time
import random
from adafruit_circuitplayground.bluefruit import cpb

from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor

from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.animation.rainbowcomet import RainbowComet

from state import StateContext, State, StateMachine

# CONFIGURATION

# Colors
WHITE = 0xFFFFFF
BLACK = 0x000000
RED = 0xFF0000
YELLOW = 0xFFFF00
GREEN = 0x00FF00
BLUE = 0x0000FF
PURPLE = 0x800080
CYAN = 0x00FFFF

COLORS = [WHITE, RED, YELLOW, GREEN, BLUE, PURPLE, CYAN]

scanAnimation = Comet(cpb.pixels, speed=0.01,
                      color=0x333333, tail_length=5, bounce=True)
unlockSelectAnimation = Comet(cpb.pixels, speed=0.05,
                              color=RED, tail_length=7, bounce=False)
unlockFailedAnimation = Comet(cpb.pixels, speed=0.02,
                              color=YELLOW, tail_length=9, bounce=False)
unlockStartingAnimation = RainbowComet(
    cpb.pixels, speed=0.1, tail_length=7, bounce=False)
unlockedAnimation = RainbowSparkle(
    cpb.pixels, speed=0.1, period=5, num_sparkles=8)

unlock_order = [(1, BLUE), (3, PURPLE), (2, GREEN), (1, YELLOW),
                (2, WHITE), (1, CYAN), (3, RED), (2, WHITE), (3, BLUE)]

# HARDWARE INITIALIZATION
ble = BLERadio()

advertisement = AdafruitColor()
advertisement.color = BLUE

cpb.pixels.auto_write = False
cpb.pixels.brightness = 0.1
cpb.pixels.fill(0)

# STATE MACHINE


class MultiKeyContext(StateContext):
    def __init__(self):
        super().__init__()

        # global
        self.previous_brightness = 0

        # search mode
        self.closest_address = None
        self.closest_last_time = 0
        self.closest_rssi = 0

        # unlock
        self.time_held = 0
        self.last_selected_lock = 0
        self.selected_lock = 0
        self.current_order_index = 0
        self.current_lock = 0
        self.correct_button = ''


class States:
    search: State
    transmit: State
    unlock_wait: State
    unlock_select: State
    unlocking: State
    unlocked_starting: State
    unlocked: State
    unlock_failed: State


class Search(State):
    def enter(self, context: MultiKeyContext):
        context.closest_address = None
        context.closest_last_time = 0
        context.closest_rssi = -100

    def update(self, context: MultiKeyContext):
        if cpb.switch:
            return States.transmit

        for entry in ble.start_scan(AdafruitColor, minimum_rssi=-100, timeout=1):
            if cpb.switch:
                break

            now = time.monotonic()
            if entry.address == context.closest_address:
                pass
            elif entry.rssi > context.closest_rssi or now - context.closest_last_time > 0.4:
                context.closest_address = entry.address
            else:
                continue

            context.closest_rssi = entry.rssi
            context.closest_last_time = now
            discrete_strength = min((100 + entry.rssi) // 5, 10)
            cpb.pixels.fill(BLACK)
            for i in range(0, discrete_strength):
                cpb.pixels[i] = entry.color
            cpb.pixels.show()

        now = time.monotonic()
        if now - context.closest_last_time > 1:
            cpb.pixels.fill(BLACK)
            scanAnimation.animate()
            cpb.pixels.show()
        ble.stop_scan()

        return self


States.search = Search()


class Transmit(State):
    def enter(self, context: MultiKeyContext):
        cpb.pixels.fill(0)
        cpb.pixels.show()

    def update(self, context: MultiKeyContext):
        if not cpb.switch:
            return States.search
        if cpb.button_a and cpb.button_b:
            return States.unlock_wait

        ble.start_advertising(advertisement)
        time.sleep(0.5)
        ble.stop_advertising()

        return self


States.transmit = Transmit()


class UnlockWait(State):
    def enter(self, context: MultiKeyContext):
        pass

    def update(self, context: MultiKeyContext):
        if not cpb.button_a and not cpb.button_b:
            return States.unlock_select
        return self


States.unlock_wait = UnlockWait()


class UnlockSelect(State):
    def enter(self, context: MultiKeyContext):
        context.time_held = 0
        context.last_selected_lock = 0

    def update(self, context: MultiKeyContext):
        if cpb.button_a or cpb.button_b:
            selected_lock = 0
            if (cpb.button_a):
                selected_lock |= 1
            if (cpb.button_b):
                selected_lock |= 2

            if context.last_selected_lock != selected_lock:
                context.last_selected_lock = selected_lock
                context.time_held = 0
                return self

            context.time_held += context.time_ellapsed
            percent_done = context.time_held / 2
            if percent_done > 1:
                context.selected_lock = selected_lock
                while cpb.button_a or cpb.button_b:
                    True
                return States.unlocking

            pixels_to_light = int(percent_done * cpb.pixels.n)
            cpb.pixels.fill(BLACK)
            for i in range(0, pixels_to_light):
                cpb.pixels[i] = GREEN
            cpb.pixels.show()
        else:
            context.time_held = 0
            unlockSelectAnimation.animate()
            cpb.pixels.show()

        return self


States.unlock_select = UnlockSelect()


class Unlocking(State):
    def enter(self, context: MultiKeyContext):
        context.current_order_index = 0
        context.current_lock = 0

        print("Selected Lock: ", context.selected_lock)

        cpb.pixels.fill(BLACK)
        cpb.pixels.show()

    def update(self, context: MultiKeyContext):
        active_lock, active_color = unlock_order[context.current_order_index]
        if (context.current_lock != active_lock):
            context.current_lock = active_lock
            if active_lock == context.selected_lock:
                cpb.pixels.fill(active_color)
                cpb.pixels.show()
            else:
                context.correct_button = random.choice(['a', 'b'])
                other_color = random.choice(COLORS)
                while other_color == active_color:
                    other_color = random.choice(COLORS)
                half_of_pixels = int(cpb.pixels.n / 2)
                for i in range(0, half_of_pixels):
                    cpb.pixels[i] = active_color if context.correct_button == 'a' else other_color
                for i in range(half_of_pixels, cpb.pixels.n):
                    cpb.pixels[i] = active_color if context.correct_button == 'b' else other_color
                cpb.pixels.show()

        if cpb.button_a or cpb.button_b:
            selected_button = 'a' if cpb.button_a else 'b'
            while cpb.button_a or cpb.button_b:
                True
            if active_lock == context.selected_lock or selected_button == context.correct_button:
                context.current_order_index = context.current_order_index + 1
                if context.current_order_index >= len(unlock_order):
                    return States.unlocked_starting
            else:
                return States.unlock_failed

        return self


States.unlocking = Unlocking()


class UnlockedStarting(State):
    def enter(self, context: MultiKeyContext):
        context.previous_brightness = cpb.pixels.brightness

        cpb.pixels.fill(0)
        cpb.pixels.show()

    def update(self, context: MultiKeyContext):
        if context.time_active > 10:
            cpb.pixels.brightness = context.previous_brightness
            return States.unlocked

        cpb.pixels.brightness = context.time_active / 10
        unlockStartingAnimation.speed = max(
            0.01, 0.5 / (1 + int(context.time_active)))
        unlockStartingAnimation.animate()
        cpb.pixels.show()

        return self


States.unlocked_starting = UnlockedStarting()


class Unlocked(State):
    def enter(self, context: MultiKeyContext):
        context.previous_brightness = cpb.pixels.brightness
        cpb.pixels.brightness = 0.05

    def update(self, context: MultiKeyContext):
        if not cpb.switch:
            cpb.pixels.brightness = context.previous_brightness
            return States.search

        unlockedAnimation.animate()
        cpb.pixels.show()

        return self


States.unlocked = Unlocked()


class UnlockFailed(State):

    def update(self, context: MultiKeyContext):
        if context.time_active > 5:
            return States.transmit

        unlockFailedAnimation.animate()
        cpb.pixels.show()

        return self


States.unlock_failed = UnlockFailed()

# MAIN LOOP
state_context = MultiKeyContext()
state_machine = StateMachine()

if cpb.switch:
    state_machine.go_to_state(States.transmit, state_context)
else:
    state_machine.go_to_state(States.search, state_context)

while True:
    state_machine.update(state_context)
