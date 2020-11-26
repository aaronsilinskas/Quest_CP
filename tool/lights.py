class PixelEdge(object):
    def __init__(self, pixel_buf, indexes):
        self.pixel_buf = pixel_buf
        self.indexes = list(indexes)
        
    def __len__(self):
        return len(self.indexes)

    def __setitem__(self, index, val):
        self.pixel_buf[self.indexes[index]] = val
    
    def __getitem__(self, index):
        return self.pixel_buf[self.indexes[index]]

def mix(color_1, color_2, weight_2):
    if weight_2 < 0.0:
        weight_2 = 0.0
    elif weight_2 > 1.0:
        weight_2 = 1.0
    weight_1 = 1.0 - weight_2
    return (int(color_1[0] * weight_1 + color_2[0] * weight_2),
            int(color_1[1] * weight_1 + color_2[1] * weight_2),
            int(color_1[2] * weight_1 + color_2[2] * weight_2))

def apply_brighten(pixels, index, offset):    
    if (index < 0) or (index >= len(pixels)):
        return
    pixel = pixels[index]
    brighten = int(192 / offset)
    r = min(pixel[0] + brighten, 255)
    g = min(pixel[1] + brighten, 255)
    b = min(pixel[2] + brighten, 255)
    pixels[index] = (r, g, b)


def draw_casting(spell_state, pixels, ellapsed_time, progress, darkener=True):
    draw_spell(spell_state, pixels, ellapsed_time)
    # TODO hardcoded for prototype, replace with pixel map
    brightener_pos = int(len(pixels) * progress) + 2
    for index in range(brightener_pos - 4, brightener_pos):
        apply_brighten(pixels, index, brightener_pos - index + 1)
    if darkener:
        darkener_pos = brightener_pos - 5
        for index in range(darkener_pos, -1, -1):
            if (index >= 0) and (index < len(pixels)):
                pixels[index] = (0, 0, 0)

def draw_weaved(spell_state, pixels, ellapsed_time, progress):
    draw_casting(spell_state, pixels, ellapsed_time, progress, darkener=False)

def draw_spell(spell_state, pixels, ellapsed_time):
    # print("Power: ", spell_state.power)
    spell_state.spell.draw(pixels, spell_state, ellapsed_time)