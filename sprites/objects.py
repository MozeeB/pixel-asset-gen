"""
Natural object animations: rock, sky, leaf, tree, water, grass.
Procedurally generated sprite sheets using sine waves, noise, and physics.
"""

import math
from engine.drawing import new_sprite, put_pixel, draw_outline, draw_outline_thick, draw_circle, draw_line
from engine.palette import OBJECTS
from engine.noise import noise_map, fractal_noise
from engine.sprite import SpriteSheet


# ============================================================
# ROCK ANIMATIONS
# ============================================================

def _draw_rock(img, ox: int, oy: int, seed: int = 42):
    """Draw a 10x8 rock shape with noise texture at offset (ox, oy)."""
    ob = OBJECTS
    nmap = noise_map(16, 16, seed=seed, octaves=2, base_scale=0.3)

    # Rock silhouette: rough oval
    rock_rows = [
        (4, 9),   # y=0: cols 4-9
        (3, 10),  # y=1
        (2, 11),  # y=2
        (2, 12),  # y=3
        (2, 12),  # y=4
        (3, 11),  # y=5
        (3, 11),  # y=6
        (4, 10),  # y=7
    ]
    for ry, (x_start, x_end) in enumerate(rock_rows):
        for rx in range(x_start, x_end):
            v = nmap[ry + oy][rx] if (ry + oy) < 16 and rx < 16 else 0.5
            if v < 0.35:
                color = ob.shadow("rock_gray")
            elif v < 0.65:
                color = ob.base("rock_gray")
            else:
                color = ob.highlight("rock_gray")
            put_pixel(img, rx + ox, ry + oy, color)

    # Moss patches
    moss_nmap = noise_map(16, 16, seed=seed + 100, octaves=1, base_scale=0.5)
    for ry, (x_start, x_end) in enumerate(rock_rows):
        for rx in range(x_start, x_end):
            if moss_nmap[ry + oy][rx] if (ry + oy) < 16 and rx < 16 else 0 > 0.75:
                if ry < 3:
                    put_pixel(img, rx + ox, ry + oy, ob.base("rock_moss"))


def generate_rock_idle(seed: int = 500) -> SpriteSheet:
    """Rock with subtle idle wobble animation."""
    frames = []
    for f in range(8):
        img = new_sprite()
        # Subtle vertical wobble: 0 or 1 pixel shift
        y_off = round(math.sin(f * math.pi / 4) * 0.6)
        _draw_rock(img, 0, 4 + y_off, seed=seed)
        draw_outline_thick(img)
        frames.append(img)
    return SpriteSheet("rock_idle", frames, frame_duration_ms=200, loop=True)


def generate_rock_crumble(seed: int = 510) -> SpriteSheet:
    """Rock crumbling into fragments."""
    ob = OBJECTS
    frames = []

    # Fragment definitions: (start_x, start_y, width, height)
    fragments = [
        (5, 5, 3, 3),
        (9, 4, 3, 4),
        (4, 8, 4, 3),
        (9, 8, 3, 3),
        (7, 6, 2, 2),
    ]
    # Velocity for each fragment: (vx, vy)
    velocities = [
        (-1.5, -2.0),
        (1.5, -1.8),
        (-1.0, 0.5),
        (1.2, 0.3),
        (0.0, -2.5),
    ]

    for f in range(6):
        img = new_sprite()
        if f == 0:
            # Full rock
            _draw_rock(img, 0, 4, seed=seed)
            draw_outline_thick(img)
        else:
            # Fragments fly outward with gravity
            t = f * 0.4
            gravity = 3.0
            alpha = max(0, 255 - f * 40)
            for (fx, fy, fw, fh), (vx, vy) in zip(fragments, velocities):
                # Parabolic trajectory
                dx = int(vx * t)
                dy = int(vy * t + 0.5 * gravity * t * t)
                nmap = noise_map(16, 16, seed=seed + fx, octaves=1, base_scale=0.4)
                for py in range(fh):
                    for px in range(fw):
                        nx = fx + px + dx
                        ny = fy + py + dy
                        if 0 <= nx < 16 and 0 <= ny < 16:
                            v = nmap[py][px] if py < 16 and px < 16 else 0.5
                            base = ob.base("rock_gray") if v > 0.4 else ob.shadow("rock_gray")
                            color = base + (alpha,)
                            put_pixel(img, nx, ny, color)
        frames.append(img)

    return SpriteSheet("rock_crumble", frames, frame_duration_ms=100, loop=False,
                       frame_durations_ms=[100, 80, 80, 100, 120, 150])


