"""
UI elements: hearts, mana orb, health bars, buttons, inventory.
"""

from PIL import Image, ImageDraw
from engine.drawing import new_sprite, put_pixel, draw_outline_thick, create_spritesheet
from engine.palette import UI, TRANSPARENT
from engine.sprite import StaticSprite, SpriteSheet


def generate_heart_full() -> StaticSprite:
    u = UI
    img = new_sprite()
    heart_pixels = [
        (3, 4), (4, 3), (5, 3), (6, 4),
        (9, 4), (10, 3), (11, 3), (12, 4),
        (2, 5), (3, 5), (4, 4), (5, 4), (6, 5), (7, 5),
        (8, 5), (9, 5), (10, 4), (11, 4), (12, 5), (13, 5),
        (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6),
        (8, 6), (9, 6), (10, 6), (11, 6), (12, 6), (13, 6),
        (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
        (8, 7), (9, 7), (10, 7), (11, 7), (12, 7),
        (4, 8), (5, 8), (6, 8), (7, 8),
        (8, 8), (9, 8), (10, 8), (11, 8),
        (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9),
        (6, 10), (7, 10), (8, 10), (9, 10),
        (7, 11), (8, 11),
    ]
    for (x, y) in heart_pixels:
        put_pixel(img, x, y, u.base("heart"))
    # Highlight
    put_pixel(img, 4, 4, u.highlight("heart"))
    put_pixel(img, 5, 4, u.highlight("heart"))
    put_pixel(img, 10, 4, u.highlight("heart"))
    # Shadow
    put_pixel(img, 7, 10, u.shadow("heart"))
    put_pixel(img, 8, 10, u.shadow("heart"))
    put_pixel(img, 7, 11, u.shadow("heart"))
    put_pixel(img, 8, 11, u.shadow("heart"))

    return StaticSprite("heart_full", draw_outline_thick(img), "ui")


def generate_heart_empty() -> StaticSprite:
    u = UI
    img = new_sprite()
    heart_pixels = [
        (3, 4), (4, 3), (5, 3), (6, 4),
        (9, 4), (10, 3), (11, 3), (12, 4),
        (2, 5), (3, 5), (4, 4), (5, 4), (6, 5), (7, 5),
        (8, 5), (9, 5), (10, 4), (11, 4), (12, 5), (13, 5),
        (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6),
        (8, 6), (9, 6), (10, 6), (11, 6), (12, 6), (13, 6),
        (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
        (8, 7), (9, 7), (10, 7), (11, 7), (12, 7),
        (4, 8), (5, 8), (6, 8), (7, 8),
        (8, 8), (9, 8), (10, 8), (11, 8),
        (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9),
        (6, 10), (7, 10), (8, 10), (9, 10),
        (7, 11), (8, 11),
    ]
    for (x, y) in heart_pixels:
        put_pixel(img, x, y, u.shadow("heart"))

    return StaticSprite("heart_empty", draw_outline_thick(img), "ui")


def generate_heart_half() -> StaticSprite:
    """Half-filled heart."""
    u = UI
    img = new_sprite()
    heart_pixels = [
        (3, 4), (4, 3), (5, 3), (6, 4),
        (9, 4), (10, 3), (11, 3), (12, 4),
        (2, 5), (3, 5), (4, 4), (5, 4), (6, 5), (7, 5),
        (8, 5), (9, 5), (10, 4), (11, 4), (12, 5), (13, 5),
        (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6),
        (8, 6), (9, 6), (10, 6), (11, 6), (12, 6), (13, 6),
        (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
        (8, 7), (9, 7), (10, 7), (11, 7), (12, 7),
        (4, 8), (5, 8), (6, 8), (7, 8),
        (8, 8), (9, 8), (10, 8), (11, 8),
        (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9),
        (6, 10), (7, 10), (8, 10), (9, 10),
        (7, 11), (8, 11),
    ]
    for (x, y) in heart_pixels:
        # Left half full, right half empty
        if x <= 7:
            put_pixel(img, x, y, u.base("heart"))
        else:
            put_pixel(img, x, y, u.shadow("heart"))

    return StaticSprite("heart_half", draw_outline_thick(img), "ui")


def generate_mana_orb() -> StaticSprite:
    u = UI
    img = new_sprite()
    orb = [
        (6, 4), (7, 4), (8, 4), (9, 4),
        (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5),
        (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (11, 6),
        (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7),
        (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (11, 8),
        (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9),
        (6, 10), (7, 10), (8, 10), (9, 10),
    ]
    for (x, y) in orb:
        put_pixel(img, x, y, u.base("mana"))
    # Highlight
    put_pixel(img, 6, 5, u.highlight("mana"))
    put_pixel(img, 7, 5, u.highlight("mana"))
    put_pixel(img, 6, 6, u.highlight("mana"))
    # Shadow
    put_pixel(img, 9, 9, u.shadow("mana"))
    put_pixel(img, 8, 10, u.shadow("mana"))

    return StaticSprite("mana_orb", draw_outline_thick(img), "ui")


def generate_healthbar(fill_pct: float = 1.0, name_suffix: str = "") -> StaticSprite:
    u = UI
    w, h = 48, 16
    img = Image.new("RGBA", (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Background
    draw.rectangle([0, 0, w - 1, h - 1], fill=u.base("bg_dark"), outline=u.base("border"))
    # Fill
    fill_w = int((w - 4) * fill_pct)
    if fill_w > 0:
        # Color based on fill level
        if fill_pct > 0.5:
            fill_color = u.base("stamina")
        elif fill_pct > 0.25:
            fill_color = (220, 180, 40)  # yellow warning
        else:
            fill_color = u.base("heart")
        draw.rectangle([2, 2, 2 + fill_w, h - 3], fill=fill_color)
        # Highlight line
        draw.line([(2, 2), (2 + fill_w, 2)], fill=u.highlight("text"))

    name = f"healthbar{'_' + name_suffix if name_suffix else ''}"
    return StaticSprite(name, img, "ui")


def generate_button() -> StaticSprite:
    u = UI
    w, h = 48, 16
    img = Image.new("RGBA", (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([1, 1, w - 2, h - 2], radius=3, fill=u.base("bg_light"))
    draw.rounded_rectangle([1, 1, w - 2, h - 2], radius=3, outline=u.base("border"))
    # Top highlight
    draw.line([(3, 2), (w - 4, 2)], fill=(100, 100, 120))
    # Bottom shadow
    draw.line([(3, h - 3), (w - 4, h - 3)], fill=(40, 40, 55))

    return StaticSprite("button", img, "ui")


def generate_inventory_slot() -> StaticSprite:
    u = UI
    img = Image.new("RGBA", (20, 20), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, 19, 19], fill=u.base("bg_dark"), outline=u.base("border"))
    # Inner highlight
    draw.rectangle([1, 1, 18, 18], outline=u.base("bg_light"))
    # Corner detail
    img.putpixel((1, 1), (*u.highlight("border"), 255))

    return StaticSprite("inventory_slot", img, "ui")


def generate_inventory_grid() -> StaticSprite:
    slot = generate_inventory_slot()
    grid = Image.new("RGBA", (64, 64), TRANSPARENT)
    for row in range(3):
        for col in range(3):
            grid.paste(slot.image, (col * 21 + 1, row * 21 + 1))
    return StaticSprite("inventory_grid", grid, "ui")


def generate_all() -> list:
    return [
        generate_heart_full(),
        generate_heart_empty(),
        generate_heart_half(),
        generate_mana_orb(),
        generate_healthbar(1.0, "full"),
        generate_healthbar(0.75, "high"),
        generate_healthbar(0.5, "half"),
        generate_healthbar(0.25, "low"),
        generate_healthbar(0.1, "critical"),
        generate_button(),
        generate_inventory_slot(),
        generate_inventory_grid(),
        # 5-heart strip
        StaticSprite("health_hearts",
                     create_spritesheet([generate_heart_full().image for _ in range(5)]),
                     "ui"),
    ]
