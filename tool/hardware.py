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


def digital_in(pin, pull=Pull.DOWN):
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
        self,
        trigger_pin,
        accelerometer_pin=None,
        audio_pin=None,
        ir_out_pin=None,
        ir_in_pin=None,
        ir_in_max_pulses=256,
    ):
        self._trigger = digital_in(trigger_pin, Pull.UP)

        if accelerometer_pin is not None:
            i2c = busio.I2C(board.SCL, board.SDA)
            int1 = DigitalInOut(accelerometer_pin)
            self._accelerometer = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
            print("Accelerometer: ", accelerometer_pin)
        elif hasattr(board, "ACCELEROMETER_SCL"):
            i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
            int1 = DigitalInOut(board.ACCELEROMETER_INTERRUPT)
            self._accelerometer = adafruit_lis3dh.LIS3DH_I2C(
                i2c, address=0x19, int1=int1
            )
            print("Accelerometer: internal")
        else:
            self._accelerometer = None
        if self._accelerometer is not None:
            self._accelerometer.range = adafruit_lis3dh.RANGE_4_G

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

        self._pixels = None
        if hasattr(board, "NEOPIXEL"):
            self._board_pixels = neopixel.NeoPixel(
                board.NEOPIXEL, 10, brightness=0.2, auto_write=False
            )
        else:
            self._board_pixels = None

        self._last_update_time = time.monotonic()

        self._button_a = (
            digital_in(board.BUTTON_A) if hasattr(board, "BUTTON_A") else None
        )
        self._button_b = (
            digital_in(board.BUTTON_B) if hasattr(board, "BUTTON_B") else None
        )
        self._switch = (
            digital_in(board.SLIDE_SWITCH, Pull.UP)
            if hasattr(board, "SLIDE_SWITCH")
            else None
        )

    def setup_pixels_dotstar(self, clock, data, count, brightness):
        self._pixels = adafruit_dotstar.DotStar(
            board.A3, board.A1, 14, brightness=brightness, auto_write=False
        )

    def update(self):
        self._trigger_down = self._trigger.value == 0

        if self._accelerometer is not None:
            self._current_acceleration = [
                value / adafruit_lis3dh.STANDARD_GRAVITY
                for value in self._accelerometer.acceleration
            ]

        if self._button_a is not None:
            self._button_a_down = self._button_a.value == 1
        if self._button_b is not None:
            self._button_b_down = self._button_b.value == 1
        if self._switch is not None:
            self._switch_on = self._switch.value == 0

        current_time = time.monotonic()
        self._ellapsed_time = current_time - self._last_update_time
        self._last_update_time = time.monotonic()

    @property
    def ellapsed_time(self):
        return self._ellapsed_time

    @property
    def trigger_down(self):
        return self._trigger_down

    @property
    def pixels(self):
        return self._pixels

    @property
    def board_pixels(self):
        return self._board_pixels

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

    @property
    def button_a_down(self):
        return self._button_a_down if self._button_a is not None else False

    @property
    def button_b_down(self):
        return self._button_b_down if self._button_b is not None else False

    @property
    def switch_on(self):
        return self._switch_on if self._switch is not None else False