# ============================================================
# SKY ANIMATIONS
# ============================================================

def _draw_cloud(img, cx: int, cy: int, width: int, height: int, seed: int):
    """Draw a fluffy cloud shape."""
    ob = OBJECTS
    nmap = noise_map(16, 16, seed=seed, octaves=2, base_scale=0.4)
    half_w = width // 2
    half_h = height // 2

    for dy in range(-half_h, half_h + 1):
        for dx in range(-half_w, half_w + 1):
            # Elliptical boundary with noise variation
            dist = (dx / (half_w + 0.1)) ** 2 + (dy / (half_h + 0.1)) ** 2
            noise_val = nmap[(cy + dy) % 16][(cx + dx) % 16]
            threshold = 0.8 + noise_val * 0.3
            if dist < threshold:
                px, py = cx + dx, cy + dy
                if 0 <= px < 32 and 0 <= py < 16:
                    if dist < 0.3:
                        color = ob.highlight("cloud")
                    elif dist < 0.6:
                        color = ob.base("cloud")
                    else:
                        color = ob.shadow("cloud")
                    put_pixel(img, px, py, color)


def generate_sky_clouds(seed: int = 600) -> SpriteSheet:
    """Scrolling clouds on a sky background (32x16 wide tile)."""
    ob = OBJECTS
    frames = []
    cloud_positions = [(8, 4, 7, 3), (22, 8, 6, 2), (15, 12, 5, 2)]

    for f in range(8):
        img = new_sprite(32, 16)
        # Sky gradient background
        for y in range(16):
            t = y / 15.0
            r = int(ob.highlight("sky_day")[0] * (1 - t) + ob.base("sky_day")[0] * t)
            g = int(ob.highlight("sky_day")[1] * (1 - t) + ob.base("sky_day")[1] * t)
            b = int(ob.highlight("sky_day")[2] * (1 - t) + ob.base("sky_day")[2] * t)
            for x in range(32):
                put_pixel(img, x, y, (r, g, b))

        # Draw clouds with horizontal scroll (4px per frame, wrapping)
        scroll = f * 4
        for cx, cy, cw, ch in cloud_positions:
            wrapped_cx = (cx + scroll) % 32
            _draw_cloud(img, wrapped_cx, cy, cw, ch, seed=seed + cx)

        frames.append(img)
    return SpriteSheet("sky_clouds", frames, frame_duration_ms=200, loop=True)


def generate_sky_cycle(seed: int = 620) -> SpriteSheet:
    """Day/night cycle with gradient sky and stars."""
    ob = OBJECTS
    frames = []

    # 8 phases: dawn, morning, noon, afternoon, dusk, twilight, night, pre-dawn
    sky_colors = [
        ((255, 180, 130), (200, 140, 160)),   # dawn
        ((170, 210, 255), (135, 190, 250)),    # morning
        ((135, 200, 255), (100, 170, 240)),    # noon
        ((150, 200, 240), (120, 170, 220)),    # afternoon
        ((255, 140, 80), (180, 80, 120)),      # dusk
        ((80, 60, 120), (40, 30, 80)),         # twilight
        ((20, 20, 55), (10, 10, 35)),          # night
        ((60, 50, 100), (100, 80, 130)),       # pre-dawn
    ]

    # Star positions (only visible at night/twilight)
    star_positions = [(3, 2), (7, 5), (12, 1), (14, 6), (10, 3),
                      (1, 8), (5, 10), (13, 9), (8, 12), (15, 4)]

    for f, (top_color, bot_color) in enumerate(sky_colors):
        img = new_sprite()
        # Gradient fill
        for y in range(16):
            t = y / 15.0
            r = int(top_color[0] * (1 - t) + bot_color[0] * t)
            g = int(top_color[1] * (1 - t) + bot_color[1] * t)
            b = int(top_color[2] * (1 - t) + bot_color[2] * t)
            for x in range(16):
                put_pixel(img, x, y, (r, g, b))

        # Stars on dark frames (twilight=5, night=6, pre-dawn=7)
        if f >= 5:
            brightness = 255 if f == 6 else 180
            star_color = (brightness, brightness, min(255, brightness + 30))
            visible_count = 10 if f == 6 else (7 if f == 5 else 5)
            for sx, sy in star_positions[:visible_count]:
                put_pixel(img, sx, sy, star_color)

        # Sun/moon indicator
        if f <= 4:
            # Sun position arcs across sky
            sun_x = 3 + f * 2
            sun_y = 3 if f == 2 else (4 if f in (1, 3) else 5)
            sun_color = (255, 240, 100) if f < 4 else (255, 180, 80)
            put_pixel(img, sun_x, sun_y, sun_color)
            put_pixel(img, sun_x + 1, sun_y, sun_color)
            put_pixel(img, sun_x, sun_y + 1, sun_color)
            put_pixel(img, sun_x + 1, sun_y + 1, sun_color)
        elif f >= 6:
            # Moon
            moon_color = (220, 220, 240)
            put_pixel(img, 11, 3, moon_color)
            put_pixel(img, 12, 3, moon_color)
            put_pixel(img, 12, 4, moon_color)

        frames.append(img)
    return SpriteSheet("sky_cycle", frames, frame_duration_ms=300, loop=True)


