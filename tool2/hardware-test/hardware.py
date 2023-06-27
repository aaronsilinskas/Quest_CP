import board
from digitalio import DigitalInOut, Direction, Pull
import pulseio
import busio
import neopixel
from adafruit_led_animation.grid import PixelGrid, VERTICAL
import adafruit_rfm69
import adafruit_lis3dh
import adafruit_drv2605
from mindwidgets_df1201s import DF1201S
from adafruit_debouncer import Debouncer

# TODO wrap this in a class and expose updated values in properties

# Device Configuration


def log(message: str):
    print(message)


log("Device Configuration")

stemma_i2c = board.STEMMA_I2C()

log("..Trigger")
trigger_in = DigitalInOut(board.A1)
trigger_in.direction = Direction.INPUT
trigger_in.pull = Pull.UP
trigger = Debouncer(lambda: not trigger_in.value, interval=0.01)

# HUD
log("..HUD")
hud_pixels = neopixel.NeoPixel(board.D10, 5*5,
                               brightness=0.1, auto_write=False)
hud_pixel_grid = PixelGrid(hud_pixels, width=5, height=5, orientation=VERTICAL, alternating=False, reverse_y=True)

hud_button_a = DigitalInOut(board.D24)
hud_button_a.direction = Direction.INPUT
hud_button_a.pull = Pull.UP

hud_button_b = DigitalInOut(board.D25)
hud_button_b.direction = Direction.INPUT
hud_button_b.pull = Pull.UP

log("..Barrel")
barrel_pixels = neopixel.NeoPixel(board.D5, 12,
                                  brightness=0.25, auto_write=False)

log("..Radio")
radio_chip_select = DigitalInOut(board.RFM_CS)
radio_reset = DigitalInOut(board.RFM_RST)
radio = adafruit_rfm69.RFM69(
    board.SPI(), radio_chip_select, radio_reset, frequency=915.0, high_power=False)
radio.listen()

log("..Accelerometer / IMU")
imu = adafruit_lis3dh.LIS3DH_I2C(stemma_i2c)
imu.range = adafruit_lis3dh.RANGE_4_G
imu.set_tap(1, 100)

log("..Vibrator / Haptic")
vibrator = adafruit_drv2605.DRV2605(stemma_i2c)

log("..Infrared")
ir_pulsein = pulseio.PulseIn(pin=board.A2, maxlen=256, idle_state=True)
ir_pulseout = pulseio.PulseOut(
    pin=board.A3, frequency=38000, duty_cycle=2 ** 15)

log("..DFPlayer Pro")
df_player = DF1201S(busio.UART(tx=board.TX, rx=board.RX, baudrate=115200))
df_player.volume = 0.1
df_player.disable_led()
df_player.disable_prompt()
df_player.enable_amp()
df_player.play_mode = DF1201S.PLAYMODE_PLAY_ONCE


def update():
    trigger.update()
    barrel_pixels.show()
    hud_pixels.show()
