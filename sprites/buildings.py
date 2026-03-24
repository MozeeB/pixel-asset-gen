"""
Building asset generators: houses, shops, castle, church, tower, inn, blacksmith,
windmill, barn, well, fountain, bridge, ruins, dungeon entrance, lighthouse, tent.

Each building is 16x16 with optional animations (chimney smoke, window glow,
flag wave, windmill spin, fountain splash, torch flicker, lantern sway).
"""

import math
from engine.drawing import (
    new_sprite, put_pixel, draw_outline, draw_rect, draw_line,
    draw_circle, dither_fill,
)
from engine.palette import BUILDINGS as B, OBJECTS as OB, EFFECTS as EF
from engine.noise import noise_map
from engine.sprite import SpriteSheet, StaticSprite


# ============================================================
# HELPER: common building parts
# ============================================================

def _draw_stone_wall(img, x, y, w, h, seed=100):
    """Draw a stone wall block with noise-based texture."""
    nmap = noise_map(16, 16, seed=seed, octaves=2, base_scale=0.4)
    for py in range(y, y + h):
        for px in range(x, x + w):
            if 0 <= px < 16 and 0 <= py < 16:
                v = nmap[py][px]
                if v < 0.35:
                    put_pixel(img, px, py, B.shadow("stone_wall"))
                elif v < 0.65:
                    put_pixel(img, px, py, B.base("stone_wall"))
                else:
                    put_pixel(img, px, py, B.highlight("stone_wall"))


def _draw_brick_wall(img, x, y, w, h):
    """Draw a brick pattern wall."""
    for py in range(y, y + h):
        for px in range(x, x + w):
            row = (py - y)
            col = (px - x)
            # Brick pattern: offset every other row
            is_mortar = (row % 3 == 0) or ((col + (3 if row % 6 < 3 else 0)) % 6 == 0)
            if is_mortar:
                put_pixel(img, px, py, B.shadow("brick"))
            elif (col + row) % 5 == 0:
                put_pixel(img, px, py, B.highlight("brick"))
            else:
                put_pixel(img, px, py, B.base("brick"))


def _draw_wood_wall(img, x, y, w, h):
    """Draw vertical wood plank wall."""
    for py in range(y, y + h):
        for px in range(x, x + w):
            col = (px - x) % 4
            if col == 0:
                put_pixel(img, px, py, B.shadow("wood_wall"))
            elif col == 3:
                put_pixel(img, px, py, B.shadow("wood_wall"))
            elif (px + py) % 7 == 0:
                put_pixel(img, px, py, B.highlight("wood_wall"))
            else:
                put_pixel(img, px, py, B.base("wood_wall"))


def _draw_roof_peaked(img, x, y, w, color_key="roof_red"):
    """Draw a triangular peaked roof."""
    peak_x = x + w // 2
    rows = w // 2 + 1
    for ry in range(rows):
        left = peak_x - ry
        right = peak_x + ry
        for px in range(left, right + 1):
            if 0 <= px < 16 and 0 <= (y + ry) < 16:
                if px == left or px == right:
                    put_pixel(img, px, y + ry, B.shadow(color_key))
                elif ry % 2 == 0:
                    put_pixel(img, px, y + ry, B.highlight(color_key))
                else:
                    put_pixel(img, px, y + ry, B.base(color_key))
    return rows


def _draw_roof_flat(img, x, y, w, h, color_key="roof_slate"):
    """Draw a flat/sloped roof."""
    for py in range(y, y + h):
        for px in range(x, x + w):
            row = py - y
            if row == 0:
                put_pixel(img, px, py, B.shadow(color_key))
            elif (px + row) % 3 == 0:
                put_pixel(img, px, py, B.shadow(color_key))
            else:
                put_pixel(img, px, py, B.base(color_key))


