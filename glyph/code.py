# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
"""
Author: Mark Roberts (mdroberts1243) from Adafruit code
This test will initialize the display using displayio and draw a solid white
background, a smaller black rectangle, miscellaneous stuff and some white text.

"""

import board
import displayio
import terminalio

# can try import bitmap_label below for alternative
from adafruit_display_text import label
from i2cdisplaybus import I2CDisplayBus

import adafruit_displayio_sh1107

displayio.release_displays()
# oled_reset = board.D9

# Use for I2C
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
display_bus = I2CDisplayBus(i2c, device_address=0x3C)

# SH1107 is vertically oriented 64x128
WIDTH = 128
HEIGHT = 64
BORDER = 2

display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)

# Make the display context
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle in black
inner_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER)
splash.append(inner_sprite)

# Draw some white squares
sm_bitmap = displayio.Bitmap(8, 8, 1)
sm_square = displayio.TileGrid(sm_bitmap, pixel_shader=color_palette, x=58, y=17)
splash.append(sm_square)

med_bitmap = displayio.Bitmap(16, 16, 1)
med_square = displayio.TileGrid(med_bitmap, pixel_shader=color_palette, x=71, y=15)
splash.append(med_square)

lrg_bitmap = displayio.Bitmap(32, 32, 1)
lrg_square = displayio.TileGrid(lrg_bitmap, pixel_shader=color_palette, x=91, y=28)
splash.append(lrg_square)

# Draw some label text
text1 = "0123456789ABCDEF123456789AB"  # overly long to see where it clips
text_area = label.Label(terminalio.FONT, text=text1, color=0xFFFFFF, x=8, y=8)
splash.append(text_area)
text2 = "SH1107"
text_area2 = label.Label(terminalio.FONT, text=text2, scale=2, color=0xFFFFFF, x=9, y=44)
splash.append(text_area2)

while True:
    pass
# SPDX-FileCopyrightText: 2025 Aaron Silinskas for MindWidgets
import time

import board
import hardware
import mindwidgets_df1201s
from state_of_things.state_of_things import ThingObserver
import charging_glyph
import adafruit_led_animation.animation.pulse as pulse
import collapse_chase
import pixel_range

hw = hardware.Hardware()
hw.setup_neopixels("neopixels", board.D5, 10, brightness=1)
hw.setup_lis3dh()
hw.setup_dfplayer_pro(board.TX, board.RX, volume=0.3)
hw.setup_capitive_touch("touch0", board.A0)
hw.setup_capitive_touch("touch1", board.A1)
hw.setup_capitive_touch("touch2", board.A2)
hw.setup_capitive_touch("touch3", board.A3)

all_pixels = hw.pixels["neopixels"]
pixels = pixel_range.PixelRange(all_pixels, 2, 10)

dfplayer: mindwidgets_df1201s.DF1201S = hw.dfplayer
if dfplayer:
    print("DFPlayer Pro detected, playing first track")
    dfplayer.play_next()

class LoggingObserver(ThingObserver):
    def state_changed(self, thing, old_state, new_state):
        print(f"State changed from {old_state.name} to {new_state.name}")
        
glyph = charging_glyph.ChargingGlyph(charge_time=5.0, discharge_time=3.0)
glyph.observers.attach(LoggingObserver())

charging_animation = pulse.Pulse(pixels, speed=0.1, color=(255, 255, 255), period=2, max_intensity=1)
glyph.set_animations(
    deactivated=collapse_chase.CollapseChase(pixels, speed=0.1, color=(255, 0, 0), target=7, distance=4, max_intensity=1),
    #deactivated=pulse.Pulse(pixels, speed=0.1, color=(255, 0, 0), period=5, max_intensity=0.5),
    activated=pulse.Pulse(pixels, speed=0.1, color=(255, 255, 255), period=3, max_intensity=0.5),
    charging=charging_animation,
    charged=pulse.Pulse(pixels, speed=0.1, color=(0, 255, 64), period=5, max_intensity=0.5),
    discharging=pulse.Pulse(pixels, speed=0.1, color=(255, 255, 255), period=1, max_intensity=0.2),
    deactivating=pulse.Pulse(pixels, speed=0.05, color=(0, 0, 255), period=1, max_intensity=0.2),
)

while True:
    hw.update()
    
    # print("Elapsed Time:", hw.elapsed_time)

    # print(
    #     "X:",
    #     hw.current_acceleration.x,
    #     "Y:",
    #     hw.current_acceleration.y,
    #     "Z:",
    #     hw.current_acceleration.z,
    # )

    # if hw.cap_touch("touch0"):
    #     print("Touch 0 detected!", hw.cap_touch_raw("touch0"))
    # if hw.cap_touch("touch1"):
    #     print("Touch 1 detected!", hw.cap_touch_raw("touch1"))
    # if hw.cap_touch("touch2"):
    #     print("Touch 2 detected!", hw.cap_touch_raw("touch2"))
    # if hw.cap_touch("touch3"):
    #     print("Touch 3 detected!", hw.cap_touch_raw("touch3"))
    
    glyph.activated = hw.cap_touch("touch0")    
    glyph.touched = hw.cap_touch("touch1")
    if glyph.activated and glyph.touched:        
        charging_animation.max_intensity = glyph.charge_level
        print("Glyph Charge Level:", glyph.charge_level)

    glyph.update()
