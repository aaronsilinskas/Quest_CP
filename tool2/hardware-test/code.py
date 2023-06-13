import time
import hardware
from infrared import Infrared
import adafruit_drv2605

infrared = Infrared(hardware.ir_pulseout, hardware.ir_pulsein)

###########

pixel_num = 0
pixel_color = (64, 0, 0)
hud_y = 0

while True:
    if hardware.trigger.value == 0:
        print("Trigger")
        pulses = b"Hello!"
        infrared.send(pulses)
        hardware.df_player.play_next()
        hardware.vibrator.sequence[0] = adafruit_drv2605.Effect(83)
        hardware.vibrator.sequence[1] = adafruit_drv2605.Effect(37)
        hardware.vibrator.sequence[2] = adafruit_drv2605.Effect(74)
        hardware.vibrator.play()

    ir_received = infrared.receive()
    if ir_received is not None:
        data, strength = ir_received
        print("IR Data Received: ", data.decode("utf-8"), strength)

    if hardware.radio.payload_ready():
        radio_received = hardware.radio.receive(keep_listening=True)
        print("Radio Data Received: ",
              radio_received.decode("utf-8"), hardware.radio.last_rssi)

    hardware.barrel_pixels[pixel_num] = pixel_color
    pixel_num = pixel_num + 1
    if pixel_num >= hardware.barrel_pixels.n:
        pixel_num = 0
        if pixel_color == 0:
            pixel_color = (64, 0, 0)
        else:
            pixel_color = 0
    hardware.barrel_pixels.show()

    hardware.hud_framebuf.fill(0)
    hardware.hud_framebuf.line(0, hud_y, hardware.hud_framebuf.width, hud_y, (0, 0, 255))
    hardware.hud_framebuf.display()
    hardware.hud_pixels.show()
    hud_y += 1
    if hud_y >= hardware.hud_framebuf.height:
        hud_y = 0

    x, y, z = hardware.imu.acceleration
    # print(x, y, z)
    if hardware.imu.tapped:
        print("Tapped!")

    time.sleep(0.2)