def _draw_door(img, x, y, w=3, h=4):
    """Draw a small door."""
    draw_rect(img, x, y, w, h, B.base("door_wood"), filled=True)
    put_pixel(img, x, y, B.shadow("door_dark"))
    put_pixel(img, x + w - 1, y, B.shadow("door_dark"))
    # Handle
    put_pixel(img, x + w - 1, y + h // 2, B.highlight("gold_trim"))


def _draw_window(img, x, y, glowing=False, frame=2):
    """Draw a window with optional glow."""
    color = B.base("window_glow") if glowing else B.base("window_glass")
    for py in range(y, y + frame):
        for px in range(x, x + frame):
            put_pixel(img, px, py, color)
    # Frame
    put_pixel(img, x - 1, y, B.base("window_frame")) if x > 0 else None
    put_pixel(img, x + frame, y, B.base("window_frame")) if x + frame < 16 else None


def _draw_chimney(img, x, y, h=3):
    """Draw a chimney stack."""
    for py in range(y, y + h):
        put_pixel(img, x, py, B.base("chimney"))
        put_pixel(img, x + 1, py, B.highlight("chimney"))
    put_pixel(img, x, y, B.shadow("chimney"))
    put_pixel(img, x + 1, y, B.shadow("chimney"))


def _draw_smoke_puff(img, x, y, frame, seed=200):
    """Draw animated smoke rising from chimney."""
    t = frame * 0.5
    # 3 smoke particles rising and drifting
    particles = [
        (x, y - 1 - int(t * 1.2), 0.3),
        (x + int(math.sin(t * 2) * 0.8), y - 2 - int(t * 0.8), 0.5),
        (x - 1 + int(math.cos(t * 1.5)), y - 3 - int(t * 0.6), 0.7),
    ]
    for px, py, age in particles:
        alpha = max(0, int(200 * (1 - age * (frame / 8))))
        if alpha > 50 and 0 <= px < 16 and 0 <= py < 16:
            put_pixel(img, px, py, (*B.base("chimney_smoke"), alpha))


# ============================================================
# HOUSE (basic cottage)
# ============================================================

def generate_house_idle(seed: int = 1000) -> SpriteSheet:
    """Cozy cottage with chimney smoke animation."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Roof
        _draw_roof_peaked(img, 1, 1, 14, "roof_red")
        # Walls
        _draw_stone_wall(img, 2, 8, 12, 7, seed=seed)
        # Door
        _draw_door(img, 7, 11, 3, 4)
        # Windows
        glow = f % 4 < 2  # flicker
        _draw_window(img, 3, 10, glowing=glow)
        _draw_window(img, 11, 10, glowing=glow)
        # Chimney
        _draw_chimney(img, 12, 3, 5)
        # Smoke animation
        _draw_smoke_puff(img, 12, 2, f)
        frames.append(draw_outline(img))
    return SpriteSheet("house_idle", frames, frame_duration_ms=200, loop=True)


def generate_house_brick(seed: int = 1010) -> StaticSprite:
    """Brick house variant."""
    img = new_sprite()
    _draw_roof_peaked(img, 1, 1, 14, "roof_blue")
    _draw_brick_wall(img, 2, 8, 12, 7)
    _draw_door(img, 7, 11, 3, 4)
    _draw_window(img, 3, 10, glowing=True)
    _draw_window(img, 11, 10, glowing=True)
    _draw_chimney(img, 2, 3, 5)
    return StaticSprite("house_brick", draw_outline(img), category="buildings")


def generate_house_wood(seed: int = 1020) -> StaticSprite:
    """Wooden cabin."""
    img = new_sprite()
    _draw_roof_peaked(img, 1, 1, 14, "roof_thatch")
    _draw_wood_wall(img, 2, 8, 12, 7)
    _draw_door(img, 7, 11, 3, 4)
    _draw_window(img, 4, 10, glowing=False)
    _draw_window(img, 10, 10, glowing=False)
    return StaticSprite("house_wood", draw_outline(img), category="buildings")


# ============================================================
# SHOP
# ============================================================

def generate_shop_idle(seed: int = 1100) -> SpriteSheet:
    """Shop with animated lantern swing."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Flat roof
        _draw_roof_flat(img, 1, 2, 14, 3, "roof_slate")
        # Brick walls
        _draw_brick_wall(img, 1, 5, 14, 10)
        # Large display window
        for wy in range(7, 11):
            for wx in range(3, 8):
                put_pixel(img, wx, wy, B.base("window_glass"))
        # Door
        _draw_door(img, 10, 11, 3, 4)
        # Sign hanging
        swing = math.sin(f * math.pi / 4) * 1.5
        sx = 8 + int(swing * 0.3)
        for sy in range(3, 5):
            put_pixel(img, sx, sy, B.base("sign_wood"))
            put_pixel(img, sx + 1, sy, B.highlight("sign_wood"))
        # Lantern glow
        glow_alpha = int(180 + 60 * math.sin(f * math.pi / 3))
        lx, ly = 1, 5
        put_pixel(img, lx, ly, (*B.base("lantern")[:3], min(255, glow_alpha)))
        frames.append(draw_outline(img))
    return SpriteSheet("shop_idle", frames, frame_duration_ms=150, loop=True)


# ============================================================
# CASTLE
# ============================================================

def generate_castle_idle(seed: int = 1200) -> SpriteSheet:
    """Castle with animated flag."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Main tower
        _draw_stone_wall(img, 4, 4, 8, 11, seed=seed)
        # Battlements
        for bx in range(4, 13, 2):
            put_pixel(img, bx, 3, B.base("stone_wall"))
            put_pixel(img, bx, 2, B.highlight("stone_wall"))
        # Gate
        for gy in range(11, 15):
            put_pixel(img, 7, gy, B.base("door_dark"))
            put_pixel(img, 8, gy, B.base("door_dark"))
        # Arch
        put_pixel(img, 7, 10, B.shadow("stone_dark"))
        put_pixel(img, 8, 10, B.shadow("stone_dark"))
        # Side turrets
        for tx in [1, 13]:
            draw_rect(img, tx, 5, 3, 10, B.base("stone_wall"), filled=True)
            put_pixel(img, tx, 4, B.highlight("stone_wall"))
            put_pixel(img, tx + 1, 4, B.highlight("stone_wall"))
            put_pixel(img, tx + 2, 4, B.highlight("stone_wall"))
        # Arrow slits
        put_pixel(img, 2, 8, B.base("door_dark"))
        put_pixel(img, 14, 8, B.base("door_dark"))
        # Windows on main
        _draw_window(img, 6, 6, glowing=(f % 3 == 0))
        _draw_window(img, 9, 6, glowing=(f % 3 == 1))
        # Flag animation
        flag_wave = math.sin(f * math.pi / 4)
        fx = 8
        # Pole
        for fy in range(0, 3):
            put_pixel(img, fx, fy, B.base("iron_bar"))
        # Flag cloth
        flag_y = 0
        for fi in range(3):
            flag_px = fx + 1 + fi
            flag_py = flag_y + int(flag_wave * (fi * 0.3))
            if 0 <= flag_px < 16 and 0 <= flag_py < 16:
                put_pixel(img, flag_px, flag_py, B.base("flag"))
                if flag_py + 1 < 16:
                    put_pixel(img, flag_px, flag_py + 1, B.shadow("flag"))
        frames.append(draw_outline(img))
    return SpriteSheet("castle_idle", frames, frame_duration_ms=150, loop=True)


# ============================================================
# CHURCH
# ============================================================

def generate_church(seed: int = 1300) -> StaticSprite:
    """Church with steeple and cross."""
    img = new_sprite()
    # Steeple
    for ry in range(4):
        cx = 8
        left = cx - ry
        right = cx + ry
        for px in range(left, right + 1):
            put_pixel(img, px, 3 + ry, B.base("roof_slate"))
    # Cross
    put_pixel(img, 8, 0, B.base("gold_trim"))
    put_pixel(img, 8, 1, B.base("gold_trim"))
    put_pixel(img, 8, 2, B.base("gold_trim"))
    put_pixel(img, 7, 1, B.base("gold_trim"))
    put_pixel(img, 9, 1, B.base("gold_trim"))
    # Body
    _draw_stone_wall(img, 3, 7, 10, 8, seed=seed)
    # Rose window
    draw_circle(img, 8, 9, 2, B.base("window_glass"), filled=True)
    put_pixel(img, 8, 9, B.base("window_glow"))
    # Door
    _draw_door(img, 7, 12, 3, 3)
    return StaticSprite("church", draw_outline(img), category="buildings")


# ============================================================
# TOWER (wizard tower)
# ============================================================

def generate_tower_idle(seed: int = 1400) -> SpriteSheet:
    """Wizard tower with pulsing crystal glow."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Conical roof
        for ry in range(5):
            cx = 8
            half = ry
            for px in range(cx - half, cx + half + 1):
                put_pixel(img, px, ry, B.base("roof_blue"))
        # Crystal on top
        glow = int(150 + 100 * math.sin(f * math.pi / 4))
        put_pixel(img, 8, 0, (*B.base("crystal_glow")[:3], min(255, glow)))
        # Tower body (narrow and tall)
        _draw_stone_wall(img, 5, 5, 6, 10, seed=seed)
        # Windows spiral
        window_positions = [(6, 7), (9, 9), (6, 11), (9, 13)]
        for i, (wx, wy) in enumerate(window_positions):
            glow_on = (f + i) % 4 < 2
            _draw_window(img, wx, wy, glowing=glow_on, frame=1)
        # Base
        draw_rect(img, 4, 14, 8, 2, B.base("stone_dark"), filled=True)
        frames.append(draw_outline(img))
    return SpriteSheet("tower_idle", frames, frame_duration_ms=180, loop=True)


# ============================================================
# INN / TAVERN
# ============================================================

def generate_inn_idle(seed: int = 1500) -> SpriteSheet:
    """Tavern with flickering warm window lights."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Wide roof
        _draw_roof_flat(img, 0, 1, 16, 3, "roof_thatch")
        # Wood walls
        _draw_wood_wall(img, 0, 4, 16, 11)
        # Large windows with warm glow
        flicker = 0.6 + 0.4 * math.sin(f * math.pi / 3)
        for wy in range(6, 10):
            for wx in range(2, 6):
                alpha = int(200 * flicker)
                put_pixel(img, wx, wy, (*B.base("window_glow")[:3], alpha))
            for wx in range(10, 14):
                alpha = int(200 * flicker * 0.8)
                put_pixel(img, wx, wy, (*B.base("window_glow")[:3], alpha))
        # Door (wide double door)
        draw_rect(img, 7, 10, 3, 5, B.base("door_wood"), filled=True)
        put_pixel(img, 7, 12, B.base("gold_trim"))
        put_pixel(img, 9, 12, B.base("gold_trim"))
        # Sign
        draw_rect(img, 6, 4, 4, 2, B.base("sign_wood"), filled=True)
        # Chimney smoke
        _draw_chimney(img, 14, 0, 2)
        _draw_smoke_puff(img, 14, -1, f)
        frames.append(draw_outline(img))
    return SpriteSheet("inn_idle", frames, frame_duration_ms=150, loop=True)


# ============================================================
# BLACKSMITH
# ============================================================

def generate_blacksmith_idle(seed: int = 1600) -> SpriteSheet:
    """Blacksmith forge with fire glow animation."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Roof
        _draw_roof_flat(img, 1, 2, 14, 3, "roof_slate")
        # Stone walls
        _draw_stone_wall(img, 1, 5, 14, 10, seed=seed)
        # Open forge area (left side)
        for fy in range(8, 14):
            for fx in range(2, 6):
                put_pixel(img, fx, fy, B.base("dark_stone"))
        # Forge fire animation
        fire_intensity = 0.5 + 0.5 * math.sin(f * math.pi / 3)
        fire_colors = [
            EF.base("fire_hot"),
            EF.base("fire_mid"),
            EF.base("fire_cool"),
        ]
        for fy in range(10, 13):
            for fx in range(3, 5):
                ci = int((fy - 10) * fire_intensity * 2) % 3
                alpha = int(200 + 55 * math.sin(f * math.pi / 2 + fx))
                put_pixel(img, fx, fy, (*fire_colors[ci], min(255, alpha)))
        # Anvil
        put_pixel(img, 7, 13, B.base("iron_bar"))
        put_pixel(img, 8, 13, B.highlight("iron_bar"))
        put_pixel(img, 7, 12, B.base("iron_bar"))
        # Door
        _draw_door(img, 10, 11, 3, 4)
        # Window
        _draw_window(img, 11, 7, glowing=(f % 2 == 0))
        frames.append(draw_outline(img))
    return SpriteSheet("blacksmith_idle", frames, frame_duration_ms=120, loop=True)


# ============================================================
# WINDMILL
# ============================================================

def generate_windmill_spin(seed: int = 1700) -> SpriteSheet:
    """Windmill with rotating blades."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Body (tapered)
        for py in range(6, 15):
            half = 2 + (py - 6) // 3
            cx = 8
            for px in range(cx - half, cx + half + 1):
                if (px + py) % 5 == 0:
                    put_pixel(img, px, py, B.highlight("plaster"))
                else:
                    put_pixel(img, px, py, B.base("plaster"))
        # Roof cap
        for ry in range(3):
            for px in range(7 - ry, 10 + ry):
                put_pixel(img, px, 5 - ry, B.base("roof_slate"))
        # Door
        put_pixel(img, 8, 14, B.base("door_wood"))
        put_pixel(img, 8, 13, B.base("door_wood"))
        # Window
        put_pixel(img, 8, 9, B.base("window_glass"))
        # Spinning blades (4 blades, rotating)
        angle = f * math.pi / 4  # 45 degrees per frame
        blade_length = 5
        hub_x, hub_y = 8, 5
        put_pixel(img, hub_x, hub_y, B.base("iron_bar"))
        for blade in range(4):
            blade_angle = angle + blade * math.pi / 2
            for dist in range(1, blade_length + 1):
                bx = hub_x + int(math.cos(blade_angle) * dist)
                by = hub_y + int(math.sin(blade_angle) * dist)
                if 0 <= bx < 16 and 0 <= by < 16:
                    put_pixel(img, bx, by, B.base("wood_dark"))
                    # Cross-bar on blade tips
                    if dist == blade_length:
                        perp_angle = blade_angle + math.pi / 2
                        for pd in range(-1, 2):
                            ppx = bx + int(math.cos(perp_angle) * pd)
                            ppy = by + int(math.sin(perp_angle) * pd)
                            if 0 <= ppx < 16 and 0 <= ppy < 16:
                                put_pixel(img, ppx, ppy, B.base("wood_wall"))
        frames.append(draw_outline(img))
    return SpriteSheet("windmill_spin", frames, frame_duration_ms=150, loop=True)


# ============================================================
# BARN
# ============================================================

def generate_barn(seed: int = 1800) -> StaticSprite:
    """Red barn with hay loft."""
    img = new_sprite()
    # Gambrel roof
    for ry in range(3):
        half = 1 + ry * 2
        cx = 8
        for px in range(cx - half, cx + half + 1):
            put_pixel(img, px, 2 + ry, B.base("roof_red"))
    # Walls
    _draw_wood_wall(img, 2, 5, 12, 10)
    # Recolor to red barn
    for py in range(5, 15):
        for px in range(2, 14):
            if img.getpixel((px, py))[3] > 0:
                v = (px + py) % 4
                if v == 0:
                    put_pixel(img, px, py, B.shadow("brick"))
                elif v == 3:
                    put_pixel(img, px, py, B.highlight("brick"))
                else:
                    put_pixel(img, px, py, B.base("brick"))
    # Barn doors (large)
    draw_rect(img, 6, 9, 5, 6, B.base("door_wood"), filled=True)
    put_pixel(img, 7, 12, B.base("gold_trim"))
    put_pixel(img, 9, 12, B.base("gold_trim"))
    # Hay loft opening
    put_pixel(img, 7, 5, B.base("sign_wood"))
    put_pixel(img, 8, 5, B.highlight("sign_wood"))
    put_pixel(img, 9, 5, B.base("sign_wood"))
    return StaticSprite("barn", draw_outline(img), category="buildings")


# ============================================================
# WELL
# ============================================================

def generate_well_idle(seed: int = 1900) -> SpriteSheet:
    """Stone well with shimmering water animation."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Stone base (circular top-down view)
        for py in range(7, 14):
            for px in range(4, 12):
                dx = px - 8
                dy = py - 10
                if dx * dx + dy * dy <= 16:
                    put_pixel(img, px, py, B.base("stone_wall"))
        # Inner water
        for py in range(8, 13):
            for px in range(5, 11):
                dx = px - 8
                dy = py - 10
                if dx * dx + dy * dy <= 9:
                    shimmer = math.sin(f * math.pi / 4 + px * 0.5) * 0.3
                    if shimmer > 0.1:
                        put_pixel(img, px, py, OB.highlight("water_mid"))
                    else:
                        put_pixel(img, px, py, OB.base("water_deep"))
        # Roof posts
        put_pixel(img, 4, 4, B.base("wood_dark"))
        put_pixel(img, 4, 5, B.base("wood_dark"))
        put_pixel(img, 4, 6, B.base("wood_dark"))
        put_pixel(img, 11, 4, B.base("wood_dark"))
        put_pixel(img, 11, 5, B.base("wood_dark"))
        put_pixel(img, 11, 6, B.base("wood_dark"))
        # Roof beam
        for px in range(4, 12):
            put_pixel(img, px, 3, B.base("wood_wall"))
        # Small peaked roof
        for px in range(5, 11):
            put_pixel(img, px, 2, B.base("roof_thatch"))
        for px in range(6, 10):
            put_pixel(img, px, 1, B.base("roof_thatch"))
        # Bucket rope
        rope_swing = int(math.sin(f * math.pi / 4) * 0.8)
        put_pixel(img, 8 + rope_swing, 4, B.base("sign_wood"))
        put_pixel(img, 8 + rope_swing, 5, B.base("sign_wood"))
        frames.append(draw_outline(img))
    return SpriteSheet("well_idle", frames, frame_duration_ms=200, loop=True)


# ============================================================
# FOUNTAIN
# ============================================================

def generate_fountain_splash(seed: int = 2000) -> SpriteSheet:
    """Fountain with animated water splash."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Base pool
        for py in range(10, 15):
            for px in range(2, 14):
                dx = px - 8
                dy = py - 12
                if dx * dx * 0.5 + dy * dy <= 6:
                    shimmer = math.sin(f * math.pi / 4 + px) * 0.3
                    if shimmer > 0.1:
                        put_pixel(img, px, py, OB.highlight("water_mid"))
                    else:
                        put_pixel(img, px, py, OB.base("water_mid"))
        # Pool rim
        for px in range(3, 13):
            put_pixel(img, px, 10, B.base("stone_wall"))
            put_pixel(img, px, 14, B.base("stone_wall"))
        for py in range(10, 15):
            put_pixel(img, 2, py, B.base("stone_wall"))
            put_pixel(img, 13, py, B.base("stone_wall"))
        # Center pedestal
        put_pixel(img, 7, 8, B.base("stone_wall"))
        put_pixel(img, 8, 8, B.base("stone_wall"))
        put_pixel(img, 7, 9, B.base("stone_wall"))
        put_pixel(img, 8, 9, B.base("stone_wall"))
        # Water spout animation
        spout_height = 3 + int(math.sin(f * math.pi / 4) * 1.5)
        for sy in range(max(0, 8 - spout_height), 8):
            alpha = int(180 - (8 - sy) * 20)
            if alpha > 0:
                put_pixel(img, 7, sy, (*OB.base("water_foam")[:3], alpha))
                put_pixel(img, 8, sy, (*OB.base("water_foam")[:3], alpha))
        # Splash particles
        num_drops = 4
        for d in range(num_drops):
            angle = (f * math.pi / 4) + d * math.pi / 2
            drop_t = (f % 4) / 4.0
            dx = int(math.cos(angle) * (2 + drop_t * 3))
            dy = int(-2 + drop_t * 5)
            dpx = 8 + dx
            dpy = 6 + dy
            if 0 <= dpx < 16 and 0 <= dpy < 16 and drop_t < 0.8:
                put_pixel(img, dpx, dpy, OB.base("water_foam"))
        frames.append(draw_outline(img))
    return SpriteSheet("fountain_splash", frames, frame_duration_ms=120, loop=True)


# ============================================================
# BRIDGE
# ============================================================

def generate_bridge(seed: int = 2100) -> StaticSprite:
    """Wooden bridge segment."""
    img = new_sprite()
    # Planks (horizontal)
    for py in range(5, 11):
        for px in range(0, 16):
            if py % 3 == 0:
                put_pixel(img, px, py, B.shadow("wood_wall"))
            elif (px + py) % 5 == 0:
                put_pixel(img, px, py, B.highlight("wood_wall"))
            else:
                put_pixel(img, px, py, B.base("wood_wall"))
    # Railings
    for px in range(0, 16, 4):
        for py in range(2, 5):
            put_pixel(img, px, py, B.base("wood_dark"))
        for py in range(11, 14):
            put_pixel(img, px, py, B.base("wood_dark"))
    # Railing bars
    for px in range(0, 16):
        put_pixel(img, px, 4, B.base("wood_wall"))
        put_pixel(img, px, 11, B.base("wood_wall"))
    return StaticSprite("bridge", draw_outline(img), category="buildings")


# ============================================================
# RUINS
# ============================================================

def generate_ruins(seed: int = 2200) -> StaticSprite:
    """Crumbling ancient ruins."""
    img = new_sprite()
    nmap = noise_map(16, 16, seed=seed, octaves=3, base_scale=0.3)
    # Broken walls at different heights
    wall_heights = [8, 5, 10, 6, 12, 7, 9, 4, 11, 6, 8, 5, 10, 7]
    for px in range(1, 15):
        idx = px - 1
        if idx < len(wall_heights):
            max_h = wall_heights[idx]
            for py in range(15 - max_h, 15):
                v = nmap[py][px]
                # Skip some pixels for broken look
                if v > 0.8 and py < 15 - max_h + 3:
                    continue
                if v < 0.35:
                    put_pixel(img, px, py, B.shadow("stone_dark"))
                elif v < 0.65:
                    put_pixel(img, px, py, B.base("stone_dark"))
                else:
                    put_pixel(img, px, py, B.highlight("stone_dark"))
    # Moss/vine growth
    for px in range(2, 14):
        for py in range(10, 15):
            if nmap[py][px] > 0.7:
                put_pixel(img, px, py, OB.base("rock_moss"))
    return StaticSprite("ruins", draw_outline(img), category="buildings")


# ============================================================
# DUNGEON ENTRANCE
# ============================================================

def generate_dungeon_entrance_idle(seed: int = 2300) -> SpriteSheet:
    """Dungeon entrance with flickering torch animation."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Stone archway
        _draw_stone_wall(img, 2, 2, 5, 13, seed=seed)
        _draw_stone_wall(img, 9, 2, 5, 13, seed=seed + 50)
        # Arch top
        for px in range(4, 12):
            put_pixel(img, px, 3, B.base("stone_dark"))
            put_pixel(img, px, 2, B.base("stone_dark"))
        # Keystone
        put_pixel(img, 7, 1, B.highlight("stone_wall"))
        put_pixel(img, 8, 1, B.highlight("stone_wall"))
        # Dark interior
        for py in range(4, 15):
            for px in range(7, 9):
                put_pixel(img, px, py, (15, 10, 20, 255))
        for py in range(5, 15):
            for px in range(5, 11):
                if 7 <= px <= 8:
                    continue
                if px >= 6 and px <= 9:
                    put_pixel(img, px, py, (20, 15, 25, 255))
        # Torches on pillars
        fire_colors = [EF.base("fire_hot"), EF.base("fire_mid"), EF.base("fire_cool")]
        for tx in [3, 12]:
            # Torch bracket
            put_pixel(img, tx, 5, B.base("iron_bar"))
            # Flame
            flame_offset = int(math.sin(f * math.pi / 3 + tx) * 0.7)
            fc = fire_colors[(f + tx) % 3]
            put_pixel(img, tx, 4 + flame_offset, fc)
            if 0 <= 3 + flame_offset < 16:
                put_pixel(img, tx, 3 + flame_offset, fire_colors[0])
        # Iron gate bars
        for px in range(6, 10):
            if px % 2 == 0:
                for py in range(5, 10):
                    put_pixel(img, px, py, B.base("iron_bar"))
        frames.append(draw_outline(img))
    return SpriteSheet("dungeon_entrance_idle", frames, frame_duration_ms=130, loop=True)


# ============================================================
# LIGHTHOUSE
# ============================================================

def generate_lighthouse_idle(seed: int = 2400) -> SpriteSheet:
    """Lighthouse with rotating beacon light."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Tower body (narrow, tapered)
        for py in range(4, 15):
            half = 1 + (py - 4) // 4
            cx = 8
            for px in range(cx - half, cx + half + 1):
                stripe = py % 4 < 2
                if stripe:
                    put_pixel(img, px, py, B.base("plaster"))
                else:
                    put_pixel(img, px, py, B.base("brick"))
        # Lantern room
        draw_rect(img, 6, 2, 4, 2, B.base("window_glass"), filled=True)
        # Beacon glow (rotating)
        beacon_angle = f * math.pi / 4
        beam_dx = int(math.cos(beacon_angle) * 4)
        beam_dy = int(math.sin(beacon_angle) * 2)
        for dist in range(1, 5):
            bx = 8 + int(beam_dx * dist / 4)
            by = 3 + int(beam_dy * dist / 4)
            if 0 <= bx < 16 and 0 <= by < 16:
                alpha = max(0, 255 - dist * 50)
                put_pixel(img, bx, by, (*B.base("lantern")[:3], alpha))
        # Roof
        put_pixel(img, 7, 1, B.base("roof_red"))
        put_pixel(img, 8, 1, B.base("roof_red"))
        put_pixel(img, 7, 0, B.base("roof_red"))
        put_pixel(img, 8, 0, B.base("roof_red"))
        # Base
        draw_rect(img, 5, 14, 6, 2, B.base("stone_wall"), filled=True)
        frames.append(draw_outline(img))
    return SpriteSheet("lighthouse_idle", frames, frame_duration_ms=150, loop=True)


# ============================================================
# TENT
# ============================================================

def generate_tent(seed: int = 2500) -> StaticSprite:
    """Camping/merchant tent."""
    img = new_sprite()
    # Tent body (triangular)
    for ry in range(10):
        cx = 8
        half = ry
        y = 3 + ry
        for px in range(cx - half, cx + half + 1):
            dist_from_center = abs(px - cx)
            if dist_from_center < half * 0.5:
                put_pixel(img, px, y, B.highlight("flag"))
            elif dist_from_center < half * 0.8:
                put_pixel(img, px, y, B.base("flag"))
            else:
                put_pixel(img, px, y, B.shadow("flag"))
    # Tent pole top
    put_pixel(img, 8, 2, B.base("wood_dark"))
    put_pixel(img, 8, 1, B.base("wood_dark"))
    # Flag/pennant
    put_pixel(img, 9, 1, B.base("banner"))
    put_pixel(img, 10, 1, B.base("banner"))
    put_pixel(img, 9, 2, B.shadow("banner"))
    # Opening
    for py in range(10, 14):
        put_pixel(img, 7, py, B.shadow("flag"))
        put_pixel(img, 9, py, B.shadow("flag"))
    return StaticSprite("tent", draw_outline(img), category="buildings")


# ============================================================
# WATCHTOWER
# ============================================================

def generate_watchtower_idle(seed: int = 2600) -> SpriteSheet:
    """Watchtower with animated torch."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Wooden structure (open frame)
        # Four posts
        for py in range(3, 15):
            put_pixel(img, 3, py, B.base("wood_dark"))
            put_pixel(img, 12, py, B.base("wood_dark"))
        # Cross braces
        for i in range(10):
            t = i / 10.0
            bx = int(3 + t * 9)
            by = int(7 + t * 7)
            put_pixel(img, bx, by, B.base("wood_wall"))
        # Platform
        for px in range(2, 14):
            put_pixel(img, px, 5, B.base("wood_wall"))
            put_pixel(img, px, 6, B.shadow("wood_wall"))
        # Railing
        for px in range(2, 14):
            put_pixel(img, px, 3, B.base("wood_wall"))
        # Roof
        for px in range(1, 15):
            put_pixel(img, px, 1, B.base("roof_thatch"))
            put_pixel(img, px, 2, B.shadow("roof_thatch"))
        # Torch
        fire_colors = [EF.base("fire_hot"), EF.base("fire_mid"), EF.base("fire_cool")]
        fc = fire_colors[f % 3]
        put_pixel(img, 7, 3, B.base("wood_dark"))  # bracket
        put_pixel(img, 7, 2, fc)
        frames.append(draw_outline(img))
    return SpriteSheet("watchtower_idle", frames, frame_duration_ms=140, loop=True)


# ============================================================
# CRYSTAL CAVE ENTRANCE
# ============================================================

def generate_crystal_cave_idle(seed: int = 2700) -> SpriteSheet:
    """Crystal cave entrance with pulsing crystal glow."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Rock formation around cave
        nmap = noise_map(16, 16, seed=seed, octaves=2, base_scale=0.3)
        for py in range(3, 15):
            for px in range(1, 15):
                # Cave opening in center
                dx = px - 8
                dy = py - 10
                if dx * dx * 0.7 + dy * dy * 0.4 < 8:
                    put_pixel(img, px, py, (15, 10, 25, 255))  # dark interior
                    continue
                v = nmap[py][px]
                if v > 0.3:
                    if v < 0.55:
                        put_pixel(img, px, py, B.shadow("dark_stone"))
                    else:
                        put_pixel(img, px, py, B.base("dark_stone"))
        # Crystals with pulsing glow
        crystal_positions = [(4, 5), (11, 6), (3, 10), (12, 9), (7, 3)]
        for i, (cx, cy) in enumerate(crystal_positions):
            glow_phase = math.sin(f * math.pi / 4 + i * 1.2)
            alpha = int(150 + 100 * glow_phase)
            put_pixel(img, cx, cy, (*B.base("crystal_glow")[:3], min(255, alpha)))
            put_pixel(img, cx, cy - 1, (*B.base("crystal_wall")[:3], min(255, alpha - 30)))
            if cy + 1 < 16:
                put_pixel(img, cx, cy + 1, (*B.base("crystal_wall")[:3], min(255, alpha - 60)))
        frames.append(draw_outline(img))
    return SpriteSheet("crystal_cave_idle", frames, frame_duration_ms=160, loop=True)


# ============================================================
# MARKET STALL
# ============================================================

def generate_market_stall(seed: int = 2800) -> StaticSprite:
    """Open-air market stall with awning."""
    img = new_sprite()
    # Awning (striped)
    for py in range(2, 5):
        for px in range(1, 15):
            stripe = (px // 2) % 2 == 0
            if stripe:
                put_pixel(img, px, py, B.base("flag"))
            else:
                put_pixel(img, px, py, B.base("plaster"))
    # Support poles
    put_pixel(img, 1, 5, B.base("wood_dark"))
    put_pixel(img, 1, 6, B.base("wood_dark"))
    put_pixel(img, 14, 5, B.base("wood_dark"))
    put_pixel(img, 14, 6, B.base("wood_dark"))
    # Counter
    for px in range(2, 14):
        put_pixel(img, px, 10, B.base("wood_wall"))
        put_pixel(img, px, 11, B.shadow("wood_wall"))
    # Shelves with items
    for px in range(3, 13):
        put_pixel(img, px, 7, B.base("wood_wall"))
    # Goods on display (colored blocks for items)
    item_colors = [(220, 40, 40), (40, 160, 40), (40, 80, 220), (220, 180, 40)]
    for i, color in enumerate(item_colors):
        put_pixel(img, 4 + i * 2, 9, color)
        put_pixel(img, 5 + i * 2, 9, color)
    # Ground cloth
    for px in range(2, 14):
        put_pixel(img, px, 14, B.base("banner"))
    return StaticSprite("market_stall", draw_outline(img), category="buildings")


# ============================================================
# GENERATE ALL
# ============================================================

def generate_all(seed_offset: int = 0) -> list:
    """Generate all building assets. Returns list of SpriteSheet and StaticSprite."""
    so = seed_offset
    return [
        # Animated buildings
        generate_house_idle(seed=1000 + so),
        generate_shop_idle(seed=1100 + so),
        generate_castle_idle(seed=1200 + so),
        generate_tower_idle(seed=1400 + so),
        generate_inn_idle(seed=1500 + so),
        generate_blacksmith_idle(seed=1600 + so),
        generate_windmill_spin(seed=1700 + so),
        generate_well_idle(seed=1900 + so),
        generate_fountain_splash(seed=2000 + so),
        generate_dungeon_entrance_idle(seed=2300 + so),
        generate_lighthouse_idle(seed=2400 + so),
        generate_watchtower_idle(seed=2600 + so),
        generate_crystal_cave_idle(seed=2700 + so),
        # Static buildings
        generate_house_brick(seed=1010 + so),
        generate_house_wood(seed=1020 + so),
        generate_church(seed=1300 + so),
        generate_barn(seed=1800 + so),
        generate_bridge(seed=2100 + so),
        generate_ruins(seed=2200 + so),
        generate_tent(seed=2500 + so),
        generate_market_stall(seed=2800 + so),
    ]
