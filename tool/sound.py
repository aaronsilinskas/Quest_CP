from hardware import audio
from audiocore import WaveFile
import audiomixer

mixer = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=1,
                         bits_per_sample=16, samples_signed=True)

def volume(level):
    mixer.voice[0].level = level

def play_file(filename, loop=False):
    print("playing sound", filename)
    wave_file = WaveFile(open('sounds/' + filename, "rb"))
    audio.play(mixer)
    mixer.play(wave_file, voice=0, loop=loop)

def sound_off():
    mixer.stop_voice(0)    

def sound_cleanup():
    if not mixer.playing and audio.playing:
        audio.stop()

def play_cast():
    play_file("hit.wav")

def play_weaved():
    play_file("on.wav")

def play_active():
    play_file("idle.wav", loop=True)

