from audiocore import WaveFile
import audiomixer


class Sound(object):
    def __init__(self, audio_out, volume=0.5, voices=1):
        self._audio_out = audio_out
        self._mixer = audiomixer.Mixer(
            voice_count=voices,
            sample_rate=22050,
            channel_count=1,
            bits_per_sample=16,
            samples_signed=True,
        )
        self._master_volume = volume

    def master_volume(self, level):
        self._master_volume = level
        for voice in self._mixer.voice:
            voice.level = level

    def play_file(self, filename, loop=False, voice=0):
        print("playing sound", filename, loop, voice)
        wave_file = WaveFile(open("sounds/" + filename, "rb"))
        if not self._audio_out.playing:
            self._audio_out.play(self._mixer)
        self._mixer.play(wave_file, voice=voice, loop=loop)

    def off(self):
        for i in range(len(self._mixer.voice)):
            self._mixer.stop_voice(i)

    def update(self):
        if self._audio_out is None:
            return

        if not self._mixer.playing and self._audio_out.playing:
            self._audio_out.stop()

    def volume_acceleration(self, voice, acceleration):
        x, y, z = acceleration
        additional_volume = min(0.5, max(0, x * x + y * y + z * z - 1))
        # print("Additional volume: ", additional_volume)
        adjusted_volume = self._master_volume + additional_volume
        self._mixer.voice[voice].level = adjusted_volume
        # print("Adjusted volume: ", adjusted_volume)
