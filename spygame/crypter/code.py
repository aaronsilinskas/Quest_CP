"""
Crypter - a crypto key and descrambler game for the Adafruit MACROPAD.
"""

import random
import displayio
import terminalio
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
from adafruit_macropad import MacroPad
from adafruit_led_animation.animation.sparklepulse import SparklePulse
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation import helper
from state_of_things import State, Thing

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

# Secret messages and their color->key combinations
INITIAL_COLOR = RED
MESSAGE_CHARS = r"""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
MAX_ENCODER_DISTANCE = 24

# Clue Format: <message>, [(<color>, <expected key>), ...]
CLUE1 = ("12 Guests For Dinner", [(BLUE, 5), (GREEN, 3), (YELLOW, 0)])
CLUE2 = ("Shoot Dirty", [(GREEN, 1), (PURPLE, 11), (WHITE, 3)])
CLUE3 = ("Hippos Bite!", [(YELLOW, 4), (PURPLE, 9), (GREEN, 0), (BLUE, 10)])
CLUE4 = ("Sew a Diamond", [(CYAN, 6), (GREEN, 10), (BLUE, 0), (PURPLE, 1)])
CLUE5 = ("Gru's Crew", [(PURPLE, 4), (BLUE, 5), (GREEN, 0), (WHITE, 11)])
CLUE6 = ("A. Three Sticks", [(WHITE, 8), (GREEN, 5), (PURPLE, 11), (BLUE, 3)])
CLUE7 = ("Smelly Shell", [(BLUE, 0), (WHITE, 4), (PURPLE, 2), (GREEN, 11)])
CLUE8 = ("What Fun It Is To Ride", [(GREEN, 11), (PURPLE, 10), (BLUE, 1), (YELLOW, 3)])
CLUE9 = ("Scan And Ink", [(YELLOW, 8), (PURPLE, 0), (CYAN, 3), (BLUE, 11)])
CLUE10 = (
    "Deepest Dark Corner",
    [(BLUE, 0), (GREEN, 4), (PURPLE, 6), (WHITE, 1), (YELLOW, 8), (CYAN, 10)],
)

# Clues Format: <initial key> -> <clue>
CLUES = {
    2: CLUE1,
    5: CLUE2,
    11: CLUE3,
    0: CLUE4,
    3: CLUE5,
    7: CLUE6,
    9: CLUE7,
    6: CLUE8,
    1: CLUE9,
    8: CLUE10,
}

# HARDWARE INITIALIZATION

macropad = MacroPad()
macropad.display.auto_refresh = False
macropad.pixels.brightness = 128
macropad.pixels.auto_write = False

display_group = displayio.Group()
macropad.display.root_group = display_group
display_group.append(Rect(0, 0, macropad.display.width, 12, fill=0xFFFFFF))
display_group.append(
    label.Label(
        terminalio.FONT,
        text="Crypter",
        color=0x000000,
        anchored_position=(macropad.display.width // 2, -2),
        anchor_point=(0.5, 0.0),
    )
)

for text_index in range(1, 6):
    display_group.append(
        label.Label(
            terminalio.FONT,
            text="",
            color=0xFFFFFF,
            anchored_position=(0, 10 * text_index),
            anchor_point=(0.0, 0.0),
        )
    )

keypadAnimation = SparklePulse(macropad.pixels, speed=0.05, period=2, color=RED)
messageAnimation = RainbowComet(
    helper.PixelSubset(macropad.pixels, 9, 12), speed=0.1, tail_length=8, bounce=True
)
failedAnimation = Comet(
    macropad.pixels, speed=0.05, color=YELLOW, tail_length=3, bounce=True
)

# STATE MACHINE


class CrypterThing(Thing):
    def __init__(self, initial_state: State):
        super().__init__(initial_state)

        # booting
        self.dot_group = 0

        # selected clue
        self.clue_message = None
        self.clue_key_colors = []

        # clue key entry
        self.expected_key = 0
        self.keycode_index = 0

        # message decrypt
        self.encoder_start = 0
        self.encoder_offset_desired = 0


class CrypterStates:
    booting: State
    ready: State
    keycoding: State
    failed: State
    message: State


class Booting(State):
    def enter(self, thing: CrypterThing):
        display_group[2].text = "Entangling Atoms"
        thing.dot_group = 3

    def update(self, thing: CrypterThing):
        num_dots = int((thing.time_active % 1) * 20)
        display_group[thing.dot_group].text = "." * num_dots
        if thing.time_active > 1:
            display_group[3].text = "Linking Quantum Net"
            thing.dot_group = 4
        if thing.time_active > 2:
            display_group[4].text = "Activating Defenses"
            thing.dot_group = 5
        if thing.time_active > 3:
            return CrypterStates.ready
        return self


CrypterStates.booting = Booting()


class Ready(State):
    def enter(self, thing: CrypterThing):
        for i in range(2, 7):
            display_group[i].text = ""

        macropad.pixels.brightness = 0.75
        macropad.pixels.fill(BLACK)
        keypadAnimation.color = INITIAL_COLOR

    def update(self, thing: CrypterThing):
        event = macropad.keys.events.get()
        if event and event.pressed:
            key_number = event.key_number
            if key_number in CLUES:
                message, key_colors = CLUES[key_number]
                # print("Start clue ", message, key_colors)

                thing.clue_message = message
                thing.clue_key_colors = key_colors

                return CrypterStates.keycoding

        keypadAnimation.animate()
        macropad.pixels.show()

        return self


CrypterStates.ready = Ready()


class Keycoding(State):
    def enter(self, thing: CrypterThing):
        color, expected_key = thing.clue_key_colors[0]

        thing.keycode_index = 0
        thing.expected_key = expected_key

        keypadAnimation.color = color

    def update(self, thing: CrypterThing):
        event = macropad.keys.events.get()
        if event and event.pressed:
            key_number = event.key_number
            if key_number != thing.expected_key:
                return CrypterStates.failed

            thing.keycode_index = thing.keycode_index + 1
            if thing.keycode_index == len(thing.clue_key_colors):
                return CrypterStates.message

            next_color, next_key = thing.clue_key_colors[thing.keycode_index]
            thing.expected_key = next_key
            keypadAnimation.color = next_color

        keypadAnimation.animate()
        macropad.pixels.show()

        return self


CrypterStates.keycoding = Keycoding()


class Failed(State):
    def enter(self, thing: CrypterThing):
        display_group[2].text = "Unauthorized Access"
        display_group[3].text = "Detected"
        display_group[5].text = "Resetting..."

        macropad.pixels.brightness = 0.1

    def update(self, thing: CrypterThing):
        if thing.time_active > 3:
            return CrypterStates.ready

        failedAnimation.animate()
        macropad.pixels.show()

        return self


CrypterStates.failed = Failed()


class Message(State):
    def _update_message(self, thing: CrypterThing):
        encoder_delta = (
            abs(thing.encoder_start - macropad.encoder) % MAX_ENCODER_DISTANCE
        )
        rotated = abs(encoder_delta - thing.encoder_offset_desired)
        encoded_message = ""
        for c in thing.clue_message:
            encoded_message = (
                encoded_message
                + MESSAGE_CHARS[(MESSAGE_CHARS.find(c) + rotated) % len(MESSAGE_CHARS)]
            )

        display_group[2].text = encoded_message
        # display_group[5].text = str(rotated)
        display_group[6].text = str(encoder_delta)

    def enter(self, thing: CrypterThing):
        thing.encoder_start = macropad.encoder
        thing.encoder_offset_desired = random.randint(8, MAX_ENCODER_DISTANCE - 1)

        self._update_message(thing)

        macropad.pixels.brightness = 0.05
        macropad.pixels.fill(BLACK)
        macropad.pixels.show()

    def update(self, thing: CrypterThing):
        self._update_message(thing)

        event = macropad.keys.events.get()
        if event and event.pressed:
            return CrypterStates.ready

        messageAnimation.animate()
        macropad.pixels.show()

        return self


CrypterStates.message = Message()


# MAIN LOOP

crypter = CrypterThing(CrypterStates.booting)

while True:
    crypter.update()

    macropad.display.refresh()
