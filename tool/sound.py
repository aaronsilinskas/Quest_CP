from audiocore import WaveFile
import audiomixer


class Sound(object):
    def __init__(self, audio_out):
        self._audio_out = audio_out
        self._mixer = audiomixer.Mixer(
            voice_count=1,
            sample_rate=22050,
            channel_count=1,
            bits_per_sample=16,
            samples_signed=True,
        )

    def volume(self, level):
        self._mixer.voice[0].level = level

    def play_file(self, filename, loop=False):
        print("playing sound", filename)
        wave_file = WaveFile(open("sounds/" + filename, "rb"))
        self._audio_out.play(self._mixer)
        self._mixer.play(wave_file, voice=0, loop=loop)

    def off(self):
        self._mixer.stop_voice(0)

    def cleanup(self):
        if not self._mixer.playing and self._audio_out.playing:
            self._audio_out.stop()
