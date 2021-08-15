import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
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


class Hardware(object):
    def __init__(self):
        self._accelerometer = None
        self._pixels = {}
        self._audio = None
        self._ir_pulsein = None
        self._ir_pulseout = None
        self._buttons = {}
        self._switches = {}
        self._piezos = {}

        self._last_update_time = time.monotonic()

    def _digital_in(self, pin, pull):
        input = DigitalInOut(pin)
        input.direction = Direction.INPUT
        input.pull = pull
        return input

    def _digital_out(self, pin, value=False):
        output = DigitalInOut(pin)
        output.direction = Direction.OUTPUT
        output.value = value
        return output

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
        print("Accelerometer: onboard")

    def setup_neopixels(self, name, data, count, brightness):
        pixels = neopixel.NeoPixel(data, count, brightness=brightness, auto_write=False)
        self._pixels[name] = pixels
        print("Pixels: ", name, data, count)

    def setup_dotstars(self, name, clock, data, count, brightness):
        pixels = adafruit_dotstar.DotStar(
            clock, data, count, brightness=brightness, auto_write=False
        )
        self._pixels[name] = pixels
        print("Dotstars: ", name, data, count)

    def setup_onboard_audio(self):
        self._digital_out(board.SPEAKER_ENABLE, True)
        self._audio = AudioOut(board.SPEAKER)
        print("Audio: onboard")

    def setup_audio(self, pin):
        self._audio = AudioOut(pin)
        print("Audio: ", pin)

    def setup_ir_in(self, pin, max_pulses=256):
        self._ir_pulsein = pulseio.PulseIn(pin, maxlen=max_pulses, idle_state=True)
        print("IR receiver: ", pin, max_pulses)

    def setup_ir_out(self, pin):
        self._ir_pwmout = pwmio.PWMOut(pin, frequency=38000, duty_cycle=2 ** 15)
        self._ir_pulseout = pulseio.PulseOut(self._ir_pwmout)
        print("IR transmitter: ", pin)

    def setup_button(self, name, pin, pull):
        self._buttons[name] = self._digital_in(pin, pull)
        print("Button: ", name, pin, pull)

    def setup_switch(self, name, pin, pull):
        self._switches[name] = self._digital_in(pin, pull)
        print("Switch: ", name, pin, pull)

    def setup_piezo_sensor(self, name, pin):
        self._piezos[name] =  AnalogIn(pin)
        print("Piezo: ", name, pin)

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

    def piezo(self, name):
        piezo = self._piezos[name]
        return piezo.value / 65536
