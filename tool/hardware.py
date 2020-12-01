import board
from digitalio import DigitalInOut, Direction, Pull
import busio
import adafruit_lis3dh
import adafruit_dotstar
try:
    from audioio import AudioOut
except ImportError:
    from audiopwmio import PWMAudioOut as AudioOut

def digital_in(pin, pull = Pull.DOWN):
    input = DigitalInOut(pin)
    input.direction = Direction.INPUT
    input.pull = pull
    return input

def digital_out(pin, value = False):
    output = DigitalInOut(pin)
    output.direction = Direction.OUTPUT
    output.value = value
    return output

# Use the CircuitPlayground built-in accelerometer if available,
# otherwise check I2C pins.
if hasattr(board, "ACCELEROMETER_SCL"):
    i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
    int1 = DigitalInOut(board.ACCELEROMETER_INTERRUPT)
    lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19, int1=int1)
else:
    i2c = busio.I2C(board.SCL, board.SDA)
    int1 = DigitalInOut(board.D6)  # Set to correct pin for interrupt!
    lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
lis3dh.range = adafruit_lis3dh.RANGE_4_G


# LEDs
pixels = adafruit_dotstar.DotStar(
    board.A3, board.A1, 14, brightness=0.2, auto_write=False
)

# Audio
if hasattr(board, "SPEAKER"):
    speaker_enable = digital_out(board.SPEAKER_ENABLE, True)

    audio = AudioOut(board.SPEAKER)
else:
    audio = AudioOut(board.A0)

# Trigger
trigger = digital_in(board.A2, Pull.UP)


def measure_acceleration():
    return [value / adafruit_lis3dh.STANDARD_GRAVITY for value in lis3dh.acceleration]


def is_trigger_down():
    return trigger.value == 0
