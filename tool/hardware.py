import board
from digitalio import DigitalInOut, Direction, Pull
import time
import busio
import pwmio
import pulseio
import neopixel
import adafruit_lis3dh
import adafruit_dotstar

try:
    from audioio import AudioOut
except ImportError:
    from audiopwmio import PWMAudioOut as AudioOut


def digital_in(pin, pull):
    input = DigitalInOut(pin)
    input.direction = Direction.INPUT
    input.pull = pull
    return input


def digital_out(pin, value=False):
    output = DigitalInOut(pin)
    output.direction = Direction.OUTPUT
    output.value = value
    return output


class Hardware(object):
    def __init__(
        self, audio_pin=None, ir_out_pin=None, ir_in_pin=None, ir_in_max_pulses=256
    ):
        if audio_pin is not None:
            self._audio = AudioOut(audio_pin)
            print("Audio: ", audio_pin)
        elif hasattr(board, "SPEAKER"):
            digital_out(board.SPEAKER_ENABLE, True)
            self._audio = AudioOut(board.SPEAKER)
        else:
            self._audio = None

        if ir_out_pin is not None:
            self._ir_pwmout = pwmio.PWMOut(
                ir_out_pin, frequency=38000, duty_cycle=2 ** 15
            )
            self._ir_pulseout = pulseio.PulseOut(self._ir_pwmout)
            print("Infrared Output: ", ir_out_pin)
        if ir_in_pin is not None:
            self._ir_pulsein = pulseio.PulseIn(
                ir_in_pin, maxlen=ir_in_max_pulses, idle_state=True
            )
            print("Infrared Input: ", ir_in_pin)
            print("Infrared Max Pulses: ", ir_in_max_pulses)

        self._accelerometer = None
        self._pixels = {}
        self._buttons = {}
        self._switches = {}

        self._last_update_time = time.monotonic()

    def setup_lis3dh(self, interrupt_pin, range=adafruit_lis3dh.RANGE_4_G):
        i2c = busio.I2C(board.SCL, board.SDA)
        int1 = DigitalInOut(interrupt_pin)
        self._accelerometer = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
        self._accelerometer.range = range
        print("Accelerometer: ", interrupt_pin)

    def setup_onboard_lis3dh(self, range=adafruit_lis3dh.RANGE_4_G):
        i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
        int1 = DigitalInOut(board.ACCELEROMETER_INTERRUPT)
        self._accelerometer = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19, int1=int1)
        self._accelerometer.range = range
        print("Accelerometer: internal")

    def setup_neopixels(self, name, data, count, brightness):
        pixels = neopixel.NeoPixel(data, count, brightness=brightness, auto_write=False)
        self._pixels[name] = pixels

    def setup_dotstars(self, name, clock, data, count, brightness):
        pixels = adafruit_dotstar.DotStar(
            clock, data, count, brightness=brightness, auto_write=False
        )
        self._pixels[name] = pixels

    def setup_button(self, name, pin, pull):
        self._buttons[name] = digital_in(pin, pull)

    def setup_switch(self, name, pin, pull):
        self._switches[name] = digital_in(pin, pull)

    def update(self):
        if self._accelerometer is not None:
            self._current_acceleration = [
                value / adafruit_lis3dh.STANDARD_GRAVITY
                for value in self._accelerometer.acceleration
            ]

        current_time = time.monotonic()
        self._ellapsed_time = current_time - self._last_update_time
        self._last_update_time = time.monotonic()

    @property
    def ellapsed_time(self):
        return self._ellapsed_time

    @property
    def pixels(self):
        return self._pixels

    @property
    def current_acceleration(self):
        return self._current_acceleration if self._accelerometer else None

    @property
    def audio(self):
        return self._audio

    @property
    def ir_pulseout(self):
        return self._ir_pulseout

    @property
    def ir_pulsein(self):
        return self._ir_pulsein

    def button_down(self, name):
        button = self._buttons[name]
        on = 0 if button.pull == Pull.UP else 1
        return button.value == on

    def switch_on(self, name):
        switch = self._switches[name]
        on = 0 if switch.pull == Pull.UP else 1
        return switch.value == on
