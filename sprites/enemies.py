"""
Enemy sprites with outlines, shading, and color variants.
Slime (3 colors), skeleton, bat, ghost, goblin.
Each enemy has idle, hit (2 frames), and death (4 frames) animations.
"""

from engine.drawing import (
    new_sprite, put_pixel, draw_outline, draw_outline_thick, apply_shading_auto,
    draw_circle, draw_ellipse_filled,
)
from engine.palette import ENEMIES, ShadedColor, recolor
from engine.sprite import SpriteSheet, StaticSprite


def _shade_and_outline(img, shade_map=None):
    if shade_map:
        img = apply_shading_auto(img, shade_map)
    return draw_outline_thick(img)


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


def _shrink_sprite(img, factor: float):
    """Shrink non-transparent pixels toward center for death dissolve."""
    result = new_sprite(img.width, img.height)
    w, h = img.size
    # Find center of mass
    cx_sum, cy_sum, count = 0, 0, 0
    for y in range(h):
        for x in range(w):
            if img.getpixel((x, y))[3] > 0:
                cx_sum += x
                cy_sum += y
                count += 1
    if count == 0:
        return result
    cx, cy = cx_sum / count, cy_sum / count
    for y in range(h):
        for x in range(w):
            px = img.getpixel((x, y))
            if px[3] > 0:
                nx = int(cx + (x - cx) * factor)
                ny = int(cy + (y - cy) * factor)
                if 0 <= nx < w and 0 <= ny < h:
                    alpha = int(px[3] * factor)
                    result.putpixel((nx, ny), (px[0], px[1], px[2], max(alpha, 30)))
    return result


# ============================================================
# SLIME (8-frame, 3 color variants)
# ============================================================

def _draw_slime_frame(f: int, base_color, eye_color, shaded: ShadedColor) -> "Image.Image":
    img = new_sprite()

    # Body shapes per frame: squish/stretch cycle
    if f in (0, 4, 7):
        # Normal
        top, bot, width = 7, 13, 4
    elif f in (1, 5):
        # Squished
        top, bot, width = 9, 13, 5
    elif f in (2, 6):
        # Stretching
        top, bot, width = 5, 13, 3
    else:
        # Tall
        top, bot, width = 6, 13, 3

    cx = 7
    for y in range(top, bot + 1):
        progress = (y - top) / max(bot - top, 1)
        w = int(width * (0.5 + progress * 0.5))
        for x in range(cx - w, cx + w + 1):
            put_pixel(img, x, y, base_color)

    # Eyes
    ey = top + 2
    put_pixel(img, 6, ey, eye_color)
    put_pixel(img, 9, ey, eye_color)
    # Highlight
    put_pixel(img, 6, ey - 1, shaded.highlight)

    shade_map = {base_color: shaded}
    return _shade_and_outline(img, shade_map)


def generate_slime(hue_shift: float = 0.0, name_suffix: str = "") -> SpriteSheet:
    base = ENEMIES.base("slime")
    eye = ENEMIES.base("eyes_yellow")
    shaded = ENEMIES.colors["slime"]

    if hue_shift != 0.0:
        base = recolor(base, hue_shift)
        shaded = ShadedColor(
            highlight=recolor(shaded.highlight, hue_shift),
            base=recolor(shaded.base, hue_shift),
            shadow=recolor(shaded.shadow, hue_shift),
        )

    frames = [_draw_slime_frame(f, base, eye, shaded) for f in range(8)]
    return SpriteSheet(f"slime{name_suffix}", frames, frame_duration_ms=120)


def generate_slime_hit(hue_shift: float = 0.0, name_suffix: str = "") -> SpriteSheet:
    base = ENEMIES.base("slime")
    eye = ENEMIES.base("eyes_yellow")
    shaded = ENEMIES.colors["slime"]
    if hue_shift != 0.0:
        base = recolor(base, hue_shift)
        shaded = ShadedColor(
            highlight=recolor(shaded.highlight, hue_shift),
            base=recolor(shaded.base, hue_shift),
            shadow=recolor(shaded.shadow, hue_shift),
        )
    # Frame 0: flash + squished
    f0 = _apply_flash(_draw_slime_frame(1, base, eye, shaded), 0.7)
    # Frame 1: recoil bounce
    f1 = _draw_slime_frame(3, base, eye, shaded)
    return SpriteSheet(f"slime{name_suffix}_hit", [f0, f1], frame_duration_ms=80, loop=False,
                       frame_durations_ms=[60, 100])


