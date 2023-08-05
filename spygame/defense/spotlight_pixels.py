import math

from adafruit_pixelbuf import PixelBuf
from adafruit_led_animation import color


class SpotlightPixels:
    def __init__(self, pixels: PixelBuf, color, width: float, wrap: bool) -> None:
        self._pixels = pixels
        self._color = color
        self._width = width
        self._wrap = wrap

        self._position: float = 0

    @property
    def position(self) -> float:
        return self._position

    @position.setter
    def position(self, position: float) -> None:
        self._position = position

    def show(self):
        pixel_count = len(self._pixels)

        center_pixel = self._position * pixel_count

        # Draw left side, handle left wrap
        left_pixel = center_pixel - self._width / 2
        right_pixel = left_pixel + self._width
        current_pixel = left_pixel
        while current_pixel <= right_pixel:
            # map to real pixel location
            pixel_index = math.floor(current_pixel)
            if pixel_index < 0:
                pixel_index += pixel_count
            elif pixel_index >= pixel_count:
                pixel_index -= pixel_count

            # calculate pixel brightness
            pixel_brightness = 1
            if current_pixel == left_pixel or current_pixel == right_pixel:
                pixel_brightness = abs(current_pixel % 1)
                if current_pixel == left_pixel:
                    # pixel is the left end, invert brightness
                    pixel_brightness = 1 - pixel_brightness

            # print("Pixel", current_pixel, "Index", pixel_index, "Brightness", pixel_brightness)

            self._pixels[pixel_index] = color.calculate_intensity(
                self._color, pixel_brightness)

            current_pixel += 1
