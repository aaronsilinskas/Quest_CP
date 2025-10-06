# SPDX-FileCopyrightText: 2023 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import board
import digitalio
from encoder import EVENT_SPELL, BitEncoder
from fixtures import HardcodedWeavingObserver, LoggingWeavingObserver
import pulseio
import keypad
import audiomixer
import audiobusio
import audiocore
import neopixel
from adafruit_debouncer import Debouncer
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation.animation.sparklepulse import SparklePulse
import adafruit_lis3dh
from spell.weaving_thing import WeavingThing
from spell.spell import Spell, SpellPurpose
from spell.weaving import WeavingPosition
from state_of_things import ThingObserver
from infrared import Infrared
from player import Player
from spell.aura import Aura, SpellCast, SpellHit
from spell.spell_color import color_for_element, color_for_shape
from spell.aura_shape import modify_aura

# I2C
i2c = board.I2C()

# Sound Hardware Setup
SOUND_FILE = "FinalFantasy.wav"

power = digitalio.DigitalInOut(board.EXTERNAL_POWER)
power.switch_to_output(value=True)

keys = keypad.Keys((board.BUTTON,), value_when_pressed=False)

i2s = audiobusio.I2SOut(board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA)
music = audiocore.WaveFile(SOUND_FILE)
# NOTE: Must set buffer size to a large number to avoid noise when I2C is used. This prevents I2S from running out of data when I2C is busy.
mixer = audiomixer.Mixer(
    buffer_size=4096,
    voice_count=1,
    sample_rate=music.sample_rate,
    channel_count=1,
    bits_per_sample=music.bits_per_sample,
    samples_signed=True,
)
mixer.voice[0].level = 0.2

# NeoPixel Setup
num_pixels = 75
pixels = neopixel.NeoPixel(board.EXTERNAL_NEOPIXELS, num_pixels)
pixels.brightness = 0.1

# IMU Setup
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c)
lis3dh.range = adafruit_lis3dh.RANGE_2_G

# Infrared Setup
ir_pulsein = pulseio.PulseIn(board.D10, maxlen=256, idle_state=True)
# ir_pwmout = pwmio.PWMOut(board.D9, frequency=38000, duty_cycle=2**15)
ir_pulseout = pulseio.PulseOut(board.D9, frequency=38000, duty_cycle=2**15)
aoe_ir_pulseout = pulseio.PulseOut(board.D11, frequency=38000, duty_cycle=2**15)
infrared = Infrared(ir_pulseout, ir_pulsein)

# Trigger Setup
trigger_pin = digitalio.DigitalInOut(board.EXTERNAL_BUTTON)
trigger_pin.direction = digitalio.Direction.INPUT
trigger_pin.pull = digitalio.Pull.UP
trigger = Debouncer(trigger_pin)

# Sound State
sound = False
last_pot = 0
i2s.play(mixer)

# IMU State
last_imu_log = time.monotonic()

# Player and Weaving State
weaving = WeavingThing(starting_level=3)
player = Player(id=1, party_id=1)


weaving.observers.attach(LoggingWeavingObserver())


class LEDAnimationWeavingObserver(ThingObserver):
    animation: AnimationSequence = None

    def _set_animation(self, color):
        # reduce the color to half brightness
        starting_color = (color[0] // 2, color[1] // 2, color[2] // 2)
        pixels.fill(starting_color)
        self.animation = SparklePulse(
            pixels, speed=0.05, color=color, period=2, breath=0, min_intensity=0.2
        )

    def spell_selected(self, thing: WeavingThing, spell: Spell):
        self._set_animation(color_for_element(spell.element).color)

    def shape_selected(self, thing: WeavingThing, spell: Spell):
        self._set_animation(color_for_shape(spell.shape).color)

    def spell_ready(self, thing: WeavingThing, spell: Spell):
        self._set_animation(color_for_element(spell.element).color)

    def spell_cast(self, thing: WeavingThing, spell: Spell):
        pass


animation_observer = LEDAnimationWeavingObserver()
weaving.observers.attach(animation_observer)


class InfraredWeavingObserver(ThingObserver):
    def spell_cast(self, thing: WeavingThing, spell: Spell):
        print("Player aura: ", player.aura.levels)
        cast = SpellCast(spell)
        player.aura.modify_cast(cast)
        print("Modified cast: ", cast.levels)

        encoder = BitEncoder()
        encoder.add_event(EVENT_SPELL)
        player.encode_ids(encoder)
        cast.encode(encoder)

        encoded_bytes = encoder.to_bytes()
        print("SpellCast encoded bytes: ", [bin(b) for b in encoded_bytes])
        infrared.send(encoded_bytes)


weaving.observers.attach(InfraredWeavingObserver())

weaving.observers.attach(HardcodedWeavingObserver(player))

last_tick = time.monotonic()

while True:
    elapsed_time = time.monotonic() - last_tick
    last_tick = time.monotonic()

    if sound and not mixer.voice[0].playing:
        print("Playing now!")
        mixer.voice[0].play(music)

    event = keys.events.get()
    if event and event.pressed:
        print("click")
        sound = not sound
        mixer.voice[0].stop()

    if animation_observer.animation:
        animation_observer.animation.animate()

    x, y, z = [
        value / adafruit_lis3dh.STANDARD_GRAVITY for value in lis3dh.acceleration
    ]

    # if last_imu_log + 1 < time.monotonic():
    #     last_imu_log = time.monotonic()
    #     print(f"x = {x:.3f} G, y = {y:.3f} G, z = {z:.3f} G")

    trigger.update()

    weaving.trigger_pressed = not trigger.value
    weaving.current_position = WeavingPosition.from_accelerometer(x, y, z)
    weaving.update()

    received = infrared.receive()
    if received is not None:
        data, margin = received
        print("IR Data Received: ", [hex(b) for b in data], margin)

    player.update(elapsed_time)
