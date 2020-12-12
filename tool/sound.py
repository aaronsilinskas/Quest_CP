from audiocore import WaveFile
import audiomixer


class Sound(object):
    def __init__(self, audio_out, volume = 0.5):
        self._audio_out = audio_out
        self._mixer = audiomixer.Mixer(
            voice_count=1,
            sample_rate=22050,
            channel_count=1,
            bits_per_sample=16,
            samples_signed=True,
        )
        self._master_volume = volume

    def master_volume(self, level):
        self._master_volume = level
        self._mixer.voice[0].level = level

    def play_file(self, filename, loop=False):
        print("playing sound", filename)
        wave_file = WaveFile(open("sounds/" + filename, "rb"))
        self._audio_out.play(self._mixer)
        self._mixer.play(wave_file, voice=0, loop=loop)

    def off(self):
        self._mixer.stop_voice(0)

    def update(self, acceleration):
        if acceleration is not None:
            x, y, z = acceleration
            additional_volume = min(0.5, max(0, x * x + y * y + z * z - 1))
            #print("Additional volume: ", additional_volume)

            self._mixer.voice[0].level = self._master_volume + additional_volume
            # print("Adjusted volume: ", self._mixer.voice[0].level)

        if not self._mixer.playing and self._audio_out.playing:
            self._audio_out.stop()
