"""
Item sprites: weapons, potions, gems, misc.
All with outlines and shading.
"""

from engine.drawing import new_sprite, put_pixel, draw_outline_thick, apply_shading_auto
from engine.palette import ITEMS, TERRAIN, PLAYER, ShadedColor, recolor
from engine.sprite import StaticSprite


def _finalize(img, shade_map=None):
    if shade_map:
        img = apply_shading_auto(img, shade_map)
    return draw_outline_thick(img)


# ============================================================
# WEAPONS
# ============================================================

def generate_sword() -> StaticSprite:
    it = ITEMS
    img = new_sprite()
    metal = it.base("metal")
    metal_s = it.colors["metal"]

    # Handle
    put_pixel(img, 6, 12, it.base("handle"))
    put_pixel(img, 7, 11, it.base("handle"))
    put_pixel(img, 5, 13, it.base("handle"))
    # Guard
    for x in range(5, 10):
        put_pixel(img, x, 10, it.base("gold"))
    # Blade
    for i in range(8):
        put_pixel(img, 7, 9 - i, metal)
        if i < 7:
            put_pixel(img, 8, 9 - i, metal)
    # Tip
    put_pixel(img, 7, 1, it.highlight("metal"))

    shade_map = {metal: metal_s}
    return StaticSprite("sword", _finalize(img, shade_map), "weapons")