# ============================================================
# LEAF ANIMATIONS
# ============================================================

def _generate_leaf_fall(name: str, color_key: str, seed: int = 700) -> SpriteSheet:
    """Falling leaf with gravity and lateral sway."""
    ob = OBJECTS
    frames = []

    for f in range(8):
        img = new_sprite()
        # Leaf position: gravity pulls down, sine sway laterally
        cx = 8 + round(math.sin(f * math.pi / 3 + seed * 0.1) * 2)
        cy = 2 + f * 1.7  # gravity: ~1.7px per frame

        if cy > 14:
            cy = 14  # ground

        cy = int(cy)

        # Leaf shape rotates slightly per frame (3x2 leaf)
        angle_step = f % 4
        leaf_pixels = [
            # angle 0: horizontal leaf
            [(0, 0), (1, 0), (2, 0), (1, 1)],
            # angle 1: tilted
            [(0, 0), (1, 0), (2, 1), (1, 1)],
            # angle 2: vertical-ish
            [(1, 0), (0, 1), (1, 1), (1, 2)],
            # angle 3: tilted other way
            [(0, 1), (1, 0), (2, 0), (1, 1)],
        ]

        base = ob.base(color_key)
        highlight = ob.highlight(color_key)
        for i, (dx, dy) in enumerate(leaf_pixels[angle_step]):
            color = highlight if i == 0 else base
            put_pixel(img, cx + dx, cy + dy, color)

        # Stem pixel
        put_pixel(img, cx + 1, cy + (2 if angle_step == 2 else 1), ob.shadow(color_key))

        frames.append(img)

    return SpriteSheet(name, frames, frame_duration_ms=120, loop=False)


def generate_leaf_fall(seed: int = 700) -> SpriteSheet:
    return _generate_leaf_fall("leaf_fall_green", "leaf_green", seed)


def generate_leaf_fall_autumn(seed: int = 710) -> SpriteSheet:
    return _generate_leaf_fall("leaf_fall_autumn", "leaf_autumn", seed)


def generate_leaf_fall_red(seed: int = 720) -> SpriteSheet:
    return _generate_leaf_fall("leaf_fall_red", "leaf_red", seed)


