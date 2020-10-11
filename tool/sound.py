from hardware import audio
import time
from audiocore import WaveFile
# import audiomixer

def play_file(filename):
    wave_file = WaveFile(open(filename, "rb"))
    audio.play(wave_file)

def play_cast():
    play_file("dip.wav")

def play_weave_complete():
    play_file("rise.wav")