def generate_shield() -> StaticSprite:
    it = ITEMS
    img = new_sprite()
    shirt = PLAYER.base("shirt")
    shirt_s = PLAYER.colors["shirt"]

    shield_pixels = [
        (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3),
        (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (11, 4),
        (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (11, 5),
        (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (11, 6),
        (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7),
        (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8),
        (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9),
        (6, 10), (7, 10), (8, 10), (9, 10),
        (7, 11), (8, 11),
    ]
    for (x, y) in shield_pixels:
        put_pixel(img, x, y, shirt)
    # Cross emblem
    gold = it.base("gold")
    for i in range(4, 9):
        put_pixel(img, 7, i + 1, gold)
        put_pixel(img, 8, i + 1, gold)
    for i in range(5, 10):
        put_pixel(img, i + 1, 7, gold)

    shade_map = {shirt: shirt_s}
    return StaticSprite("shield", _finalize(img, shade_map), "weapons")


def generate_bow() -> StaticSprite:
    it = ITEMS
    img = new_sprite()
    handle = it.base("handle")

    # Bow curve
    bow = [(6, 2), (5, 3), (4, 4), (4, 5), (4, 6), (4, 7),
           (4, 8), (4, 9), (4, 10), (5, 11), (6, 12)]
    for (x, y) in bow:
        put_pixel(img, x, y, handle)
    # String
    for y in range(3, 12):
        put_pixel(img, 8, y, (200, 200, 200))
    # Arrow
    for x in range(8, 15):
        put_pixel(img, x, 7, handle)
    put_pixel(img, 14, 6, it.base("metal"))
    put_pixel(img, 15, 7, it.base("metal"))
    put_pixel(img, 14, 8, it.base("metal"))

    return StaticSprite("bow", _finalize(img), "weapons")


def generate_axe() -> StaticSprite:
    it = ITEMS
    img = new_sprite()
    handle = it.base("handle")
    metal = it.base("metal")

    # Handle
    for y in range(5, 14):
        put_pixel(img, 7, y, handle)
    # Axe head
    for y in range(3, 8):
        put_pixel(img, 8, y, metal)
        put_pixel(img, 9, y, metal)
        if y > 3 and y < 7:
            put_pixel(img, 10, y, metal)
    put_pixel(img, 10, 5, it.highlight("metal"))

    shade_map = {metal: it.colors["metal"]}
    return StaticSprite("axe", _finalize(img, shade_map), "weapons")


# ============================================================
# POTIONS (3 variants generated from base)
# ============================================================

def _generate_potion(color_key: str, name: str) -> StaticSprite:
    it = ITEMS
    img = new_sprite()
    color = it.base(color_key)
    shaded = it.colors[color_key]

    # Cork
    put_pixel(img, 7, 3, (160, 120, 60))
    put_pixel(img, 8, 3, (160, 120, 60))
    # Neck
    put_pixel(img, 7, 4, (200, 200, 220))
    put_pixel(img, 8, 4, (200, 200, 220))
    # Body
    for x in range(5, 11):
        for y in range(5, 12):
            if y == 5 and (x == 5 or x == 10):
                continue
            put_pixel(img, x, y, color)
    # Highlight
    put_pixel(img, 6, 6, shaded.highlight)
    put_pixel(img, 6, 7, shaded.highlight)
    # Bottom rim
    for x in range(5, 11):
        put_pixel(img, x, 12, it.shadow("metal"))
    # Label
    put_pixel(img, 7, 8, (255, 255, 255, 180))
    put_pixel(img, 8, 8, (255, 255, 255, 180))
    put_pixel(img, 7, 9, (255, 255, 255, 180))
    put_pixel(img, 8, 9, (255, 255, 255, 180))

    shade_map = {color: shaded}
    return StaticSprite(name, _finalize(img, shade_map), "potions")


def generate_health_potion() -> StaticSprite:
    return _generate_potion("potion_red", "health_potion")

def generate_mana_potion() -> StaticSprite:
    return _generate_potion("potion_blue", "mana_potion")

def generate_stamina_potion() -> StaticSprite:
    return _generate_potion("potion_green", "stamina_potion")


# ============================================================
# GEMS (3 colors)
# ============================================================

def _generate_gem(color_key: str, name: str) -> StaticSprite:
    it = ITEMS
    img = new_sprite()
    color = it.base(color_key)
    shaded = it.colors[color_key]

    gem_pixels = [
        (7, 4), (8, 4),
        (6, 5), (7, 5), (8, 5), (9, 5),
        (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6),
        (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7),
        (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8),
        (6, 9), (7, 9), (8, 9), (9, 9),
        (7, 10), (8, 10),
    ]
    for (x, y) in gem_pixels:
        put_pixel(img, x, y, color)
    # Facet highlight
    put_pixel(img, 7, 5, shaded.highlight)
    put_pixel(img, 6, 6, shaded.highlight)
    put_pixel(img, 7, 6, (255, 255, 255, 200))
    # Facet lines
    put_pixel(img, 8, 7, shaded.shadow)
    put_pixel(img, 9, 8, shaded.shadow)

    shade_map = {color: shaded}
    return StaticSprite(name, _finalize(img, shade_map), "gems")


def generate_ruby() -> StaticSprite:
    return _generate_gem("gem_red", "ruby")

def generate_sapphire() -> StaticSprite:
    return _generate_gem("gem_blue", "sapphire")

def generate_emerald() -> StaticSprite:
    return _generate_gem("gem_green", "emerald")


# ============================================================
# MISC ITEMS
# ============================================================

def generate_coin() -> StaticSprite:
    it = ITEMS
    img = new_sprite()
    gold = it.base("gold")
    shaded = it.colors["gold"]

    coin_pixels = [
        (6, 5), (7, 5), (8, 5), (9, 5),
        (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6),
        (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7),
        (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8),
        (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9),
        (6, 10), (7, 10), (8, 10), (9, 10),
    ]
    for (x, y) in coin_pixels:
        put_pixel(img, x, y, gold)
    # Dollar sign
    for pos in [(7, 6), (8, 6), (7, 7), (8, 8), (7, 9), (8, 9)]:
        put_pixel(img, pos[0], pos[1], shaded.shadow)
    # Highlight
    put_pixel(img, 6, 6, shaded.highlight)
    put_pixel(img, 6, 7, shaded.highlight)

    shade_map = {gold: shaded}
    return StaticSprite("coin", _finalize(img, shade_map), "misc")


def generate_key() -> StaticSprite:
    it = ITEMS
    img = new_sprite()
    gold = it.base("gold")
    shaded = it.colors["gold"]

    ring = [(6, 3), (7, 3), (8, 3), (9, 3),
            (5, 4), (10, 4), (5, 5), (10, 5),
            (6, 6), (7, 6), (8, 6), (9, 6)]
    for (x, y) in ring:
        put_pixel(img, x, y, gold)
    for y in range(7, 13):
        put_pixel(img, 7, y, gold)
        put_pixel(img, 8, y, shaded.shadow)
    put_pixel(img, 9, 11, gold)
    put_pixel(img, 9, 12, gold)
    put_pixel(img, 10, 12, gold)

    shade_map = {gold: shaded}
    return StaticSprite("key", _finalize(img, shade_map), "misc")


def generate_chest() -> StaticSprite:
    it = ITEMS
    t = TERRAIN
    img = new_sprite()
    wood = t.base("wood")
    wood_s = t.colors["wood"]

    # Body
    for x in range(3, 13):
        for y in range(6, 13):
            put_pixel(img, x, y, wood)
    # Lid
    for x in range(3, 13):
        for y in range(4, 7):
            put_pixel(img, x, y, wood)
    # Metal bands
    metal = it.shadow("metal")
    for x in range(3, 13):
        put_pixel(img, x, 6, metal)
        put_pixel(img, x, 4, metal)
    # Side bands
    for y in range(4, 13):
        put_pixel(img, 3, y, metal)
        put_pixel(img, 12, y, metal)
    # Lock
    gold = it.base("gold")
    for pos in [(7, 7), (8, 7), (7, 8), (8, 8)]:
        put_pixel(img, pos[0], pos[1], gold)
    # Keyhole
    put_pixel(img, 7, 8, it.shadow("gold"))

    shade_map = {wood: wood_s}
    return StaticSprite("chest", _finalize(img, shade_map), "misc")


def generate_all() -> list:
    return [
        generate_sword(), generate_shield(), generate_bow(), generate_axe(),
        generate_health_potion(), generate_mana_potion(), generate_stamina_potion(),
        generate_ruby(), generate_sapphire(), generate_emerald(),
        generate_coin(), generate_key(), generate_chest(),
    ]