def generate_leaf_swirl(seed: int = 730) -> SpriteSheet:
    """Multiple leaves swirling in circular/figure-8 paths."""
    ob = OBJECTS
    frames = []

    # 3 leaves with different phases and colors
    leaves = [
        {"color": "leaf_green", "phase": 0.0, "radius": 4, "center": (7, 7)},
        {"color": "leaf_autumn", "phase": 2.1, "radius": 3, "center": (8, 8)},
        {"color": "leaf_red", "phase": 4.2, "radius": 5, "center": (8, 7)},
    ]

    for f in range(8):
        img = new_sprite()
        t = f * math.pi / 4  # angle step

        for leaf in leaves:
            angle = t + leaf["phase"]
            r = leaf["radius"]
            cx = leaf["center"][0] + round(math.cos(angle) * r)
            cy = leaf["center"][1] + round(math.sin(angle) * r * 0.6)  # squished vertical

            # Small 2x2 leaf
            base = ob.base(leaf["color"])
            highlight = ob.highlight(leaf["color"])
            if 0 <= cx < 15 and 0 <= cy < 15:
                put_pixel(img, cx, cy, highlight)
                put_pixel(img, cx + 1, cy, base)
                put_pixel(img, cx, cy + 1, base)
                put_pixel(img, cx + 1, cy + 1, ob.shadow(leaf["color"]))

        frames.append(img)
    return SpriteSheet("leaf_swirl", frames, frame_duration_ms=100, loop=True)


# ============================================================
# TREE ANIMATION
# ============================================================

def generate_tree_sway(seed: int = 800) -> SpriteSheet:
    """Tree with wind-swaying canopy, anchored trunk."""
    ob = OBJECTS
    frames = []
    nmap = noise_map(16, 16, seed=seed, octaves=2, base_scale=0.3)

    for f in range(8):
        img = new_sprite()
        # Wind offset for canopy (increases with height)
        wind = round(math.sin(f * math.pi / 4) * 1.5)

        # Trunk: 2px wide, from y=8 to y=15 (anchored at bottom)
        for y in range(8, 16):
            trunk_x = 7
            put_pixel(img, trunk_x, y, ob.base("trunk"))
            put_pixel(img, trunk_x + 1, y, ob.shadow("trunk"))
            # Bark detail
            if y % 3 == 0:
                put_pixel(img, trunk_x, y, ob.shadow("bark"))

        # Roots at bottom
        put_pixel(img, 6, 15, ob.shadow("trunk"))
        put_pixel(img, 9, 15, ob.shadow("trunk"))

        # Canopy: roughly circular, shifted by wind
        canopy_cx = 8 + wind
        canopy_cy = 5
        canopy_r = 5

        for dy in range(-canopy_r, canopy_r + 1):
            for dx in range(-canopy_r, canopy_r + 1):
                dist_sq = dx * dx + dy * dy
                if dist_sq <= canopy_r * canopy_r:
                    px = canopy_cx + dx
                    py = canopy_cy + dy
                    if 0 <= px < 16 and 0 <= py < 16:
                        noise_v = nmap[py % 16][px % 16]
                        dist = math.sqrt(dist_sq) / canopy_r
                        if dist < 0.4 and noise_v > 0.4:
                            color = ob.highlight("canopy_light")
                        elif dist < 0.7:
                            color = ob.base("canopy")
                        else:
                            color = ob.shadow("canopy")
                        # Add noise variation
                        if noise_v > 0.8:
                            color = ob.highlight("canopy_light")
                        elif noise_v < 0.2:
                            color = ob.shadow("canopy")
                        put_pixel(img, px, py, color)

        draw_outline_thick(img)
        frames.append(img)
    return SpriteSheet("tree_sway", frames, frame_duration_ms=150, loop=True)


# ============================================================
# WATER ANIMATIONS
# ============================================================

def generate_water_waves(seed: int = 900) -> SpriteSheet:
    """Animated water tile with sine wave surface."""
    ob = OBJECTS
    frames = []

    for f in range(8):
        img = new_sprite()
        phase = f * math.pi / 4

        for x in range(16):
            # Wave surface height
            wave_y = 3 + round(math.sin(x * 0.8 + phase) * 1.5)

            for y in range(16):
                if y < wave_y:
                    continue  # above water

                depth = y - wave_y
                if depth == 0:
                    # Foam/surface
                    color = ob.highlight("water_foam")
                elif depth == 1:
                    color = ob.base("water_foam")
                elif depth < 5:
                    # Mid water with subtle variation
                    noise_v = fractal_noise(x, y + f * 0.5, seed, 2, 0.5, 0.3)
                    if noise_v > 0.3:
                        color = ob.highlight("water_mid")
                    else:
                        color = ob.base("water_mid")
                else:
                    # Deep water
                    noise_v = fractal_noise(x, y, seed + 50, 1, 0.5, 0.2)
                    if noise_v > 0.5:
                        color = ob.base("water_deep")
                    else:
                        color = ob.shadow("water_deep")

                put_pixel(img, x, y, color)

        frames.append(img)
    return SpriteSheet("water_waves", frames, frame_duration_ms=120, loop=True)


