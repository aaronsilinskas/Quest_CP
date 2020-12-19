import board
import time
from digitalio import Pull
from hardware import Hardware
from sound import Sound
from spell import receive_spell
from lights import draw_hitpoints
from infrared import Infrared
from player import Player


hw = Hardware()

hw.setup_neopixels("health", data=board.NEOPIXEL, count=10, brightness=0.2)

hw.setup_onboard_audio()
sound = Sound(hw.audio, voices=2, volume=0.2)

hw.setup_ir_in(board.D0)
hw.setup_ir_out(board.D1)
infrared = Infrared(hw.ir_pulseout, hw.ir_pulsein)

hw.setup_button("A", board.BUTTON_A, Pull.DOWN)
hw.setup_button("B", board.BUTTON_B, Pull.DOWN)
hw.setup_switch("switch", board.SLIDE_SWITCH, Pull.UP)

player = Player(team=1)

while True:
    hw.update()

    ellapsed_time = hw.ellapsed_time

    player.update(ellapsed_time)

    draw_hitpoints(hw.pixels["health"], player.hitpoints, player.max_hitpoints)
    hw.pixels["health"].show()

    if hw.button_down("A"):
        infrared.send([0b11111111, 0b01010101, 0b11001100, 0b00000000])
        time.sleep(0.5)

    received = infrared.receive()
    if received is not None:
        data, margin = received
        print("IR Data Received: ", data, margin)

        if receive_spell(data, player):
            sound.play_file("hit.wav", loop=False, voice=1)
        # add other receivers that'll handle different events

    sound.update()
