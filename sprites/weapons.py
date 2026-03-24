"""
Advanced weapon sprite and animation generator.

Melee: sword slash, axe chop, mace swing, spear thrust, dagger stab, hammer smash, scythe sweep
Ranged: bow draw/release, crossbow fire, shuriken spin, throwing knife
Magic: staff charge, wand cast, orb pulse, tome open
Shields: round shield, kite shield, tower shield
Enchantments: fire, ice, lightning, poison, shadow overlays
Rarity: common, uncommon, rare, epic, legendary glow tiers
"""

import math
from engine.drawing import (
    new_sprite, put_pixel, get_pixel, draw_outline, draw_outline_thick, draw_line,
    draw_circle, draw_rect, draw_ellipse_filled,
)
from engine.palette import WEAPONS
from engine.sprite import SpriteSheet, StaticSprite


wp = WEAPONS


# ============================================================
# HELPERS
# ============================================================

def _rotate_point(x: float, y: float, cx: float, cy: float, angle: float) -> tuple[int, int]:
    """Rotate point (x,y) around center (cx,cy) by angle in radians."""
    dx = x - cx
    dy = y - cy
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    nx = cx + dx * cos_a - dy * sin_a
    ny = cy + dx * sin_a + dy * cos_a
    return round(nx), round(ny)


def _draw_rotated_pixels(img, pixels: list[tuple[int, int, tuple]], cx: float, cy: float, angle: float):
    """Draw a list of (x, y, color) pixels rotated around center."""
    for px, py, color in pixels:
        rx, ry = _rotate_point(px, py, cx, cy, angle)
        if 0 <= rx < img.width and 0 <= ry < img.height:
            put_pixel(img, rx, ry, color)