def generate_water_ripple(seed: int = 920) -> SpriteSheet:
    """Expanding ripple circles from center."""
    ob = OBJECTS
    frames = []
    cx, cy = 7, 7

    for f in range(6):
        img = new_sprite()

        # Background water
        for y in range(16):
            for x in range(16):
                noise_v = fractal_noise(x, y, seed, 2, 0.5, 0.3)
                if noise_v > 0.3:
                    color = ob.base("water_mid")
                else:
                    color = ob.shadow("water_mid")
                put_pixel(img, x, y, color)

        # Ripple rings
        radius = (f + 1) * 2
        alpha_factor = max(0, 255 - f * 35)

        for ring in range(max(0, f - 1), f + 1):
            r = (ring + 1) * 2
            brightness = alpha_factor if ring == f else alpha_factor // 2
            if brightness <= 0:
                continue
            ring_color = (
                min(255, ob.highlight("water_foam")[0]),
                min(255, ob.highlight("water_foam")[1]),
                min(255, ob.highlight("water_foam")[2]),
                brightness,
            )
            # Draw ring using circle approximation
            for angle_step in range(64):
                a = angle_step * math.pi * 2 / 64
                px = cx + round(math.cos(a) * r)
                py = cy + round(math.sin(a) * r)
                if 0 <= px < 16 and 0 <= py < 16:
                    put_pixel(img, px, py, ring_color)

        frames.append(img)

    return SpriteSheet("water_ripple", frames, frame_duration_ms=100, loop=False,
                       frame_durations_ms=[80, 100, 100, 120, 120, 150])


# ============================================================
# GRASS ANIMATION
# ============================================================

def generate_grass_sway(seed: int = 1000) -> SpriteSheet:
    """Grass blades swaying in wind, anchored at base."""
    ob = OBJECTS
    frames = []

    # Define grass blades: (base_x, height, phase_offset)
    blades = [
        (2, 7, 0.0),
        (5, 9, 0.8),
        (8, 8, 1.6),
        (11, 10, 2.4),
        (14, 7, 3.2),
    ]

    for f in range(8):
        img = new_sprite()
        t = f * math.pi / 4

        # Ground base
        for x in range(16):
            put_pixel(img, x, 15, ob.shadow("grass_dark"))
            put_pixel(img, x, 14, ob.base("grass_dark"))

        for base_x, height, phase in blades:
            for h in range(height):
                # Sway increases with height (anchored at base)
                sway_amount = (h / height) ** 2  # quadratic increase
                sway = round(math.sin(t + phase) * sway_amount * 2.5)

                px = base_x + sway
                py = 14 - h  # grow upward from ground

                if 0 <= px < 16 and 0 <= py < 16:
                    # Color: dark at base, bright at tip
                    h_ratio = h / height
                    if h_ratio > 0.8:
                        color = ob.highlight("grass_tip")
                    elif h_ratio > 0.4:
                        color = ob.base("grass_green")
                    else:
                        color = ob.shadow("grass_dark")
                    put_pixel(img, px, py, color)

                    # Second pixel width for thicker blades at base
                    if h_ratio < 0.6 and 0 <= px + 1 < 16:
                        put_pixel(img, px + 1, py, ob.base("grass_green") if h_ratio > 0.3 else ob.shadow("grass_dark"))

        frames.append(img)
    return SpriteSheet("grass_sway", frames, frame_duration_ms=120, loop=True)


# ============================================================
# GENERATE ALL
# ============================================================

def generate_all() -> list[SpriteSheet]:
    """Generate all natural object animations."""
    return [
        generate_rock_idle(),
        generate_rock_crumble(),
        generate_sky_clouds(),
        generate_sky_cycle(),
        generate_leaf_fall(),
        generate_leaf_fall_autumn(),
        generate_leaf_fall_red(),
        generate_leaf_swirl(),
        generate_tree_sway(),
        generate_water_waves(),
        generate_water_ripple(),
        generate_grass_sway(),
    ]