def generate_slime_death(hue_shift: float = 0.0, name_suffix: str = "") -> SpriteSheet:
    base = ENEMIES.base("slime")
    eye = ENEMIES.base("eyes_yellow")
    shaded = ENEMIES.colors["slime"]
    if hue_shift != 0.0:
        base = recolor(base, hue_shift)
        shaded = ShadedColor(
            highlight=recolor(shaded.highlight, hue_shift),
            base=recolor(shaded.base, hue_shift),
            shadow=recolor(shaded.shadow, hue_shift),
        )
    frames = []
    # Frame 0: flash
    frames.append(_apply_flash(_draw_slime_frame(0, base, eye, shaded), 0.5))
    # Frame 1: flatten (very squished)
    frames.append(_draw_slime_frame(1, base, eye, shaded))
    # Frame 2: shrink
    f2 = _draw_slime_frame(1, base, eye, shaded)
    frames.append(_shrink_sprite(f2, 0.5))
    # Frame 3: dissolve (tiny + faded)
    f3 = _draw_slime_frame(1, base, eye, shaded)
    frames.append(_shrink_sprite(f3, 0.2))
    return SpriteSheet(f"slime{name_suffix}_death", frames, frame_duration_ms=100, loop=False,
                       frame_durations_ms=[80, 100, 120, 150])


# ============================================================
# SKELETON
# ============================================================

def generate_skeleton() -> SpriteSheet:
    e = ENEMIES
    bone = e.base("skeleton")
    shade = e.colors["skeleton"]
    frames = []

    for f in range(4):
        img = new_sprite()
        y_off = 1 if f in (1, 3) else 0

        # Skull
        for x in range(5, 11):
            for y in range(2, 6):
                put_pixel(img, x, y + y_off, bone)
        # Eye sockets
        put_pixel(img, 6, 4 + y_off, (40, 20, 20))
        put_pixel(img, 9, 4 + y_off, (40, 20, 20))
        # Jaw
        put_pixel(img, 7, 5 + y_off, shade.shadow)
        put_pixel(img, 8, 5 + y_off, shade.shadow)
        # Spine
        for y in range(6, 10):
            put_pixel(img, 7, y + y_off, bone)
            put_pixel(img, 8, y + y_off, bone)
        # Ribs
        for y in range(7, 9):
            put_pixel(img, 5, y + y_off, shade.shadow)
            put_pixel(img, 6, y + y_off, bone)
            put_pixel(img, 9, y + y_off, bone)
            put_pixel(img, 10, y + y_off, shade.shadow)
        # Arms (sway)
        arm_off = 1 if f % 2 == 0 else 0
        put_pixel(img, 4, 7 + y_off + arm_off, bone)
        put_pixel(img, 3, 8 + y_off + arm_off, bone)
        put_pixel(img, 11, 7 + y_off, bone)
        put_pixel(img, 12, 8 + y_off, bone)
        # Legs
        for y in range(10, 14):
            put_pixel(img, 6, y + y_off, bone)
            put_pixel(img, 9, y + y_off, bone)
        put_pixel(img, 5, 14 + y_off, bone)
        put_pixel(img, 10, 14 + y_off, bone)

        shade_map = {bone: shade}
        frames.append(_shade_and_outline(img, shade_map))

    return SpriteSheet("skeleton", frames, frame_duration_ms=200)


def generate_skeleton_hit() -> SpriteSheet:
    idle = generate_skeleton()
    f0 = _apply_flash(idle.frames[0], 0.7)
    f1 = idle.frames[1]
    return SpriteSheet("skeleton_hit", [f0, f1], frame_duration_ms=80, loop=False,
                       frame_durations_ms=[60, 100])


def generate_skeleton_death() -> SpriteSheet:
    idle = generate_skeleton()
    frames = [
        _apply_flash(idle.frames[0], 0.5),
        idle.frames[2],
        _shrink_sprite(idle.frames[0], 0.6),
        _shrink_sprite(idle.frames[0], 0.2),
    ]
    return SpriteSheet("skeleton_death", frames, frame_duration_ms=100, loop=False,
                       frame_durations_ms=[80, 100, 120, 150])


# ============================================================
# BAT (6-frame wing flap)
# ============================================================

