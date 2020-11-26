
def map_pixel(pixels, row, col):
    if (row < 0) or (row >= pixels.n / 2):
        return None
    if col == 0:
        return row
    return pixels.n - row - 1


def apply_brighten(pixels, row, col, offset):
    i = map_pixel(pixels, row, col)
    if i is None:
        return
    pixel = pixels[i]
    brighten = int(192 / offset)
    r = min(pixel[0] + brighten, 255)
    g = min(pixel[1] + brighten, 255)
    b = min(pixel[2] + brighten, 255)
    pixels[i] = (r, g, b)


def draw_casting(spell_state, pixels, ellapsed_time, progress):
    draw_spell(spell_state, pixels, ellapsed_time)
    # TODO hardcoded for prototype, replace with pixel map
    pix_per_side = pixels.n / 2
    brightener_pos = int(pix_per_side * progress) + 2
    for row in range(brightener_pos - 4, brightener_pos):
        for col in range(0, 2):
            apply_brighten(pixels, row, col, brightener_pos - row + 1)
    darkener_pos = brightener_pos - 5
    for row in range(darkener_pos, -1, -1):
        for col in range(0, 2):
            i = map_pixel(pixels, row, col)
            if i is not None:
                pixels[i] = (0, 0, 0)

def draw_weaved(spell, pixels, ellapsed_time, progress):
    # TODO make amazing initial spell animation
    pass

def draw_spell(spell_state, pixels, ellapsed_time):
    # print("Power: ", spell_state.power)
    spell_state.spell.draw(pixels, spell_state, ellapsed_time)