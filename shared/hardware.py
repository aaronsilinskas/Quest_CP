try:
    from typing import Optional
except ImportError:
    pass
import board
import microcontroller
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
import time
import busio
import pwmio
import touchio
import pulseio
import adafruit_pixelbuf
import neopixel

try:
    import adafruit_lis3dh
except ImportError:
    adafruit_lis3dh = None
try:
    import adafruit_dotstar
except ImportError:
    adafruit_dotstar = None

try:
    from audioio import AudioOut
except ImportError:
    from audiopwmio import PWMAudioOut as AudioOut

try:
    import mindwidgets_df1201s
except ImportError:
    mindwidgets_df1201s = None


class Acceleration(object):
    def __init__(self):
        self.x: float = 0.0
        self.y: float = 0.0
        self.z: float = 0.0


class Hardware(object):
    def __init__(self):
        self._i2c = None
        self._accelerometer = None
        self._current_acceleration: Optional[Acceleration] = None
        self._pixels = {}
        self._audio = None
        self._ir_pulsein = None
        self._ir_pulseout = None
        self._dfplayer = None
        self._buttons = {}
        self._cap_touch = {}
        self._switches = {}
        self._piezos = {}

        self._last_update_time = time.monotonic()

    def _digital_in(self, pin: microcontroller.Pin, pull: Direction):
        input = DigitalInOut(pin)
        input.direction = Direction.INPUT
        input.pull = pull
        return input

    def _digital_out(self, pin: microcontroller.Pin, value: bool = False):
        output = DigitalInOut(pin)
        output.direction = Direction.OUTPUT
        output.value = value
        return output

    def setup_i2c(
        self,
        scl_pin: microcontroller.Pin = board.SCL,
        sda_pin: microcontroller.Pin = board.SDA,
        frequency: int = 400000,
    ):
        if self._i2c is not None:
            return
        self._i2c = busio.I2C(scl_pin, sda_pin, frequency=frequency)
        print("I2C - SCL Pin:", scl_pin, "SDA Pin:", sda_pin, "Frequency:", frequency)

    def setup_lis3dh(
        self,
        interrupt_pin: Optional[microcontroller.Pin] = None,
        range: int = adafruit_lis3dh.RANGE_4_G,
    ):
        if self._i2c is None:
            self.setup_i2c()
        int1 = DigitalInOut(interrupt_pin) if interrupt_pin else None
        self._accelerometer = adafruit_lis3dh.LIS3DH_I2C(self._i2c, int1=int1)
        self._accelerometer.range = range
        print("Accelerometer - Interrupt Pin:", interrupt_pin)

    def setup_onboard_lis3dh(self, range: int = adafruit_lis3dh.RANGE_4_G):
        if self._i2c is None:
            self.setup_i2c()
        int1 = DigitalInOut(board.ACCELEROMETER_INTERRUPT)
        self._accelerometer = adafruit_lis3dh.LIS3DH_I2C(
            self._i2c, address=0x19, int1=int1
        )
        self._accelerometer.range = range
        print("Accelerometer - Onboard")

    def setup_neopixels(
        self, name: str, data: microcontroller.Pin, count: int, brightness: float
    ):
        pixels = neopixel.NeoPixel(data, count, brightness=brightness, auto_write=False)
        self._pixels[name] = pixels
        print("Pixels - Name:", name, "Data Pin:", data, "Count:", count)

    def setup_dotstars(
        self,
        name: str,
        clock: microcontroller.Pin,
        data: microcontroller.Pin,
        count: int,
        brightness: float,
    ):
        pixels = adafruit_dotstar.DotStar(
            clock, data, count, brightness=brightness, auto_write=False
        )
        self._pixels[name] = pixels
        print("Dotstars - Name:", name, "Data Pin:", data, "Count:", count)

    def setup_onboard_audio(self):
        self._digital_out(board.SPEAKER_ENABLE, True)
        self._audio = AudioOut(board.SPEAKER)
        print("Audio - Onboard")

    def setup_audio(self, pin: microcontroller.Pin):
        self._audio = AudioOut(pin)
        print("Audio - Pin:", pin)

    def setup_dfplayer_pro(
        self, tx: microcontroller.Pin, rx: microcontroller.Pin, volume: float = 0.2
    ):
        dfplayer_uart = busio.UART(tx, rx, baudrate=115200)
        self._dfplayer = mindwidgets_df1201s.DF1201S(dfplayer_uart)
        self._dfplayer.volume = volume
        self._dfplayer.play_mode = mindwidgets_df1201s.DF1201S.PLAYMODE_PLAY_ONCE
        print("DFPlayer Pro - TX:", tx, "RX:", rx)

    def setup_ir_in(self, pin: microcontroller.Pin, max_pulses: int = 256):
        self._ir_pulsein = pulseio.PulseIn(pin, maxlen=max_pulses, idle_state=True)
        print("IR receiver - Pin:", pin, "Max Pulses:", max_pulses)

    def setup_ir_out(self, pin: microcontroller.Pin):
        self._ir_pwmout = pwmio.PWMOut(pin, frequency=38000, duty_cycle=2**15)
        self._ir_pulseout = pulseio.PulseOut(self._ir_pwmout)
        print("IR transmitter - Pin:", pin)

    def setup_button(self, name, pin: microcontroller.Pin, pull):
        self._buttons[name] = self._digital_in(pin, pull)
        print("Button - Name:", name, "Pin:", pin, "Pull:", pull)

    def setup_capitive_touch(self, name: str, pin: microcontroller.Pin):
        self._cap_touch[name] = touchio.TouchIn(pin)
        print("Capacitive Touch - Name:", name, "Pin:", pin)

    def setup_switch(self, name, pin: microcontroller.Pin, pull):
        self._switches[name] = self._digital_in(pin, pull)
        print("Switch - Name:", name, "Pin:", pin, "Pull:", pull)

    def setup_piezo_sensor(self, name: str, pin: microcontroller.Pin):
        self._piezos[name] = AnalogIn(pin)
        print("Piezo - Name:", name, "Pin:", pin)

    def update(self):
        if self._accelerometer is not None:
            acceleration = self._accelerometer.acceleration
            if not self._current_acceleration:
                self._current_acceleration = Acceleration()
            self._current_acceleration.x = (
                acceleration[0] / adafruit_lis3dh.STANDARD_GRAVITY
            )
            self._current_acceleration.y = (
                acceleration[1] / adafruit_lis3dh.STANDARD_GRAVITY
            )
            self._current_acceleration.z = (
                acceleration[2] / adafruit_lis3dh.STANDARD_GRAVITY
            )

        current_time = time.monotonic()
        self._ellapsed_time = current_time - self._last_update_time
        self._last_update_time = time.monotonic()

    @property
    def ellapsed_time(self) -> float:
        return self._ellapsed_time

    @property
    def pixels(self) -> dict[str, adafruit_pixelbuf.PixelBuf]:
        return self._pixels

    @property
    def current_acceleration(self) -> Optional[Acceleration]:
        return self._current_acceleration if self._accelerometer else None

    @property
    def audio(self) -> Optional[AudioOut]:
        return self._audio

    @property
    def ir_pulseout(self) -> Optional[pulseio.PulseOut]:
        return self._ir_pulseout

    @property
    def ir_pulsein(self) -> Optional[pulseio.PulseIn]:
        return self._ir_pulsein

    @property
    def dfplayer(self) -> Optional[mindwidgets_df1201s.DF1201S]:
        return self._dfplayer

    def button_down(self, name: str) -> bool:
        button = self._buttons[name]
        on = 0 if button.pull == Pull.UP else 1
        return button.value == on

    def cap_touch(self, name: str) -> bool:
        cap_touch = self._cap_touch[name]
        return cap_touch.value

    def cap_touch_raw(self, name: str) -> int:
        cap_touch = self._cap_touch[name]
        return cap_touch.raw_value

    def switch_on(self, name: str) -> bool:
        switch = self._switches[name]
        on = 0 if switch.pull == Pull.UP else 1
        return switch.value == on

    def piezo(self, name: str) -> float:
        piezo = self._piezos[name]
        return piezo.value / 65536
