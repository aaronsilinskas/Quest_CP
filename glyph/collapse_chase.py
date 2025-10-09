# SPDX-FileCopyrightText: 2025 Aaron Silinskas for MindWidgets
#
# SPDX-License-Identifier: MIT

"""
`mindwidgets_animation.collapse_chase`
================================================================================

Glyph LED animation.

* Author(s): Aaron Silinskas
"""
import math
from adafruit_led_animation.animation import Animation
from adafruit_led_animation.color import calculate_intensity
from adafruit_led_animation import monotonic_ms

class CollapseChase(Animation):
    """
    Chase pixels to a target pixel from both ends of the strip.

    :param pixel_object: The initialised LED object.
    :param float speed: Animation refresh rate in seconds, e.g. ``0.1``.
    :param color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
    :param target: Target pixel index to chase towards. Default 0 (the first pixel).
    :param distance: Distance from target to start the chase. Default is half the number of pixels.
    :param min_intensity: Starting brightness level of the pixels. Default 0.
    :param max_intensity: Ending brightness level of the pixels. Default 1.
    """

    def __init__(
        self,
        pixel_object,
        speed,
        color,
        target: int=0,
        distance: int=None,
        min_intensity=0,
        max_intensity=1,
        name=None,
    ):
        super().__init__(pixel_object, speed, color, name=name)
        self._target = target
        self._distance: int = distance if distance is not None else int(len(pixel_object) // 2)
        self.min_intensity = min_intensity
        self.max_intensity = max_intensity

        self._distance_remaining: float = float(self._distance)

        self.reset()

    on_cycle_complete_supported = True

    def draw(self):
        self._distance_remaining = max(0.0, self._distance_remaining - self.speed)
        if self._distance_remaining <= 0:
            self.cycle_complete = True
            self._distance_remaining = self._distance
        
        intensity_range = self.max_intensity - self.min_intensity
        brightness = self.min_intensity + intensity_range * (1 - self._distance_remaining / self._distance)
        color = calculate_intensity(self.color, brightness)
        self.pixel_object.fill((0, 0, 0))
        if self._distance_remaining > 1:
            left_pixel = math.ceil(self._target - self._distance_remaining) % len(self.pixel_object)
            self.pixel_object[left_pixel] = color
            right_pixel = math.floor(self._target + self._distance_remaining) % len(self.pixel_object)
            self.pixel_object[right_pixel] = color
            
            print("Distance:", self._distance_remaining, "Left:", left_pixel, "Right:", right_pixel, "Color:", color)
        else:            
            self.pixel_object[self._target] = color
            
            print("Reached destination:", self._target, "Color:", color)

    def reset(self):
        """
        Resets the animation.
        """
        
        
