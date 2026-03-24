"""
Visual effects: explosion, magic sparkle, smoke puff, fire,
and advanced effects: dash afterimage, hit sparks, dust puff,
slash arc, heal aura, charge up, shockwave, portal, level up,
screen flash.
"""

import math
from engine.drawing import new_sprite, put_pixel, draw_outline, draw_circle, draw_line
from engine.palette import EFFECTS
from engine.sprite import SpriteSheet


def generate_explosion() -> SpriteSheet:
    ef = EFFECTS
    frames = []
    for f in range(8):
        img = new_sprite()
        # Radius grows then shrinks
        if f < 5:
            radius = f + 1
        else:
            radius = 8 - f

        cx, cy = 7, 7
        colors = [ef.highlight("fire_hot"), ef.base("fire_mid"),
                  ef.base("fire_cool"), ef.base("smoke")]

        for dx in range(-radius - 1, radius + 2):
            for dy in range(-radius - 1, radius + 2):
                dist = abs(dx) + abs(dy)
                if dist <= radius:
                    ci = min(dist * len(colors) // (radius + 1), len(colors) - 1)
                    if f >= 5:
                        ci = min(ci + 1, len(colors) - 1)
                    put_pixel(img, cx + dx, cy + dy, colors[ci])

        # Sparks
        if f < 5:
            spark = ef.highlight("spark")
            for sx, sy in [(-radius, -1), (radius, 1), (0, -radius), (1, radius)]:
                put_pixel(img, cx + sx, cy + sy, spark)
                put_pixel(img, cx + sx + 1, cy + sy, ef.base("fire_hot"))

        frames.append(img)
    return SpriteSheet("explosion", frames, frame_duration_ms=60, loop=False)


def generate_magic_sparkle() -> SpriteSheet:
    ef = EFFECTS
    frames = []
    for f in range(8):
        img = new_sprite()
        cx, cy = 7, 7
        size = 2 + (f % 3)

        # Cross pattern
        for i in range(-size, size + 1):
            intensity = 1.0 - abs(i) / (size + 1)
            if intensity > 0.5:
                put_pixel(img, cx + i, cy, ef.highlight("magic_blue"))
                put_pixel(img, cx, cy + i, ef.highlight("magic_blue"))
            else:
                put_pixel(img, cx + i, cy, ef.base("magic_blue"))
                put_pixel(img, cx, cy + i, ef.base("magic_blue"))

        # X pattern
        for i in range(-size + 1, size):
            put_pixel(img, cx + i, cy + i, ef.base("magic_purple"))
            put_pixel(img, cx + i, cy - i, ef.base("magic_purple"))

        # Center glow
        put_pixel(img, cx, cy, ef.highlight("spark"))
        put_pixel(img, cx - 1, cy, ef.highlight("magic_blue"))
        put_pixel(img, cx + 1, cy, ef.highlight("magic_blue"))

        # Rotating outer sparkles
        angle_idx = f % 4
        offsets = [
            (-size - 1, 0), (size + 1, 0),
            (0, -size - 1), (0, size + 1),
        ]
        for j, (ox, oy) in enumerate(offsets):
            if (j + angle_idx) % 2 == 0:
                put_pixel(img, cx + ox, cy + oy, ef.highlight("spark"))

        frames.append(img)
    return SpriteSheet("magic_sparkle", frames, frame_duration_ms=80)


def generate_smoke_puff() -> SpriteSheet:
    ef = EFFECTS
    frames = []
    for f in range(8):
        img = new_sprite()
        radius = min(f + 2, 6)
        cx, cy = 7, 9 - f  # rises upward
        alpha = max(220 - f * 30, 30)

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                dist = abs(dx) + abs(dy)
                if dist <= radius:
                    # Fade from center
                    fade = max(alpha - dist * 20, 20)
                    c = ef.base("smoke") if (dx + dy) % 2 == 0 else ef.highlight("smoke")
                    put_pixel(img, cx + dx, cy + dy, (*c, fade))

        frames.append(img)
    return SpriteSheet("smoke_puff", frames, frame_duration_ms=100, loop=False)


def generate_fire() -> SpriteSheet:
    """Flickering fire effect."""
    ef = EFFECTS
    frames = []
    for f in range(8):
        img = new_sprite()
        cx = 7

        # Base (wide, hot)
        for x in range(cx - 3, cx + 4):
            for y in range(11, 14):
                put_pixel(img, x, y, ef.base("fire_cool"))

        # Middle (medium)
        for x in range(cx - 2, cx + 3):
            for y in range(8, 12):
                c = ef.base("fire_mid") if (x + y + f) % 2 == 0 else ef.highlight("fire_hot")
                put_pixel(img, x, y, c)

        # Top (narrow, brightest)
        top_h = 3 + (f % 2)
        for y in range(8 - top_h, 8):
            w = max(1, (8 - y) // 2)
            for x in range(cx - w, cx + w + 1):
                put_pixel(img, x, y, ef.highlight("fire_hot"))

        # Sparks
        spark_y = 8 - top_h - 1
        if f % 3 == 0:
            put_pixel(img, cx - 1, spark_y, ef.highlight("spark"))
        if f % 3 == 1:
            put_pixel(img, cx + 1, spark_y, ef.highlight("spark"))

        frames.append(img)
    return SpriteSheet("fire", frames, frame_duration_ms=100)


# ============================================================
# ADVANCED EFFECTS
# ============================================================


def generate_dash_afterimage() -> SpriteSheet:
    """Dash afterimage / ghost trail — 6 frames fading out with motion blur."""
    ef = EFFECTS
    frames = []
    for f in range(6):
        img = new_sprite()
        cx, cy = 7, 7
        alpha = max(200 - f * 40, 20)
        # Silhouette shrinks and fades as it trails behind
        body_h = max(8 - f, 3)
        body_w = max(5 - f // 2, 2)
        # Head
        head_r = max(3 - f // 2, 1)
        head_y = cy - body_h // 2
        for dx in range(-head_r, head_r + 1):
            for dy in range(-head_r, head_r + 1):
                if abs(dx) + abs(dy) <= head_r:
                    c = ef.highlight("ghost_cyan") if f < 2 else ef.base("ghost_blue")
                    put_pixel(img, cx + dx + f, head_y + dy, (*c, alpha))
        # Body
        for dy in range(0, body_h):
            for dx in range(-body_w // 2, body_w // 2 + 1):
                c = ef.base("ghost_blue") if dy < body_h // 2 else ef.shadow("ghost_blue")
                put_pixel(img, cx + dx + f, cy - body_h // 4 + dy, (*c, alpha))
        # Motion streak lines
        streak_alpha = max(alpha - 60, 10)
        for sy in range(cy - 2, cy + 3):
            for sx in range(0, max(3 - f, 0)):
                put_pixel(img, sx, sy, (*ef.highlight("ghost_cyan"), streak_alpha))
        frames.append(img)
    return SpriteSheet("dash_afterimage", frames, frame_duration_ms=50, loop=False)


def generate_hit_sparks() -> SpriteSheet:
    """Impact sparks radiating outward — 6 frames."""
    ef = EFFECTS
    frames = []
    for f in range(6):
        img = new_sprite()
        cx, cy = 7, 7
        num_sparks = 8
        spark_dist = f * 2 + 1
        alpha = max(255 - f * 45, 30)

        # Central flash on first 2 frames
        if f < 2:
            flash_r = 3 - f
            for dx in range(-flash_r, flash_r + 1):
                for dy in range(-flash_r, flash_r + 1):
                    if abs(dx) + abs(dy) <= flash_r:
                        put_pixel(img, cx + dx, cy + dy,
                                  (*ef.highlight("flash_white"), 255))

        # Radiating sparks
        for i in range(num_sparks):
            angle = (i / num_sparks) * 2 * math.pi
            sx = cx + int(math.cos(angle) * spark_dist)
            sy = cy + int(math.sin(angle) * spark_dist)
            c = ef.highlight("hit_yellow") if i % 2 == 0 else ef.base("hit_orange")
            put_pixel(img, sx, sy, (*c, alpha))
            # Trail pixel behind spark
            if f > 0:
                tx = cx + int(math.cos(angle) * (spark_dist - 1))
                ty = cy + int(math.sin(angle) * (spark_dist - 1))
                put_pixel(img, tx, ty, (*ef.base("hit_orange"), alpha // 2))

        frames.append(img)
    return SpriteSheet("hit_sparks", frames, frame_duration_ms=40, loop=False)


def generate_dust_puff_landing() -> SpriteSheet:
    """Ground dust puff for landing/running — 6 frames, spreads laterally."""
    ef = EFFECTS
    frames = []
    for f in range(6):
        img = new_sprite()
        cx, cy = 7, 12  # Near ground level
        spread = f * 2 + 2
        height = max(3 - f // 2, 1)
        alpha = max(180 - f * 35, 20)

        # Dust cloud expands horizontally, shrinks vertically
        for dx in range(-spread, spread + 1):
            for dy in range(-height, 1):
                dist = abs(dx) + abs(dy)
                if dist <= spread:
                    fade = max(alpha - dist * 10, 10)
                    c = ef.base("dust_tan") if (dx + dy + f) % 2 == 0 else ef.highlight("dust_light")
                    put_pixel(img, cx + dx, cy + dy, (*c, fade))

        # Individual dust particles floating up
        if f > 1:
            for px_off in [-spread + 1, 0, spread - 1]:
                py_off = -(f - 1) * 2
                put_pixel(img, cx + px_off, cy + py_off,
                          (*ef.highlight("dust_light"), alpha // 2))

        frames.append(img)
    return SpriteSheet("dust_puff_landing", frames, frame_duration_ms=60, loop=False)


def generate_slash_arc() -> SpriteSheet:
    """Sword slash arc VFX — 5 frames, sweeping crescent."""
    ef = EFFECTS
    frames = []
    for f in range(5):
        img = new_sprite()
        cx, cy = 7, 7
        # Arc sweeps from top-right to bottom-left
        start_angle = -0.3 + f * 0.5
        arc_length = 1.2 + f * 0.3
        radius = 5 + f
        alpha = max(255 - f * 50, 40)

        # Draw arc
        steps = 20
        for s in range(steps):
            t = s / steps
            angle = start_angle + t * arc_length
            ax = cx + int(math.cos(angle) * radius)
            ay = cy + int(math.sin(angle) * radius)
            # Main arc pixel
            c = ef.highlight("slash_white") if t > 0.3 and t < 0.7 else ef.base("slash_light")
            put_pixel(img, ax, ay, (*c, alpha))
            # Inner edge (thicken the arc)
            ix = cx + int(math.cos(angle) * (radius - 1))
            iy = cy + int(math.sin(angle) * (radius - 1))
            put_pixel(img, ix, iy, (*ef.base("slash_light"), alpha // 2))

        # Leading edge sparkle
        tip_angle = start_angle + arc_length
        tx = cx + int(math.cos(tip_angle) * radius)
        ty = cy + int(math.sin(tip_angle) * radius)
        if f < 4:
            put_pixel(img, tx, ty, (*ef.highlight("spark"), 255))
            put_pixel(img, tx + 1, ty, (*ef.highlight("spark"), 180))

        frames.append(img)
    return SpriteSheet("slash_arc", frames, frame_duration_ms=35, loop=False)


def generate_heal_aura() -> SpriteSheet:
    """Healing aura ring rising upward — 8 frames, looping."""
    ef = EFFECTS
    frames = []
    for f in range(8):
        img = new_sprite()
        cx, cy = 7, 7

        # Pulsing ring
        ring_r = 4 + (f % 3)
        for angle_step in range(24):
            angle = (angle_step / 24) * 2 * math.pi
            rx = cx + int(math.cos(angle) * ring_r)
            ry = cy + int(math.sin(angle) * ring_r)
            # Alternate colors around ring
            c = ef.highlight("heal_light") if angle_step % 3 == 0 else ef.base("heal_green")
            alpha = 200 + int(30 * math.sin(f * 0.8 + angle_step))
            alpha = max(min(alpha, 255), 100)
            put_pixel(img, rx, ry, (*c, alpha))

        # Rising sparkle particles (+ shaped)
        for p in range(3):
            py = cy + 5 - ((f + p * 3) % 8)
            px = cx + [-3, 0, 3][p]
            if 0 <= py < 16:
                put_pixel(img, px, py, (*ef.highlight("heal_light"), 200))
                put_pixel(img, px, py - 1, (*ef.highlight("spark"), 150))

        # Center glow
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if abs(dx) + abs(dy) <= 1:
                    glow_alpha = 120 + int(60 * math.sin(f * 0.5))
                    put_pixel(img, cx + dx, cy + dy,
                              (*ef.highlight("heal_light"), glow_alpha))

        frames.append(img)
    return SpriteSheet("heal_aura", frames, frame_duration_ms=100)


def generate_charge_up() -> SpriteSheet:
    """Power charge-up — 8 frames, particles converge to center then burst."""
    ef = EFFECTS
    frames = []
    for f in range(8):
        img = new_sprite()
        cx, cy = 7, 7

        if f < 6:
            # Converging phase: particles move inward
            num_particles = 8
            max_dist = 7 - f
            for i in range(num_particles):
                angle = (i / num_particles) * 2 * math.pi + f * 0.3
                dist = max_dist
                px = cx + int(math.cos(angle) * dist)
                py = cy + int(math.sin(angle) * dist)
                alpha = 150 + f * 15
                c = ef.highlight("charge_yellow") if i % 2 == 0 else ef.base("charge_orange")
                put_pixel(img, px, py, (*c, min(alpha, 255)))
                # Trail
                if dist > 1:
                    tx = cx + int(math.cos(angle) * (dist + 1))
                    ty = cy + int(math.sin(angle) * (dist + 1))
                    put_pixel(img, tx, ty, (*ef.base("charge_orange"), alpha // 3))

            # Growing center glow
            glow_r = f // 2
            for dx in range(-glow_r, glow_r + 1):
                for dy in range(-glow_r, glow_r + 1):
                    if abs(dx) + abs(dy) <= glow_r:
                        put_pixel(img, cx + dx, cy + dy,
                                  (*ef.highlight("charge_yellow"), 100 + f * 20))
        else:
            # Burst phase (frames 6-7)
            burst_r = (f - 5) * 4
            for i in range(12):
                angle = (i / 12) * 2 * math.pi
                bx = cx + int(math.cos(angle) * burst_r)
                by = cy + int(math.sin(angle) * burst_r)
                alpha = 255 if f == 6 else 120
                c = ef.highlight("spark") if i % 3 == 0 else ef.highlight("charge_yellow")
                put_pixel(img, bx, by, (*c, alpha))

            # Center flash
            if f == 6:
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if abs(dx) + abs(dy) <= 2:
                            put_pixel(img, cx + dx, cy + dy,
                                      (*ef.highlight("spark"), 255))

        frames.append(img)
    return SpriteSheet("charge_up", frames, frame_duration_ms=80, loop=False)


def generate_shockwave() -> SpriteSheet:
    """Ground slam shockwave — 6 frames, expanding ring."""
    ef = EFFECTS
    frames = []
    for f in range(6):
        img = new_sprite()
        cx, cy = 7, 9  # Slightly below center (ground-based)
        ring_r = f * 2 + 2
        alpha = max(255 - f * 45, 30)

        # Expanding ring (elliptical — wider than tall for ground perspective)
        steps = max(ring_r * 4, 12)
        for s in range(steps):
            angle = (s / steps) * 2 * math.pi
            rx = cx + int(math.cos(angle) * ring_r)
            ry = cy + int(math.sin(angle) * (ring_r * 0.5))  # Squashed vertically
            c = ef.highlight("shock_white") if s % 3 == 0 else ef.base("shock_cyan")
            put_pixel(img, rx, ry, (*c, alpha))

        # Inner distortion lines
        if f < 4:
            inner_r = max(ring_r - 2, 1)
            for s in range(0, steps, 3):
                angle = (s / steps) * 2 * math.pi
                ix = cx + int(math.cos(angle) * inner_r)
                iy = cy + int(math.sin(angle) * (inner_r * 0.5))
                put_pixel(img, ix, iy, (*ef.base("shock_cyan"), alpha // 2))

        # Ground debris at base
        if f < 3:
            for gx in range(-ring_r, ring_r + 1, 2):
                if abs(gx) <= ring_r and abs(gx) > ring_r - 3:
                    put_pixel(img, cx + gx, cy + 1, (*ef.base("dust_tan"), alpha))

        frames.append(img)
    return SpriteSheet("shockwave", frames, frame_duration_ms=50, loop=False)


def generate_portal() -> SpriteSheet:
    """Teleport portal swirl — 8 frames, rotating spiral."""
    ef = EFFECTS
    frames = []
    for f in range(8):
        img = new_sprite()
        cx, cy = 7, 7

        # Outer ring
        outer_r = 6
        steps = 24
        for s in range(steps):
            angle = (s / steps) * 2 * math.pi + f * 0.4
            px = cx + int(math.cos(angle) * outer_r)
            py = cy + int(math.sin(angle) * outer_r)
            c = ef.highlight("portal_pink") if s % 4 < 2 else ef.base("portal_purple")
            put_pixel(img, px, py, (*c, 220))

        # Spiral arms (2 arms, rotating)
        for arm in range(2):
            arm_offset = arm * math.pi
            for t in range(8):
                angle = arm_offset + f * 0.5 + t * 0.4
                dist = 1 + t * 0.7
                sx = cx + int(math.cos(angle) * dist)
                sy = cy + int(math.sin(angle) * dist)
                alpha = 255 - t * 25
                c = ef.highlight("portal_pink") if t < 4 else ef.base("portal_purple")
                put_pixel(img, sx, sy, (*c, max(alpha, 80)))

        # Center void (dark)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if abs(dx) + abs(dy) <= 1:
                    put_pixel(img, cx + dx, cy + dy, (20, 10, 40, 230))

        # Floating particles
        for p in range(4):
            pa = (p / 4) * 2 * math.pi + f * 0.7
            pr = 4 + int(2 * math.sin(f * 0.3 + p))
            ppx = cx + int(math.cos(pa) * pr)
            ppy = cy + int(math.sin(pa) * pr)
            put_pixel(img, ppx, ppy, (*ef.highlight("spark"), 180))

        frames.append(img)
    return SpriteSheet("portal", frames, frame_duration_ms=90)


def generate_level_up() -> SpriteSheet:
    """Level up celebration burst — 8 frames, rising sparkles + expanding ring."""
    ef = EFFECTS
    frames = []
    for f in range(8):
        img = new_sprite()
        cx, cy = 7, 7

        if f < 3:
            # Build-up: glowing center
            glow_r = f + 1
            for dx in range(-glow_r, glow_r + 1):
                for dy in range(-glow_r, glow_r + 1):
                    if abs(dx) + abs(dy) <= glow_r:
                        alpha = 150 + f * 30
                        put_pixel(img, cx + dx, cy + dy,
                                  (*ef.highlight("levelup_gold"), min(alpha, 255)))
        else:
            # Burst + rising sparkles
            burst_frame = f - 3
            ring_r = burst_frame * 2 + 3
            alpha = max(255 - burst_frame * 40, 40)

            # Expanding star burst
            for i in range(8):
                angle = (i / 8) * 2 * math.pi + burst_frame * 0.2
                for d in range(1, ring_r + 1):
                    bx = cx + int(math.cos(angle) * d)
                    by = cy + int(math.sin(angle) * d)
                    c = ef.highlight("levelup_gold") if d < ring_r // 2 else ef.base("levelup_gold")
                    pa = max(alpha - d * 15, 20)
                    put_pixel(img, bx, by, (*c, pa))

            # Rising sparkle particles
            for p in range(5):
                sp_x = cx + [-4, -2, 0, 2, 4][p]
                sp_y = cy - burst_frame * 2 - p
                if 0 <= sp_y < 16:
                    put_pixel(img, sp_x, sp_y, (*ef.highlight("levelup_white"), alpha))
                    if sp_y + 1 < 16:
                        put_pixel(img, sp_x, sp_y + 1, (*ef.highlight("spark"), alpha // 2))

        frames.append(img)
    return SpriteSheet("level_up", frames, frame_duration_ms=70, loop=False)


def generate_screen_flash() -> SpriteSheet:
    """Full-screen white flash overlay — 4 frames, flash then fade."""
    ef = EFFECTS
    frames = []
    alphas = [220, 160, 80, 30]
    for f in range(4):
        img = new_sprite()
        alpha = alphas[f]
        for x in range(16):
            for y in range(16):
                put_pixel(img, x, y, (*ef.highlight("flash_white"), alpha))
        frames.append(img)
    return SpriteSheet("screen_flash", frames, frame_duration_ms=40, loop=False)


def generate_shield_bash() -> SpriteSheet:
    """Shield bash impact — 6 frames, radial burst with shield outline."""
    ef = EFFECTS
    frames = []
    for f in range(6):
        img = new_sprite()
        cx, cy = 7, 7

        if f < 2:
            # Shield shape at center (impact moment)
            # Shield outline
            for dy in range(-3, 4):
                w = 3 - abs(dy) // 2
                for dx in range(-w, w + 1):
                    if abs(dx) == w or abs(dy) == 3:
                        put_pixel(img, cx + dx, cy + dy, ef.base("shield_gold"))
                    else:
                        alpha = 255 if f == 0 else 180
                        put_pixel(img, cx + dx, cy + dy,
                                  (*ef.highlight("shield_white"), alpha))

        # Radial impact lines
        num_lines = 6
        line_len = f * 2 + 1
        alpha = max(255 - f * 45, 30)
        for i in range(num_lines):
            angle = (i / num_lines) * 2 * math.pi + 0.3
            for d in range(2, min(line_len + 2, 8)):
                lx = cx + int(math.cos(angle) * d)
                ly = cy + int(math.sin(angle) * d)
                c = ef.highlight("shield_gold") if d < 4 else ef.base("shield_gold")
                put_pixel(img, lx, ly, (*c, alpha))

        # Spark tips
        if f < 4:
            for i in range(num_lines):
                angle = (i / num_lines) * 2 * math.pi + 0.3
                d = line_len + 2
                sx = cx + int(math.cos(angle) * d)
                sy = cy + int(math.sin(angle) * d)
                put_pixel(img, sx, sy, (*ef.highlight("spark"), alpha))

        frames.append(img)
    return SpriteSheet("shield_bash", frames, frame_duration_ms=45, loop=False)


def generate_combo_counter() -> list[SpriteSheet]:
    """Combo hit counter sprites 1-5 — single-frame each, styled numbers."""
    ef = EFFECTS
    results = []
    # Simple 3x5 pixel font for digits 1-5
    digit_maps = {
        1: [
            (1, 0), (0, 1), (1, 1), (1, 2), (1, 3), (1, 4),
            (0, 4), (1, 4), (2, 4),
        ],
        2: [
            (0, 0), (1, 0), (2, 0), (2, 1), (0, 2), (1, 2), (2, 2),
            (0, 3), (0, 4), (1, 4), (2, 4),
        ],
        3: [
            (0, 0), (1, 0), (2, 0), (2, 1), (0, 2), (1, 2), (2, 2),
            (2, 3), (0, 4), (1, 4), (2, 4),
        ],
        4: [
            (0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2),
            (2, 3), (2, 4),
        ],
        5: [
            (0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (1, 2), (2, 2),
            (2, 3), (0, 4), (1, 4), (2, 4),
        ],
    }
    for num in range(1, 6):
        img = new_sprite()
        ox, oy = 6, 5  # Center the 3x5 digit
        # Glow behind number
        for dx in range(-1, 5):
            for dy in range(-1, 7):
                put_pixel(img, ox + dx, oy + dy, (*ef.shadow("hit_orange"), 60))
        # Number pixels
        for px, py in digit_maps[num]:
            put_pixel(img, ox + px, oy + py, ef.highlight("hit_yellow"))
            # Outline
            for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = ox + px + ddx, oy + py + ddy
                if (px + ddx, py + ddy) not in digit_maps[num]:
                    put_pixel(img, nx, ny, ef.shadow("hit_orange"))
        results.append(SpriteSheet(f"combo_{num}", [img], frame_duration_ms=200, loop=False))
    return results


def generate_energy_orb() -> SpriteSheet:
    """Floating energy orb — 8 frames, pulsing glow with orbiting particles."""
    ef = EFFECTS
    frames = []
    for f in range(8):
        img = new_sprite()
        cx, cy = 7, 7

        # Core orb (pulsing size)
        core_r = 2 + int(math.sin(f * 0.8) * 0.8)
        for dx in range(-core_r, core_r + 1):
            for dy in range(-core_r, core_r + 1):
                dist = math.sqrt(dx * dx + dy * dy)
                if dist <= core_r:
                    alpha = int(255 - dist * 40)
                    c = ef.highlight("magic_blue") if dist < core_r * 0.5 else ef.base("magic_blue")
                    put_pixel(img, cx + dx, cy + dy, (*c, max(alpha, 100)))

        # Orbiting particles
        for p in range(3):
            pa = (p / 3) * 2 * math.pi + f * 0.5
            orbit_r = 4
            ox = cx + int(math.cos(pa) * orbit_r)
            oy = cy + int(math.sin(pa) * orbit_r)
            put_pixel(img, ox, oy, (*ef.highlight("spark"), 220))

        # Outer glow halo
        halo_r = 5
        for s in range(16):
            angle = (s / 16) * 2 * math.pi
            hx = cx + int(math.cos(angle) * halo_r)
            hy = cy + int(math.sin(angle) * halo_r)
            glow_alpha = 60 + int(40 * math.sin(f * 0.6 + s * 0.5))
            put_pixel(img, hx, hy, (*ef.base("magic_purple"), max(glow_alpha, 30)))

        frames.append(img)
    return SpriteSheet("energy_orb", frames, frame_duration_ms=100)


def generate_frost_burst() -> SpriteSheet:
    """Ice/frost burst effect — 6 frames, crystalline expansion."""
    ef = EFFECTS
    frames = []
    ice_core = (180, 220, 255)
    ice_edge = (100, 180, 240)
    ice_shard = (220, 240, 255)
    for f in range(6):
        img = new_sprite()
        cx, cy = 7, 7

        # Expanding ice crystal pattern (6-fold symmetry)
        for arm in range(6):
            angle = (arm / 6) * 2 * math.pi
            arm_len = f + 2
            for d in range(arm_len):
                ix = cx + int(math.cos(angle) * d)
                iy = cy + int(math.sin(angle) * d)
                alpha = max(255 - f * 30, 60)
                c = ice_core if d < arm_len // 2 else ice_edge
                put_pixel(img, ix, iy, (*c, alpha))

                # Branch crystals
                if d > 1 and d % 2 == 0:
                    branch_angle = angle + math.pi / 3
                    bx = ix + int(math.cos(branch_angle) * 1)
                    by = iy + int(math.sin(branch_angle) * 1)
                    put_pixel(img, bx, by, (*ice_shard, alpha // 2))
                    branch_angle2 = angle - math.pi / 3
                    bx2 = ix + int(math.cos(branch_angle2) * 1)
                    by2 = iy + int(math.sin(branch_angle2) * 1)
                    put_pixel(img, bx2, by2, (*ice_shard, alpha // 2))

        # Center flash
        if f < 2:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    put_pixel(img, cx + dx, cy + dy, (*ice_shard, 255))

        frames.append(img)
    return SpriteSheet("frost_burst", frames, frame_duration_ms=55, loop=False)


def generate_poison_cloud() -> SpriteSheet:
    """Poison cloud — 8 frames, billowing toxic gas."""
    ef = EFFECTS
    frames = []
    poison_dark = (60, 120, 30)
    poison_mid = (80, 180, 50)
    poison_light = (120, 220, 80)
    for f in range(8):
        img = new_sprite()
        cx, cy = 7, 8

        # Multiple overlapping circles that shift
        blobs = [
            (cx - 2 + (f % 3), cy - 1, 3),
            (cx + 1 - (f % 2), cy, 3),
            (cx + (f % 2), cy - 2, 2),
        ]
        for bx, by, br in blobs:
            for dx in range(-br, br + 1):
                for dy in range(-br, br + 1):
                    dist = abs(dx) + abs(dy)
                    if dist <= br:
                        alpha = max(160 - dist * 30 - f * 5, 30)
                        if dist == 0:
                            c = poison_light
                        elif dist < br:
                            c = poison_mid
                        else:
                            c = poison_dark
                        # Don't overwrite with lower alpha
                        existing = img.getpixel((bx + dx, by + dy)) if 0 <= bx + dx < 16 and 0 <= by + dy < 16 else (0, 0, 0, 0)
                        if existing[3] < alpha:
                            put_pixel(img, bx + dx, by + dy, (*c, alpha))

        # Bubbles rising
        for b in range(2):
            bubble_x = cx + [-2, 2][b] + (f % 2)
            bubble_y = cy - 3 - (f + b * 2) % 4
            if 0 <= bubble_y < 16:
                put_pixel(img, bubble_x, bubble_y, (*poison_light, 140))

        frames.append(img)
    return SpriteSheet("poison_cloud", frames, frame_duration_ms=110)


def generate_lightning_strike() -> SpriteSheet:
    """Lightning bolt strike — 6 frames, flash then jagged bolt."""
    ef = EFFECTS
    frames = []
    bolt_color = (200, 220, 255)
    glow_color = (150, 180, 255)
    flash_color = (240, 245, 255)
    for f in range(6):
        img = new_sprite()
        cx = 7

        if f == 0:
            # Full screen flash
            for x in range(16):
                for y in range(16):
                    put_pixel(img, x, y, (*flash_color, 180))
        elif f < 4:
            # Jagged bolt from top to bottom
            alpha = max(255 - (f - 1) * 60, 80)
            x = cx
            segments = [(x, 0)]
            for y in range(1, 15):
                # Zigzag
                if y % 3 == 0:
                    x += [-2, -1, 1, 2][(y + f) % 4]
                    x = max(2, min(13, x))
                segments.append((x, y))

            # Draw bolt
            for i in range(len(segments) - 1):
                x0, y0 = segments[i]
                x1, y1 = segments[i + 1]
                # Core
                put_pixel(img, x0, y0, (*bolt_color, alpha))
                # Glow around bolt
                for gx in [-1, 1]:
                    put_pixel(img, x0 + gx, y0, (*glow_color, alpha // 3))

            # Impact point glow at bottom
            impact_x = segments[-1][0]
            for dx in range(-2, 3):
                for dy in range(-1, 2):
                    dist = abs(dx) + abs(dy)
                    if dist <= 2:
                        put_pixel(img, impact_x + dx, 14 + dy,
                                  (*flash_color, max(alpha - dist * 40, 30)))
        else:
            # Afterglow
            alpha = 40 if f == 4 else 15
            for x in range(16):
                for y in range(16):
                    put_pixel(img, x, y, (*glow_color, alpha))

        frames.append(img)
    return SpriteSheet("lightning_strike", frames, frame_duration_ms=45, loop=False)


def generate_all() -> list:
    all_effects = [
        # Original effects
        generate_explosion(),
        generate_magic_sparkle(),
        generate_smoke_puff(),
        generate_fire(),
        # Advanced effects
        generate_dash_afterimage(),
        generate_hit_sparks(),
        generate_dust_puff_landing(),
        generate_slash_arc(),
        generate_heal_aura(),
        generate_charge_up(),
        generate_shockwave(),
        generate_portal(),
        generate_level_up(),
        generate_screen_flash(),
        generate_shield_bash(),
        generate_energy_orb(),
        generate_frost_burst(),
        generate_poison_cloud(),
        generate_lightning_strike(),
    ]
    # Add combo counter sprites (list of SpriteSheets)
    all_effects.extend(generate_combo_counter())
    return all_effects
