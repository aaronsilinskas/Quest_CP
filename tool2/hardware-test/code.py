import time
from digitalio import DigitalInOut, Direction, Pull
import pulseio
import busio
import board
import neopixel
import adafruit_rfm69
import adafruit_lis3dh
import adafruit_drv2605
from mindwidgets_df1201s import DF1201S
from infrared import Infrared

# Pins
PIN_NEOPIXEL = board.D5
PIN_NEOPIXEL_5X5 = board.D10
PIN_DFPLAYER_TX = board.TX
PIN_DFPLAYER_RX = board.RX
PIN_TRIGGER = board.A1
PIN_IR_RECEIVER = board.A2
PIN_IR_TRANSMITTER = board.A3

# Set up Neopixel
NUM_PIXELS = 12  # NeoPixel strip length (in pixels)
strip = neopixel.NeoPixel(PIN_NEOPIXEL, NUM_PIXELS,
                          brightness=0.25, auto_write=False)
hud = neopixel.NeoPixel(PIN_NEOPIXEL_5X5, 5*5,
                          brightness=0.1, auto_write=False)

# Set up Radio
RADIO_FREQ_MHZ = 915.0
radio_chip_select = DigitalInOut(board.RFM_CS)
radio_reset = DigitalInOut(board.RFM_RST)

# Initialise RFM69 radio
radio = adafruit_rfm69.RFM69(
    board.SPI(), radio_chip_select, radio_reset, RADIO_FREQ_MHZ, high_power=False)
radio.listen()

# Set up I2C
i2c = board.STEMMA_I2C()

# Set up accelerometer on I2C bus, 4G range
accel = adafruit_lis3dh.LIS3DH_I2C(i2c)
accel.range = adafruit_lis3dh.RANGE_4_G
accel.set_tap(1, 100)

# Set up vibrator driver
vibrator = adafruit_drv2605.DRV2605(i2c)

# # Set up audio
uart = busio.UART(tx=PIN_DFPLAYER_TX, rx=PIN_DFPLAYER_RX, baudrate=115200)

df_player = DF1201S(uart)
df_player.volume = 0.3
df_player.disable_led()
df_player.disable_prompt()
df_player.enable_amp()
df_player.play_mode = DF1201S.PLAYMODE_PLAY_ONCE

# # Set up IR
ir_pulsein = pulseio.PulseIn(pin=PIN_IR_RECEIVER, maxlen=256, idle_state=True)
ir_pulseout = pulseio.PulseOut(
    pin=PIN_IR_TRANSMITTER, frequency=38000, duty_cycle=2 ** 15)
infrared = Infrared(ir_pulseout, ir_pulsein)

# Set up trigger
trigger = DigitalInOut(PIN_TRIGGER)
trigger.direction = Direction.INPUT
trigger.pull = Pull.UP


###########

pixel_num = 0
pixel_color = (64, 0, 0)
hud_y = 0

while True:
    if trigger.value == 0:
        print("Trigger")
        pulses = b"Hello!"
        infrared.send(pulses)
        df_player.play_next()
        vibrator.sequence[0] = adafruit_drv2605.Effect(83)
        vibrator.sequence[1] = adafruit_drv2605.Effect(37)
        vibrator.sequence[2] = adafruit_drv2605.Effect(74)
        vibrator.play()

    ir_received = infrared.receive()
    if ir_received is not None:
        data, strength = ir_received
        print("IR Data Received: ", data.decode("utf-8"), strength)

    if radio.payload_ready():
        radio_received = radio.receive(keep_listening=True)
        print("Radio Data Received: ",
              radio_received.decode("utf-8"), radio.last_rssi)

    strip[pixel_num] = pixel_color
    pixel_num = pixel_num + 1
    if pixel_num >= NUM_PIXELS:
        pixel_num = 0
        if pixel_color == 0:
            pixel_color = (64, 0, 0)
        else:
            pixel_color = 0
    strip.show()

    hud.fill(0)
    hud_pixel = hud_y * 5
    for p in range(hud_pixel, hud_pixel + 5):
        hud[p] = (0,0,255)
    hud.show()
    hud_y += 1
    if hud_y > 4:
        hud_y = 0

    x, y, z = accel.acceleration
    print(x, y, z)
    if accel.tapped:
        print("Tapped!")

    time.sleep(0.2)