def generate_bat() -> SpriteSheet:
    e = ENEMIES
    body_c = e.base("bat")
    shade = e.colors["bat"]
    eye_c = e.base("eyes_red")
    frames = []

    wing_angles = [0, 1, 2, 2, 1, 0]  # up, mid, down, down, mid, up

    for f in range(6):
        img = new_sprite()
        # Body
        for x in range(6, 10):
            for y in range(6, 10):
                put_pixel(img, x, y, body_c)
        # Ears
        put_pixel(img, 6, 5, body_c)
        put_pixel(img, 9, 5, body_c)
        # Eyes
        put_pixel(img, 7, 7, eye_c)
        put_pixel(img, 8, 7, eye_c)
        # Fangs
        put_pixel(img, 7, 9, (255, 255, 255))

        # Wings based on angle
        wa = wing_angles[f]
        for i in range(4):
            if wa == 0:  # Up
                put_pixel(img, 5 - i, 5 - i, shade.shadow)
                put_pixel(img, 5 - i, 6 - i, body_c)
                put_pixel(img, 10 + i, 5 - i, shade.shadow)
                put_pixel(img, 10 + i, 6 - i, body_c)
            elif wa == 1:  # Mid
                put_pixel(img, 5 - i, 7, shade.shadow)
                put_pixel(img, 5 - i, 6, body_c)
                put_pixel(img, 10 + i, 7, shade.shadow)
                put_pixel(img, 10 + i, 6, body_c)
            else:  # Down
                put_pixel(img, 5 - i, 8 + i, shade.shadow)
                put_pixel(img, 5 - i, 7 + i, body_c)
                put_pixel(img, 10 + i, 8 + i, shade.shadow)
                put_pixel(img, 10 + i, 7 + i, body_c)

        shade_map = {body_c: shade}
        frames.append(_shade_and_outline(img, shade_map))

    return SpriteSheet("bat", frames, frame_duration_ms=80)


def generate_bat_hit() -> SpriteSheet:
    idle = generate_bat()
    f0 = _apply_flash(idle.frames[0], 0.7)
    f1 = idle.frames[3]  # wings down = recoil look
    return SpriteSheet("bat_hit", [f0, f1], frame_duration_ms=80, loop=False,
                       frame_durations_ms=[60, 100])


def generate_bat_death() -> SpriteSheet:
    idle = generate_bat()
    frames = [
        _apply_flash(idle.frames[2], 0.5),  # flash with wings down
        idle.frames[3],
        _shrink_sprite(idle.frames[3], 0.6),
        _shrink_sprite(idle.frames[3], 0.2),
    ]
    return SpriteSheet("bat_death", frames, frame_duration_ms=100, loop=False,
                       frame_durations_ms=[80, 100, 120, 150])


# ============================================================
# GHOST (8-frame float + wave)
# ============================================================

def generate_ghost() -> SpriteSheet:
    e = ENEMIES
    body_c = e.base("ghost")
    shade = e.colors["ghost"]
    eye_c = (150, 170, 220)
    frames = []

    for f in range(8):
        img = new_sprite()
        y_off = [0, 0, 1, 1, 1, 0, 0, 0][f]

        # Body (oval)
        for x in range(4, 12):
            for y in range(3, 12):
                # Rough oval shape
                cx_d = abs(x - 7.5)
                if y < 5 and cx_d > 2:
                    continue
                put_pixel(img, x, y + y_off, body_c)

        # Wavy bottom
        for x in range(4, 12):
            wave = 1 if (x + f) % 3 == 0 else 0
            put_pixel(img, x, 12 + wave + y_off, body_c)
            if wave == 0:
                put_pixel(img, x, 13 + y_off, body_c)

        # Eyes
        put_pixel(img, 6, 6 + y_off, eye_c)
        put_pixel(img, 9, 6 + y_off, eye_c)
        # Mouth
        put_pixel(img, 7, 8 + y_off, eye_c)
        put_pixel(img, 8, 8 + y_off, eye_c)

        # Semi-transparent effect
        shade_map = {body_c: shade}
        frames.append(_shade_and_outline(img, shade_map))

    return SpriteSheet("ghost", frames, frame_duration_ms=150)


def generate_ghost_hit() -> SpriteSheet:
    idle = generate_ghost()
    f0 = _apply_flash(idle.frames[0], 0.7)
    f1 = idle.frames[2]
    return SpriteSheet("ghost_hit", [f0, f1], frame_duration_ms=80, loop=False,
                       frame_durations_ms=[60, 100])