def _smoothstep(t: float) -> float:
    """Smoothstep easing for natural swing motion."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _add_enchantment_particles(img, enchant: str, frame: int, seed: int = 0):
    """Add enchantment particle overlay to a weapon frame."""
    if not enchant:
        return

    colors = {
        "fire": (wp.base("fire"), wp.highlight("fire_bright")),
        "ice": (wp.base("ice"), wp.highlight("ice_bright")),
        "lightning": (wp.base("lightning"), wp.highlight("lightning_bright")),
        "poison": (wp.base("poison"), wp.highlight("poison")),
        "shadow": (wp.base("shadow"), wp.highlight("shadow")),
    }
    if enchant not in colors:
        return

    c1, c2 = colors[enchant]
    # Scatter particles near non-transparent pixels
    rng_base = seed + frame * 17
    for i in range(4):
        rng = (rng_base + i * 31) % 256
        px = (rng * 7 + i * 13) % img.width
        py = (rng * 11 + i * 19 + frame * 3) % img.height
        # Only place near existing pixels
        check_x = max(0, min(img.width - 1, px))
        check_y = max(0, min(img.height - 1, py))
        nearby = False
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                nx, ny = check_x + dx, check_y + dy
                if 0 <= nx < img.width and 0 <= ny < img.height:
                    _, _, _, a = get_pixel(img, nx, ny)
                    if a > 0:
                        nearby = True
                        break
            if nearby:
                break
        if nearby:
            color = c1 if i % 2 == 0 else c2
            # Float upward for fire, downward for ice
            y_off = -frame % 3 if enchant == "fire" else (frame % 3 if enchant == "ice" else 0)
            fy = py + y_off
            if 0 <= px < img.width and 0 <= fy < img.height:
                put_pixel(img, px, int(fy), color + (180,))


def _add_rarity_glow(img, rarity: str):
    """Add a 1px glow outline around the weapon for rarity tier."""
    if rarity == "common" or not rarity:
        return

    glow_colors = {
        "uncommon": wp.base("uncommon"),
        "rare": wp.base("rare"),
        "epic": wp.base("epic"),
        "legendary": wp.base("legendary"),
    }
    color = glow_colors.get(rarity)
    if not color:
        return

    glow_color = color + (100,)
    # Find all edge pixels (transparent pixel adjacent to opaque pixel)
    w, h = img.width, img.height
    glow_pixels = []
    for y in range(h):
        for x in range(w):
            _, _, _, a = get_pixel(img, x, y)
            if a == 0:
                # Check if adjacent to opaque pixel
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        _, _, _, na = get_pixel(img, nx, ny)
                        if na > 0:
                            glow_pixels.append((x, y))
                            break
    for gx, gy in glow_pixels:
        put_pixel(img, gx, gy, glow_color)


# ============================================================
# SWORD (static + slash animation)
# ============================================================

def _draw_sword(img, ox: int = 0, oy: int = 0):
    """Draw a 16x16 sword at offset."""
    # Handle (bottom)
    for y in range(11, 15):
        put_pixel(img, 7 + ox, y + oy, wp.base("wood"))
        put_pixel(img, 8 + ox, y + oy, wp.shadow("wood"))
    # Grip wrap
    put_pixel(img, 7 + ox, 12 + oy, wp.base("leather"))
    put_pixel(img, 8 + ox, 13 + oy, wp.base("leather"))
    # Pommel
    put_pixel(img, 7 + ox, 15 + oy, wp.base("gold_metal"))
    put_pixel(img, 8 + ox, 15 + oy, wp.shadow("gold_metal"))
    # Crossguard
    for x in range(5, 11):
        put_pixel(img, x + ox, 10 + oy, wp.base("gold_metal"))
    put_pixel(img, 5 + ox, 10 + oy, wp.highlight("gold_metal"))
    put_pixel(img, 10 + ox, 10 + oy, wp.shadow("gold_metal"))
    # Blade
    for y in range(2, 10):
        t = (y - 2) / 8.0
        put_pixel(img, 7 + ox, y + oy, wp.highlight("steel"))
        put_pixel(img, 8 + ox, y + oy, wp.base("steel"))
        # Blade widens slightly at base
        if y > 5:
            put_pixel(img, 6 + ox, y + oy, wp.base("steel"))
            put_pixel(img, 9 + ox, y + oy, wp.shadow("steel"))
    # Tip
    put_pixel(img, 7 + ox, 1 + oy, wp.highlight("steel"))
    put_pixel(img, 8 + ox, 2 + oy, wp.highlight("steel"))
    # Fuller (center line detail)
    for y in range(4, 9):
        put_pixel(img, 7 + ox, y + oy, wp.shadow("steel"))


def generate_sword() -> StaticSprite:
    """Static sword sprite."""
    img = new_sprite()
    _draw_sword(img)
    draw_outline_thick(img)
    return StaticSprite("weapon_sword", img, "weapons")


def generate_sword_slash() -> SpriteSheet:
    """Sword slash animation: 6 frames with swing arc + trail."""
    frames = []
    # Sword pixels (relative to pivot at 7,10)
    blade_pixels = []
    for y in range(1, 10):
        blade_pixels.append((7, y, wp.highlight("steel")))
        blade_pixels.append((8, y, wp.base("steel")))
        if y > 5:
            blade_pixels.append((6, y, wp.base("steel")))
            blade_pixels.append((9, y, wp.shadow("steel")))
    blade_pixels.append((7, 1, wp.highlight("steel")))
    # Guard
    for x in range(5, 11):
        blade_pixels.append((x, 10, wp.base("gold_metal")))

    pivot_x, pivot_y = 7.5, 12.0
    # Swing angles: anticipation -> swing -> follow-through
    angles = [-0.4, -0.2, 0.6, 1.4, 1.8, 1.6]  # radians

    for f, angle in enumerate(angles):
        img = new_sprite()
        t = f / 5.0
        eased = _smoothstep(t)

        _draw_rotated_pixels(img, blade_pixels, pivot_x, pivot_y, angle)

        # Trail effect on fast frames (2-4)
        if 2 <= f <= 4:
            prev_angle = angles[f - 1]
            mid_angle = (prev_angle + angle) / 2
            trail_color = wp.highlight("steel") + (80,)
            for ty in range(3, 9):
                tx, tty = _rotate_point(7, ty, pivot_x, pivot_y, mid_angle)
                if 0 <= tx < 16 and 0 <= tty < 16:
                    put_pixel(img, tx, tty, trail_color)

        draw_outline_thick(img)
        frames.append(img)

    return SpriteSheet("weapon_sword_slash", frames,
                       frame_durations_ms=[100, 60, 40, 50, 80, 100], loop=False)


# ============================================================
# AXE
# ============================================================

def _draw_axe(img, ox: int = 0, oy: int = 0):
    """Draw a battle axe."""
    # Handle
    for y in range(6, 15):
        put_pixel(img, 7 + ox, y + oy, wp.base("wood"))
        put_pixel(img, 8 + ox, y + oy, wp.shadow("dark_wood"))
    # Grip
    put_pixel(img, 7 + ox, 13 + oy, wp.base("leather"))
    put_pixel(img, 8 + ox, 12 + oy, wp.base("leather"))
    # Axe head (right side blade)
    for y in range(2, 7):
        width = 3 if y in (3, 4, 5) else 2
        for dx in range(width):
            x = 9 + dx + ox
            color = wp.highlight("iron") if dx == 0 else wp.base("iron")
            if dx == width - 1:
                color = wp.shadow("iron")
            put_pixel(img, x, y + oy, color)
    # Blade edge (bright)
    for y in range(3, 6):
        put_pixel(img, 11 + ox, y + oy, wp.highlight("steel"))
    # Top spike
    put_pixel(img, 8 + ox, 1 + oy, wp.base("iron"))
    put_pixel(img, 7 + ox, 2 + oy, wp.base("iron"))


def generate_axe() -> StaticSprite:
    img = new_sprite()
    _draw_axe(img)
    draw_outline_thick(img)
    return StaticSprite("weapon_axe", img, "weapons")


def generate_axe_chop() -> SpriteSheet:
    """Axe overhead chop animation."""
    frames = []
    axe_pixels = []
    # Head
    for y in range(2, 7):
        w = 3 if y in (3, 4, 5) else 2
        for dx in range(w):
            c = wp.highlight("iron") if dx == 0 else wp.base("iron")
            axe_pixels.append((9 + dx, y, c))
    # Handle
    for y in range(6, 14):
        axe_pixels.append((7, y, wp.base("wood")))
        axe_pixels.append((8, y, wp.shadow("wood")))

    pivot_x, pivot_y = 7.5, 14.0
    angles = [-1.2, -0.8, -0.2, 0.5, 0.8, 0.6]

    for f, angle in enumerate(angles):
        img = new_sprite()
        _draw_rotated_pixels(img, axe_pixels, pivot_x, pivot_y, angle)
        draw_outline_thick(img)
        frames.append(img)

    return SpriteSheet("weapon_axe_chop", frames,
                       frame_durations_ms=[100, 80, 40, 50, 80, 100], loop=False)


# ============================================================
# MACE
# ============================================================

def generate_mace() -> StaticSprite:
    img = new_sprite()
    # Handle
    for y in range(7, 15):
        put_pixel(img, 7, y, wp.base("wood"))
        put_pixel(img, 8, y, wp.shadow("dark_wood"))
    put_pixel(img, 7, 14, wp.base("leather"))
    # Head (circle)
    draw_circle(img, 7, 4, 3, wp.base("iron"), filled=True)
    # Highlight
    put_pixel(img, 6, 3, wp.highlight("steel"))
    put_pixel(img, 7, 3, wp.highlight("steel"))
    # Flanges (spikes)
    for dx, dy in [(-1, -3), (1, -3), (-3, -1), (3, -1), (-3, 1), (3, 1)]:
        px, py = 7 + dx, 4 + dy
        if 0 <= px < 16 and 0 <= py < 16:
            put_pixel(img, px, py, wp.base("iron"))
    draw_outline_thick(img)
    return StaticSprite("weapon_mace", img, "weapons")


def generate_mace_swing() -> SpriteSheet:
    """Mace wide swing animation."""
    frames = []
    angles = [-1.0, -0.5, 0.3, 1.0, 1.5, 1.2]
    for f, angle in enumerate(angles):
        img = new_sprite()
        pivot_x, pivot_y = 7.5, 14.0
        # Handle
        handle = [(7, y, wp.base("wood")) for y in range(7, 14)]
        handle += [(8, y, wp.shadow("wood")) for y in range(7, 14)]
        _draw_rotated_pixels(img, handle, pivot_x, pivot_y, angle)
        # Head
        head = []
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if dx * dx + dy * dy <= 9:
                    c = wp.highlight("steel") if dx + dy < -1 else wp.base("iron")
                    head.append((7 + dx, 4 + dy, c))
        _draw_rotated_pixels(img, head, pivot_x, pivot_y, angle)
        draw_outline_thick(img)
        frames.append(img)
    return SpriteSheet("weapon_mace_swing", frames,
                       frame_durations_ms=[100, 80, 40, 50, 80, 100], loop=False)


# ============================================================
# SPEAR
# ============================================================

def generate_spear() -> StaticSprite:
    img = new_sprite()
    # Shaft (full height)
    for y in range(3, 15):
        put_pixel(img, 7, y, wp.base("wood"))
        put_pixel(img, 8, y, wp.shadow("dark_wood"))
    # Spearhead (triangle)
    put_pixel(img, 7, 0, wp.highlight("steel"))
    put_pixel(img, 7, 1, wp.highlight("steel"))
    put_pixel(img, 8, 1, wp.base("steel"))
    put_pixel(img, 6, 2, wp.base("iron"))
    put_pixel(img, 7, 2, wp.highlight("steel"))
    put_pixel(img, 8, 2, wp.base("steel"))
    put_pixel(img, 9, 2, wp.shadow("iron"))
    # Binding
    put_pixel(img, 7, 3, wp.base("leather"))
    put_pixel(img, 8, 3, wp.base("leather"))
    draw_outline_thick(img)
    return StaticSprite("weapon_spear", img, "weapons")


def generate_spear_thrust() -> SpriteSheet:
    """Spear thrust animation: translate forward and back."""
    frames = []
    offsets_y = [0, -1, -3, -5, -3, 0]
    for f, y_off in enumerate(offsets_y):
        img = new_sprite()
        # Shaft
        for y in range(3, 15):
            py = y + y_off
            if 0 <= py < 16:
                put_pixel(img, 7, py, wp.base("wood"))
                put_pixel(img, 8, py, wp.shadow("dark_wood"))
        # Head
        for dy, pixels in enumerate([(7,), (7, 8), (6, 7, 8, 9)]):
            py = dy + y_off
            if 0 <= py < 16:
                for px in pixels:
                    c = wp.highlight("steel") if px == 7 else wp.base("steel")
                    put_pixel(img, px, py, c)
        # Thrust blur on fast frames
        if f in (2, 3):
            for y in range(0, 4):
                py = y + y_off + 4
                if 0 <= py < 16:
                    put_pixel(img, 7, py, wp.highlight("steel") + (60,))
        draw_outline_thick(img)
        frames.append(img)
    return SpriteSheet("weapon_spear_thrust", frames,
                       frame_durations_ms=[80, 60, 40, 50, 80, 100], loop=False)


# ============================================================
# DAGGER
# ============================================================

def generate_dagger() -> StaticSprite:
    img = new_sprite()
    # Handle
    for y in range(10, 14):
        put_pixel(img, 7, y, wp.base("dark_wood"))
        put_pixel(img, 8, y, wp.shadow("dark_wood"))
    put_pixel(img, 7, 14, wp.base("gold_metal"))  # pommel
    # Guard
    for x in range(6, 10):
        put_pixel(img, x, 9, wp.base("gold_metal"))
    # Blade (short, wide)
    for y in range(5, 9):
        put_pixel(img, 7, y, wp.highlight("steel"))
        put_pixel(img, 8, y, wp.base("steel"))
        if y >= 6:
            put_pixel(img, 6, y, wp.base("steel"))
            put_pixel(img, 9, y, wp.shadow("steel"))
    # Tip
    put_pixel(img, 7, 4, wp.highlight("steel"))
    draw_outline_thick(img)
    return StaticSprite("weapon_dagger", img, "weapons")


def generate_dagger_stab() -> SpriteSheet:
    """Quick dagger stab animation."""
    frames = []
    offsets_y = [0, -1, -4, -6, -3, 0]
    for f, y_off in enumerate(offsets_y):
        img = new_sprite()
        # Blade
        for y in range(4, 9):
            py = y + y_off
            if 0 <= py < 16:
                put_pixel(img, 7, py, wp.highlight("steel"))
                put_pixel(img, 8, py, wp.base("steel"))
        # Tip
        ty = 4 + y_off
        if 0 <= ty < 16:
            put_pixel(img, 7, ty, wp.highlight("steel"))
        # Guard
        gy = 9 + y_off
        if 0 <= gy < 16:
            for x in range(6, 10):
                put_pixel(img, x, gy, wp.base("gold_metal"))
        # Handle
        for y in range(10, 14):
            py = y + y_off
            if 0 <= py < 16:
                put_pixel(img, 7, py, wp.base("dark_wood"))
        draw_outline_thick(img)
        frames.append(img)
    return SpriteSheet("weapon_dagger_stab", frames,
                       frame_durations_ms=[60, 40, 30, 40, 60, 80], loop=False)


# ============================================================
# HAMMER
# ============================================================

def generate_hammer() -> StaticSprite:
    img = new_sprite()
    # Handle
    for y in range(7, 15):
        put_pixel(img, 7, y, wp.base("wood"))
        put_pixel(img, 8, y, wp.shadow("dark_wood"))
    put_pixel(img, 7, 14, wp.base("leather"))
    # Head (wide rectangle)
    draw_rect(img, 4, 3, 8, 4, wp.base("iron"), filled=True)
    # Shading
    for x in range(4, 12):
        put_pixel(img, x, 3, wp.highlight("steel"))
    for x in range(4, 12):
        put_pixel(img, x, 6, wp.shadow("iron"))
    # Center detail
    put_pixel(img, 7, 4, wp.shadow("iron"))
    put_pixel(img, 8, 4, wp.shadow("iron"))
    draw_outline_thick(img)
    return StaticSprite("weapon_hammer", img, "weapons")


# ============================================================
# SCYTHE
# ============================================================

def generate_scythe() -> StaticSprite:
    img = new_sprite()
    # Long handle (diagonal)
    for i in range(12):
        x = 4 + i // 2
        y = 15 - i
        if 0 <= x < 16 and 0 <= y < 16:
            put_pixel(img, x, y, wp.base("dark_wood"))
            if x + 1 < 16:
                put_pixel(img, x + 1, y, wp.shadow("dark_wood"))
    # Curved blade (arc from handle top)
    blade_points = [
        (10, 3), (11, 2), (12, 2), (13, 3), (13, 4),
        (12, 5), (11, 5), (10, 4),
    ]
    for bx, by in blade_points:
        put_pixel(img, bx, by, wp.base("steel"))
    # Edge highlight
    for bx, by in [(11, 2), (12, 2), (13, 3)]:
        put_pixel(img, bx, by, wp.highlight("steel"))
    # Inner shadow
    put_pixel(img, 11, 4, wp.shadow("iron"))
    put_pixel(img, 12, 4, wp.shadow("iron"))
    draw_outline_thick(img)
    return StaticSprite("weapon_scythe", img, "weapons")


# ============================================================
# BOW
# ============================================================

def _draw_bow_frame(img, string_pull: float = 0.0, show_arrow: bool = False):
    """Draw bow with configurable string pull (0=idle, 1=full draw)."""
    # Bow body (bezier-like curve)
    bow_points = [
        (5, 2), (4, 3), (3, 4), (3, 5), (3, 6), (3, 7),
        (3, 8), (3, 9), (3, 10), (4, 11), (5, 12),
    ]
    for bx, by in bow_points:
        put_pixel(img, bx, by, wp.base("wood"))
        put_pixel(img, bx - 1, by, wp.shadow("dark_wood"))

    # String
    string_offset = int(string_pull * 4)
    top = (5, 2)
    bot = (5, 12)
    mid_x = 5 + string_offset
    mid_y = 7

    # Upper string
    draw_line(img, top[0], top[1], mid_x, mid_y, wp.base("string"))
    # Lower string
    draw_line(img, mid_x, mid_y, bot[0], bot[1], wp.base("string"))

    # Arrow
    if show_arrow:
        arrow_x = mid_x + 1
        # Shaft
        for dx in range(5):
            if arrow_x + dx < 16:
                put_pixel(img, arrow_x + dx, 7, wp.base("arrow_shaft"))
        # Head
        if arrow_x + 5 < 16:
            put_pixel(img, arrow_x + 5, 7, wp.highlight("steel"))
            put_pixel(img, arrow_x + 5, 6, wp.base("steel"))
            put_pixel(img, arrow_x + 5, 8, wp.base("steel"))
        # Fletching
        put_pixel(img, arrow_x, 6, wp.base("fletching"))
        put_pixel(img, arrow_x, 8, wp.base("fletching"))


def generate_bow() -> StaticSprite:
    img = new_sprite()
    _draw_bow_frame(img, 0.0, True)
    draw_outline_thick(img)
    return StaticSprite("weapon_bow", img, "weapons")


def generate_bow_shoot() -> SpriteSheet:
    """Bow draw and release animation."""
    frames = []
    configs = [
        (0.0, True),   # idle with arrow
        (0.3, True),   # pulling
        (0.7, True),   # near full draw
        (1.0, True),   # full draw
        (0.0, False),  # released (string snaps back, arrow gone)
        (0.0, False),  # recovery
    ]
    for f, (pull, arrow) in enumerate(configs):
        img = new_sprite()
        _draw_bow_frame(img, pull, arrow)
        # Arrow flying away on release frame
        if f == 4:
            for dx in range(8, 15):
                put_pixel(img, dx, 7, wp.base("arrow_shaft"))
            put_pixel(img, 15, 7, wp.highlight("steel"))
            put_pixel(img, 15, 6, wp.base("steel"))
            put_pixel(img, 15, 8, wp.base("steel"))
        draw_outline_thick(img)
        frames.append(img)
    return SpriteSheet("weapon_bow_shoot", frames,
                       frame_durations_ms=[120, 100, 80, 120, 50, 100], loop=False)


# ============================================================
# CROSSBOW
# ============================================================

def generate_crossbow() -> StaticSprite:
    img = new_sprite()
    # Stock (horizontal)
    for x in range(3, 13):
        put_pixel(img, x, 8, wp.base("wood"))
        put_pixel(img, x, 9, wp.shadow("dark_wood"))
    # Prod (bow arms)
    for dy in range(-3, 4):
        bx = 3 - abs(dy) // 2
        put_pixel(img, bx, 8 + dy, wp.base("iron"))
    # String
    draw_line(img, 2, 5, 4, 8, wp.base("string"))
    draw_line(img, 4, 8, 2, 11, wp.base("string"))
    # Bolt
    for x in range(5, 12):
        put_pixel(img, x, 7, wp.base("arrow_shaft"))
    put_pixel(img, 12, 7, wp.highlight("steel"))
    # Trigger
    put_pixel(img, 9, 10, wp.base("iron"))
    put_pixel(img, 9, 11, wp.base("iron"))
    draw_outline_thick(img)
    return StaticSprite("weapon_crossbow", img, "weapons")


# ============================================================
# SHURIKEN
# ============================================================

def generate_shuriken_spin() -> SpriteSheet:
    """Spinning shuriken animation."""
    frames = []
    for f in range(8):
        img = new_sprite()
        angle = f * math.pi / 4
        cx, cy = 7.5, 7.5

        # 4-pointed star
        for point in range(4):
            a = angle + point * math.pi / 2
            # Outer point
            for r in range(1, 5):
                px = cx + math.cos(a) * r
                py = cy + math.sin(a) * r
                rpx, rpy = round(px), round(py)
                if 0 <= rpx < 16 and 0 <= rpy < 16:
                    c = wp.highlight("steel") if r < 3 else wp.base("iron")
                    put_pixel(img, rpx, rpy, c)

        # Center
        put_pixel(img, 7, 7, wp.shadow("dark_metal"))
        put_pixel(img, 8, 7, wp.shadow("dark_metal"))
        put_pixel(img, 7, 8, wp.shadow("dark_metal"))
        put_pixel(img, 8, 8, wp.shadow("dark_metal"))

        draw_outline_thick(img)
        frames.append(img)
    return SpriteSheet("weapon_shuriken_spin", frames, frame_duration_ms=60, loop=True)


# ============================================================
# STAFF (magic)
# ============================================================

def generate_staff() -> StaticSprite:
    img = new_sprite()
    # Shaft
    for y in range(4, 15):
        put_pixel(img, 7, y, wp.base("dark_wood"))
        put_pixel(img, 8, y, wp.shadow("dark_wood"))
    # Grip wrapping
    for y in range(10, 14, 2):
        put_pixel(img, 7, y, wp.base("leather"))
    # Crystal head
    put_pixel(img, 7, 1, wp.highlight("crystal"))
    put_pixel(img, 8, 1, wp.base("crystal"))
    put_pixel(img, 6, 2, wp.base("crystal"))
    put_pixel(img, 7, 2, wp.highlight("crystal"))
    put_pixel(img, 8, 2, wp.base("crystal"))
    put_pixel(img, 9, 2, wp.shadow("crystal"))
    put_pixel(img, 7, 3, wp.base("crystal"))
    put_pixel(img, 8, 3, wp.shadow("crystal"))
    # Glow dot
    put_pixel(img, 7, 2, (230, 240, 255))
    draw_outline_thick(img)
    return StaticSprite("weapon_staff", img, "weapons")


def generate_staff_charge() -> SpriteSheet:
    """Staff magical charge-up animation."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Shaft
        for y in range(4, 15):
            put_pixel(img, 7, y, wp.base("dark_wood"))
            put_pixel(img, 8, y, wp.shadow("dark_wood"))
        # Crystal
        for dx, dy, c in [(0, -1, "crystal"), (1, -1, "crystal"),
                           (-1, 0, "crystal"), (0, 0, "crystal"),
                           (1, 0, "crystal"), (2, 0, "crystal"),
                           (0, 1, "crystal"), (1, 1, "crystal")]:
            put_pixel(img, 7 + dx, 2 + dy, wp.base(c))

        # Growing glow
        glow_r = 1 + f // 2
        glow_alpha = min(200, 80 + f * 20)
        glow_color = wp.highlight("magic_blue") + (glow_alpha,)
        for dy in range(-glow_r, glow_r + 1):
            for dx in range(-glow_r, glow_r + 1):
                if dx * dx + dy * dy <= glow_r * glow_r:
                    gx, gy = 7 + dx, 2 + dy
                    if 0 <= gx < 16 and 0 <= gy < 16:
                        put_pixel(img, gx, gy, glow_color)

        # Sparkle particles
        for i in range(f // 2 + 1):
            a = f * 0.8 + i * 2.1
            r = glow_r + 1
            sx = 7 + round(math.cos(a) * r)
            sy = 2 + round(math.sin(a) * r)
            if 0 <= sx < 16 and 0 <= sy < 16:
                put_pixel(img, sx, sy, wp.highlight("magic_white"))

        draw_outline_thick(img)
        frames.append(img)
    return SpriteSheet("weapon_staff_charge", frames, frame_duration_ms=100, loop=False)


# ============================================================
# WAND
# ============================================================

def generate_wand() -> StaticSprite:
    img = new_sprite()
    # Shaft (thin)
    for y in range(5, 14):
        put_pixel(img, 7, y, wp.base("dark_wood"))
    put_pixel(img, 7, 13, wp.base("leather"))
    # Tip crystal
    put_pixel(img, 7, 3, wp.highlight("magic_purple"))
    put_pixel(img, 7, 4, wp.base("magic_purple"))
    put_pixel(img, 6, 4, wp.base("magic_purple"))
    put_pixel(img, 8, 4, wp.shadow("magic_purple"))
    # Glow
    put_pixel(img, 7, 3, (220, 200, 255))
    draw_outline_thick(img)
    return StaticSprite("weapon_wand", img, "weapons")


# ============================================================
# ORB
# ============================================================

def generate_orb_pulse() -> SpriteSheet:
    """Magic orb with pulsing glow animation."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Stand/holder
        put_pixel(img, 6, 12, wp.base("gold_metal"))
        put_pixel(img, 7, 11, wp.base("gold_metal"))
        put_pixel(img, 8, 11, wp.shadow("gold_metal"))
        put_pixel(img, 9, 12, wp.shadow("gold_metal"))
        put_pixel(img, 7, 12, wp.base("gold_metal"))
        put_pixel(img, 8, 12, wp.base("gold_metal"))

        # Orb body
        draw_circle(img, 7, 7, 4, wp.base("magic_blue"), filled=True)
        # Inner gradient
        draw_circle(img, 7, 7, 3, wp.highlight("magic_blue"), filled=True)
        draw_circle(img, 7, 7, 2, wp.base("crystal"), filled=True)

        # Pulsing highlight (moves with sine)
        hx = 6 + round(math.sin(f * math.pi / 4) * 0.8)
        hy = 5 + round(math.cos(f * math.pi / 4) * 0.8)
        put_pixel(img, hx, hy, wp.highlight("magic_white"))
        put_pixel(img, hx + 1, hy, (255, 255, 255))

        # Outer glow pulse
        glow_alpha = 60 + round(math.sin(f * math.pi / 4) * 40)
        glow_color = wp.base("magic_blue") + (glow_alpha,)
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                d = dx * dx + dy * dy
                if 16 < d <= 25:
                    gx, gy = 7 + dx, 7 + dy
                    if 0 <= gx < 16 and 0 <= gy < 16:
                        put_pixel(img, gx, gy, glow_color)

        draw_outline_thick(img)
        frames.append(img)
    return SpriteSheet("weapon_orb_pulse", frames, frame_duration_ms=120, loop=True)


# ============================================================
# SHIELDS
# ============================================================

def generate_round_shield() -> StaticSprite:
    img = new_sprite()
    # Shield body
    draw_circle(img, 7, 7, 5, wp.base("iron"), filled=True)
    draw_circle(img, 7, 7, 5, wp.shadow("iron"), filled=False)
    # Highlight
    draw_circle(img, 7, 7, 4, wp.highlight("steel"), filled=False)
    # Boss (center)
    draw_circle(img, 7, 7, 1, wp.base("gold_metal"), filled=True)
    put_pixel(img, 7, 7, wp.highlight("gold_metal"))
    # Rim detail
    for a_i in range(0, 360, 45):
        a = math.radians(a_i)
        rx = 7 + round(math.cos(a) * 5)
        ry = 7 + round(math.sin(a) * 5)
        if 0 <= rx < 16 and 0 <= ry < 16:
            put_pixel(img, rx, ry, wp.base("gold_metal"))
    draw_outline_thick(img)
    return StaticSprite("weapon_round_shield", img, "weapons")


def generate_kite_shield() -> StaticSprite:
    img = new_sprite()
    # Top rounded part
    for dy in range(-4, 1):
        half_w = round(math.sqrt(max(0, 16 - dy * dy)))
        for dx in range(-half_w, half_w + 1):
            px, py = 7 + dx, 5 + dy
            if 0 <= px < 16 and 0 <= py < 16:
                c = wp.highlight("iron") if dx < 0 else wp.base("iron")
                put_pixel(img, px, py, c)
    # Bottom triangle
    for dy in range(0, 7):
        half_w = max(0, 4 - dy)
        for dx in range(-half_w, half_w + 1):
            px, py = 7 + dx, 5 + dy
            if 0 <= px < 16 and 0 <= py < 16:
                c = wp.base("iron") if dx <= 0 else wp.shadow("iron")
                put_pixel(img, px, py, c)
    # Center stripe
    for y in range(2, 12):
        put_pixel(img, 7, y, wp.base("gold_metal"))
    # Cross
    for x in range(5, 10):
        put_pixel(img, x, 5, wp.base("gold_metal"))
    draw_outline_thick(img)
    return StaticSprite("weapon_kite_shield", img, "weapons")


def generate_tower_shield() -> StaticSprite:
    img = new_sprite()
    # Main body (tall rectangle with rounded top)
    draw_rect(img, 3, 4, 10, 10, wp.base("iron"), filled=True)
    # Rounded top
    for dx in range(-4, 5):
        py = 3 if abs(dx) < 4 else 4
        put_pixel(img, 7 + dx, py, wp.base("iron"))
    # Shading
    for y in range(3, 14):
        put_pixel(img, 3, y, wp.shadow("iron"))
        put_pixel(img, 12, y, wp.shadow("iron"))
        put_pixel(img, 4, y, wp.highlight("steel"))
    # Reinforcing bands
    for x in range(3, 13):
        put_pixel(img, x, 6, wp.shadow("iron"))
        put_pixel(img, x, 10, wp.shadow("iron"))
    # Boss
    put_pixel(img, 7, 8, wp.base("gold_metal"))
    put_pixel(img, 8, 8, wp.highlight("gold_metal"))
    draw_outline_thick(img)
    return StaticSprite("weapon_tower_shield", img, "weapons")


# ============================================================
# ENCHANTED VARIANTS (animated)
# ============================================================

def generate_fire_sword() -> SpriteSheet:
    """Fire-enchanted sword with flickering particles."""
    frames = []
    for f in range(8):
        img = new_sprite()
        _draw_sword(img)
        _add_enchantment_particles(img, "fire", f, seed=100)
        draw_outline_thick(img)
        frames.append(img)
    return SpriteSheet("weapon_fire_sword", frames, frame_duration_ms=100, loop=True)


def generate_ice_sword() -> SpriteSheet:
    """Ice-enchanted sword with frost crystals."""
    frames = []
    for f in range(8):
        img = new_sprite()
        _draw_sword(img)
        _add_enchantment_particles(img, "ice", f, seed=200)
        # Ice tint on blade
        for y in range(2, 10):
            for x in range(6, 10):
                r, g, b, a = get_pixel(img, x, y)
                if a > 0:
                    # Tint toward blue
                    nr = max(0, r - 40)
                    nb = min(255, b + 40)
                    put_pixel(img, x, y, (nr, g, nb, a))
        draw_outline_thick(img)
        frames.append(img)
    return SpriteSheet("weapon_ice_sword", frames, frame_duration_ms=120, loop=True)


def generate_lightning_axe() -> SpriteSheet:
    """Lightning-enchanted axe with sparks."""
    frames = []
    for f in range(8):
        img = new_sprite()
        _draw_axe(img)
        _add_enchantment_particles(img, "lightning", f, seed=300)
        # Flash every 3 frames
        if f % 3 == 0:
            for y in range(2, 7):
                for x in range(9, 12):
                    r, g, b, a = get_pixel(img, x, y)
                    if a > 0:
                        put_pixel(img, x, y, (min(255, r + 60), min(255, g + 60), min(255, b + 30), a))
        draw_outline_thick(img)
        frames.append(img)
    return SpriteSheet("weapon_lightning_axe", frames, frame_duration_ms=80, loop=True)


def generate_poison_dagger() -> SpriteSheet:
    """Poison-enchanted dagger with dripping effect."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Dagger base
        for y in range(10, 14):
            put_pixel(img, 7, y, wp.base("dark_wood"))
        for x in range(6, 10):
            put_pixel(img, x, 9, wp.base("gold_metal"))
        for y in range(4, 9):
            put_pixel(img, 7, y, wp.highlight("steel"))
            put_pixel(img, 8, y, wp.base("steel"))
        put_pixel(img, 7, 4, wp.highlight("steel"))

        # Green tint on blade
        for y in range(4, 9):
            for x in range(6, 10):
                r, g, b, a = get_pixel(img, x, y)
                if a > 0:
                    ng = min(255, g + 30)
                    put_pixel(img, x, y, (r, ng, b, a))

        _add_enchantment_particles(img, "poison", f, seed=400)

        # Drip animation
        drip_y = 9 + (f % 4)
        if drip_y < 16:
            put_pixel(img, 7, drip_y, wp.base("poison") + (180,))

        draw_outline_thick(img)
        frames.append(img)
    return SpriteSheet("weapon_poison_dagger", frames, frame_duration_ms=120, loop=True)


# ============================================================
# RARITY VARIANTS
# ============================================================

def generate_legendary_sword() -> StaticSprite:
    """Legendary tier sword with golden glow."""
    img = new_sprite()
    # Gold blade instead of steel
    for y in range(2, 10):
        put_pixel(img, 7, y, wp.highlight("gold_metal"))
        put_pixel(img, 8, y, wp.base("gold_metal"))
        if y > 5:
            put_pixel(img, 6, y, wp.base("gold_metal"))
            put_pixel(img, 9, y, wp.shadow("gold_metal"))
    put_pixel(img, 7, 1, wp.highlight("gold_metal"))
    # Guard (crystal)
    for x in range(5, 11):
        put_pixel(img, x, 10, wp.base("crystal"))
    # Handle
    for y in range(11, 15):
        put_pixel(img, 7, y, wp.base("leather"))
        put_pixel(img, 8, y, wp.shadow("leather"))
    put_pixel(img, 7, 15, wp.base("crystal"))
    draw_outline_thick(img)
    _add_rarity_glow(img, "legendary")
    return StaticSprite("weapon_legendary_sword", img, "weapons")


def generate_epic_staff() -> StaticSprite:
    """Epic tier staff with purple glow."""
    img = new_sprite()
    for y in range(4, 15):
        put_pixel(img, 7, y, wp.base("dark_wood"))
        put_pixel(img, 8, y, wp.shadow("dark_wood"))
    # Purple crystal
    put_pixel(img, 7, 1, wp.highlight("magic_purple"))
    put_pixel(img, 8, 1, wp.base("magic_purple"))
    put_pixel(img, 6, 2, wp.base("magic_purple"))
    put_pixel(img, 7, 2, wp.highlight("magic_purple"))
    put_pixel(img, 8, 2, wp.base("magic_purple"))
    put_pixel(img, 9, 2, wp.shadow("magic_purple"))
    put_pixel(img, 7, 3, wp.base("magic_purple"))
    put_pixel(img, 8, 3, wp.shadow("magic_purple"))
    put_pixel(img, 7, 2, (230, 200, 255))
    draw_outline_thick(img)
    _add_rarity_glow(img, "epic")
    return StaticSprite("weapon_epic_staff", img, "weapons")


# ============================================================
# GENERATE ALL
# ============================================================

def generate_all() -> list:
    """Generate all weapon sprites and animations."""
    return [
        # --- Static Weapons ---
        generate_sword(),
        generate_axe(),
        generate_mace(),
        generate_spear(),
        generate_dagger(),
        generate_hammer(),
        generate_scythe(),
        generate_bow(),
        generate_crossbow(),
        generate_wand(),
        generate_staff(),
        # --- Shields ---
        generate_round_shield(),
        generate_kite_shield(),
        generate_tower_shield(),
        # --- Attack Animations ---
        generate_sword_slash(),
        generate_axe_chop(),
        generate_mace_swing(),
        generate_spear_thrust(),
        generate_dagger_stab(),
        generate_bow_shoot(),
        generate_shuriken_spin(),
        generate_staff_charge(),
        generate_orb_pulse(),
        # --- Enchanted Variants ---
        generate_fire_sword(),
        generate_ice_sword(),
        generate_lightning_axe(),
        generate_poison_dagger(),
        # --- Rarity Variants ---
        generate_legendary_sword(),
        generate_epic_staff(),
    ]
