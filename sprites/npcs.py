"""
NPC sprites: villager and merchant, with outlines and shading.
Each NPC has idle and hit (2-frame flinch) animations.
"""

from engine.drawing import new_sprite, put_pixel, draw_outline, draw_outline_thick, apply_shading_auto
from engine.palette import PLAYER, ITEMS, ShadedColor
from engine.sprite import SpriteSheet


def _apply_flash(img, intensity: float = 0.7):
    """Apply a white flash effect for hit feedback."""
    result = img.copy()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            px = result.getpixel((x, y))
            if px[3] > 0:
                r = int(px[0] + (255 - px[0]) * intensity)
                g = int(px[1] + (255 - px[1]) * intensity)
                b = int(px[2] + (255 - px[2]) * intensity)
                result.putpixel((x, y), (r, g, b, px[3]))
    return result

ROBE_COLOR = (160, 80, 40)
ROBE_SHADED = ShadedColor.from_base(ROBE_COLOR)
MERCHANT_ROBE = (120, 40, 140)
MERCHANT_SHADED = ShadedColor.from_base(MERCHANT_ROBE)
BLONDE = (180, 140, 60)
BLONDE_SHADED = ShadedColor.from_base(BLONDE)


def _shade_and_outline(img, shade_map):
    img = apply_shading_auto(img, shade_map)
    return draw_outline_thick(img)


def generate_villager() -> SpriteSheet:
    p = PLAYER
    frames = []
    shade_map = {
        p.base("skin"): p.colors["skin"],
        ROBE_COLOR: ROBE_SHADED,
        BLONDE: BLONDE_SHADED,
    }

    for f in range(4):
        img = new_sprite()
        y_off = 1 if f in (1, 3) else 0

        # Head
        for x in range(5, 11):
            for y in range(2, 6):
                put_pixel(img, x, y + y_off, p.base("skin"))
        # Blonde hair
        for x in range(5, 11):
            put_pixel(img, x, 2 + y_off, BLONDE)
            put_pixel(img, x, 3 + y_off, BLONDE)
        # Eyes
        put_pixel(img, 7, 4 + y_off, p.base("eyes"))
        put_pixel(img, 9, 4 + y_off, p.base("eyes"))
        # Blink
        if f == 2:
            put_pixel(img, 7, 4 + y_off, p.base("skin"))
            put_pixel(img, 9, 4 + y_off, p.base("skin"))
        # Robe
        for x in range(4, 12):
            for y in range(6, 13):
                put_pixel(img, x, y + y_off, ROBE_COLOR)
        # Belt
        for x in range(4, 12):
            put_pixel(img, x, 9 + y_off, (200, 160, 60))
        # Feet
        for pos in [(5, 13), (6, 13), (9, 13), (10, 13)]:
            put_pixel(img, pos[0], pos[1] + y_off, (100, 60, 30))

        frames.append(_shade_and_outline(img, shade_map))

    return SpriteSheet("villager", frames, frame_duration_ms=200)


def generate_merchant() -> SpriteSheet:
    p = PLAYER
    frames = []
    shade_map = {
        p.base("skin"): p.colors["skin"],
        MERCHANT_ROBE: MERCHANT_SHADED,
    }

    for f in range(4):
        img = new_sprite()
        y_off = 1 if f in (1, 3) else 0

        # Head
        for x in range(5, 11):
            for y in range(1, 6):
                put_pixel(img, x, y + y_off, p.base("skin"))
        # Hat
        for x in range(4, 12):
            put_pixel(img, x, 1 + y_off, (100, 50, 120))
        for x in range(5, 11):
            put_pixel(img, x, 0 + y_off, (100, 50, 120))
        # Eyes
        put_pixel(img, 7, 4 + y_off, p.base("eyes"))
        put_pixel(img, 9, 4 + y_off, p.base("eyes"))
        # Beard
        for pos in [(7, 5), (8, 5), (7, 6)]:
            put_pixel(img, pos[0], pos[1] + y_off, (180, 170, 150))
        # Robe
        for x in range(4, 12):
            for y in range(6, 13):
                put_pixel(img, x, y + y_off, MERCHANT_ROBE)
        # Gold trim
        gold = ITEMS.base("gold")
        for x in range(4, 12):
            put_pixel(img, x, 12 + y_off, gold)
        put_pixel(img, 4, 7 + y_off, gold)
        put_pixel(img, 11, 7 + y_off, gold)
        # Feet
        put_pixel(img, 6, 13 + y_off, (80, 40, 100))
        put_pixel(img, 9, 13 + y_off, (80, 40, 100))

        frames.append(_shade_and_outline(img, shade_map))

    return SpriteSheet("merchant", frames, frame_duration_ms=200)


def generate_villager_hit() -> SpriteSheet:
    idle = generate_villager()
    f0 = _apply_flash(idle.frames[0], 0.6)
    f1 = idle.frames[1]  # bobbed frame as flinch
    return SpriteSheet("villager_hit", [f0, f1], frame_duration_ms=100, loop=False,
                       frame_durations_ms=[80, 120])


def generate_merchant_hit() -> SpriteSheet:
    idle = generate_merchant()
    f0 = _apply_flash(idle.frames[0], 0.6)
    f1 = idle.frames[1]
    return SpriteSheet("merchant_hit", [f0, f1], frame_duration_ms=100, loop=False,
                       frame_durations_ms=[80, 120])


def generate_all() -> list:
    return [
        generate_villager(),
        generate_villager_hit(),
        generate_merchant(),
        generate_merchant_hit(),
    ]