def generate_ghost_death() -> SpriteSheet:
    """Ghost fades out instead of shrinking."""
    idle = generate_ghost()
    frames = []
    base = idle.frames[0]
    alphas = [200, 140, 80, 30]
    for alpha in alphas:
        faded = base.copy()
        w, h = faded.size
        for y in range(h):
            for x in range(w):
                px = faded.getpixel((x, y))
                if px[3] > 0:
                    faded.putpixel((x, y), (px[0], px[1], px[2], min(px[3], alpha)))
        frames.append(faded)
    return SpriteSheet("ghost_death", frames, frame_duration_ms=100, loop=False,
                       frame_durations_ms=[80, 120, 150, 180])


# ============================================================
# GOBLIN
# ============================================================

def generate_goblin() -> SpriteSheet:
    e = ENEMIES
    g = e.base("goblin")
    shade = e.colors["goblin"]
    eye_c = e.base("eyes_red")
    armor = (120, 80, 40)
    frames = []

    for f in range(4):
        img = new_sprite()
        y_off = 1 if f in (1, 3) else 0

        # Head
        for x in range(5, 11):
            for y in range(2, 6):
                put_pixel(img, x, y + y_off, g)
        # Pointy ears
        put_pixel(img, 4, 3 + y_off, g)
        put_pixel(img, 3, 2 + y_off, shade.shadow)
        put_pixel(img, 11, 3 + y_off, g)
        put_pixel(img, 12, 2 + y_off, shade.shadow)
        # Eyes
        put_pixel(img, 6, 4 + y_off, eye_c)
        put_pixel(img, 9, 4 + y_off, eye_c)
        # Teeth
        put_pixel(img, 7, 5 + y_off, (255, 255, 240))
        put_pixel(img, 8, 5 + y_off, (255, 255, 240))
        # Body (leather armor)
        for x in range(5, 11):
            for y in range(6, 10):
                put_pixel(img, x, y + y_off, armor)
        # Arms
        for y in range(6, 9):
            put_pixel(img, 4, y + y_off, g)
            put_pixel(img, 11, y + y_off, g)
        # Legs
        for y in range(10, 14):
            put_pixel(img, 6, y + y_off, shade.shadow)
            put_pixel(img, 9, y + y_off, shade.shadow)
        put_pixel(img, 5, 14 + y_off, shade.shadow)
        put_pixel(img, 10, 14 + y_off, shade.shadow)

        shade_map = {g: shade}
        frames.append(_shade_and_outline(img, shade_map))

    return SpriteSheet("goblin", frames, frame_duration_ms=150)


def generate_goblin_hit() -> SpriteSheet:
    idle = generate_goblin()
    f0 = _apply_flash(idle.frames[0], 0.7)
    f1 = idle.frames[1]
    return SpriteSheet("goblin_hit", [f0, f1], frame_duration_ms=80, loop=False,
                       frame_durations_ms=[60, 100])


def generate_goblin_death() -> SpriteSheet:
    idle = generate_goblin()
    frames = [
        _apply_flash(idle.frames[0], 0.5),
        idle.frames[2],
        _shrink_sprite(idle.frames[0], 0.6),
        _shrink_sprite(idle.frames[0], 0.2),
    ]
    return SpriteSheet("goblin_death", frames, frame_duration_ms=100, loop=False,
                       frame_durations_ms=[80, 100, 120, 150])


def generate_all() -> list:
    """Generate all enemy sprites including idle, hit, and death animations."""
    return [
        # Slime variants (idle + hit + death)
        generate_slime(0.0, ""),
        generate_slime_hit(0.0, ""),
        generate_slime_death(0.0, ""),
        generate_slime(200.0, "_blue"),
        generate_slime_hit(200.0, "_blue"),
        generate_slime_death(200.0, "_blue"),
        generate_slime(320.0, "_red"),
        generate_slime_hit(320.0, "_red"),
        generate_slime_death(320.0, "_red"),
        # Skeleton
        generate_skeleton(),
        generate_skeleton_hit(),
        generate_skeleton_death(),
        # Bat
        generate_bat(),
        generate_bat_hit(),
        generate_bat_death(),
        # Ghost
        generate_ghost(),
        generate_ghost_hit(),
        generate_ghost_death(),
        # Goblin
        generate_goblin(),
        generate_goblin_hit(),
        generate_goblin_death(),
    ]
