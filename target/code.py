import board
from hardware import Hardware
from sound import Sound
from spell import receive_spell
from lights import SPELL_COLORS
from infrared import Infrared


hw = Hardware()

hw.setup_neopixels("hit", data=board.NEOPIXEL, count=10, brightness=0.2)

hw.setup_onboard_audio()
sound = Sound(hw.audio, voices=1, volume=0.2)

hw.setup_ir_in(board.D0)
hw.setup_ir_out(board.D1)
infrared = Infrared(hw.ir_pulseout, hw.ir_pulsein)


def draw_hit(spell, ir_strength):
    pixels = hw.pixels["hit"]
    pixels.fill((0, 0, 0))
    pixels_to_light = round(pixels.n * ir_strength)
    spell_color = SPELL_COLORS[spell.name]
    for index in range(pixels_to_light):
        pixels[index] = spell_color
    pixels.show()


while True:
    hw.update()

    received = infrared.receive()
    if received is not None:
        data, strength = received
        print("IR Data Received: ", data, strength)

        spell_event = receive_spell(data)
        if spell_event:
            spell, team = spell_event
            draw_hit(spell, strength)

            sound.play_file("hit.wav", loop=False, voice=0)

    sound.update()
