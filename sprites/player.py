"""
Player character sprites: 4-directional animations for idle, walk, run,
attack, jump, hit, and death. With outline and 3-tier shading applied.
"""

from engine.drawing import (
    new_sprite, put_pixel, draw_outline, draw_outline_thick, apply_shading_auto,
    mirror_horizontal, draw_rect, get_pixel,
)
from engine.palette import PLAYER, ShadedColor, TRANSPARENT
from engine.sprite import SpriteSheet, DirectionalSprite

# Shading map for auto-shading pass
_SHADE_MAP = {
    PLAYER.base("skin"): PLAYER.colors["skin"],
    PLAYER.base("shirt"): PLAYER.colors["shirt"],
    PLAYER.base("pants"): PLAYER.colors["pants"],
    PLAYER.base("boots"): PLAYER.colors["boots"],
    PLAYER.base("hair"): PLAYER.colors["hair"],
    PLAYER.base("belt"): PLAYER.colors["belt"],
}


def _draw_player_right(y_off: int = 0, arm_swing: int = 0) -> "Image.Image":
    """Draw base player facing right."""
    img = new_sprite()
    p = PLAYER

    # Head
    for x in range(5, 11):
        for y in range(2, 6):
            put_pixel(img, x, y + y_off, p.base("skin"))
    # Hair
    for x in range(5, 11):
        put_pixel(img, x, 2 + y_off, p.base("hair"))
    put_pixel(img, 5, 3 + y_off, p.base("hair"))
    put_pixel(img, 5, 4 + y_off, p.base("hair"))
    # Eyes
    put_pixel(img, 8, 4 + y_off, p.base("eyes"))
    put_pixel(img, 9, 4 + y_off, p.base("eyes"))
    # Mouth hint
    put_pixel(img, 8, 5 + y_off, p.shadow("skin"))
    # Body/shirt
    for x in range(5, 11):
        for y in range(6, 10):
            put_pixel(img, x, y + y_off, p.base("shirt"))
    # Belt
    for x in range(5, 11):
        put_pixel(img, x, 9 + y_off, p.base("belt"))
    # Arms
    for y in range(6, 9):
        arm_y = y + y_off + (arm_swing if y == 8 else 0)
        put_pixel(img, 4, arm_y, p.base("skin"))
        put_pixel(img, 11, arm_y, p.base("skin"))
    # Pants
    for y in range(10, 13):
        for x in [6, 7, 8, 9]:
            put_pixel(img, x, y + y_off, p.base("pants"))
    # Boots
    for pos in [(5, 13), (6, 13), (9, 13), (10, 13)]:
        put_pixel(img, pos[0], pos[1] + y_off, p.base("boots"))

    return img


def _draw_player_down(y_off: int = 0) -> "Image.Image":
    """Draw player facing down (toward camera)."""
    img = new_sprite()
    p = PLAYER

    # Head (wider, centered)
    for x in range(5, 11):
        for y in range(2, 6):
            put_pixel(img, x, y + y_off, p.base("skin"))
    # Hair (top)
    for x in range(5, 11):
        put_pixel(img, x, 2 + y_off, p.base("hair"))
    # Eyes (centered, wider apart)
    put_pixel(img, 6, 4 + y_off, p.base("eyes"))
    put_pixel(img, 9, 4 + y_off, p.base("eyes"))
    # Mouth
    put_pixel(img, 7, 5 + y_off, p.shadow("skin"))
    put_pixel(img, 8, 5 + y_off, p.shadow("skin"))
    # Body
    for x in range(5, 11):
        for y in range(6, 10):
            put_pixel(img, x, y + y_off, p.base("shirt"))
    # Belt
    for x in range(5, 11):
        put_pixel(img, x, 9 + y_off, p.base("belt"))
    # Arms
    for y in range(6, 9):
        put_pixel(img, 4, y + y_off, p.base("skin"))
        put_pixel(img, 11, y + y_off, p.base("skin"))
    # Pants
    for y in range(10, 13):
        for x in [6, 7, 8, 9]:
            put_pixel(img, x, y + y_off, p.base("pants"))
    # Boots
    for pos in [(5, 13), (6, 13), (9, 13), (10, 13)]:
        put_pixel(img, pos[0], pos[1] + y_off, p.base("boots"))
    return img


def _draw_player_up(y_off: int = 0) -> "Image.Image":
    """Draw player facing up (away from camera)."""
    img = new_sprite()
    p = PLAYER

    # Head - back of head, all hair
    for x in range(5, 11):
        for y in range(2, 6):
            put_pixel(img, x, y + y_off, p.base("hair"))
    # Body
    for x in range(5, 11):
        for y in range(6, 10):
            put_pixel(img, x, y + y_off, p.base("shirt"))
    # Belt
    for x in range(5, 11):
        put_pixel(img, x, 9 + y_off, p.base("belt"))
    # Arms
    for y in range(6, 9):
        put_pixel(img, 4, y + y_off, p.base("skin"))
        put_pixel(img, 11, y + y_off, p.base("skin"))
    # Pants
    for y in range(10, 13):
        for x in [6, 7, 8, 9]:
            put_pixel(img, x, y + y_off, p.base("pants"))
    # Boots
    for pos in [(5, 13), (6, 13), (9, 13), (10, 13)]:
        put_pixel(img, pos[0], pos[1] + y_off, p.base("boots"))
    return img


def _finalize(img):
    """Apply shading and outline to a player frame."""
    img = apply_shading_auto(img, _SHADE_MAP)
    return draw_outline_thick(img)


def generate_idle_right() -> SpriteSheet:
    frames = []
    # 8 frames: subtle breathing (body expansion) + blink at frame 5
    bob_pattern = [0, 0, 0, 1, 1, 0, 0, 0]
    for i in range(8):
        frame = _draw_player_right(y_off=bob_pattern[i])
        # Blink on frame 5
        if i == 5:
            put_pixel(frame, 8, 4 + bob_pattern[i], PLAYER.base("skin"))
            put_pixel(frame, 9, 4 + bob_pattern[i], PLAYER.base("skin"))
        frames.append(_finalize(frame))
    return SpriteSheet("player_idle_right", frames, frame_duration_ms=150)


def generate_idle_down() -> SpriteSheet:
    frames = []
    bob_pattern = [0, 0, 0, 1, 1, 0, 0, 0]
    for i in range(8):
        frame = _draw_player_down(y_off=bob_pattern[i])
        if i == 5:
            put_pixel(frame, 6, 4 + bob_pattern[i], PLAYER.base("skin"))
            put_pixel(frame, 9, 4 + bob_pattern[i], PLAYER.base("skin"))
        frames.append(_finalize(frame))
    return SpriteSheet("player_idle_down", frames, frame_duration_ms=150)


def generate_idle_up() -> SpriteSheet:
    frames = []
    bob_pattern = [0, 0, 0, 1, 1, 0, 0, 0]
    for i in range(8):
        frame = _draw_player_up(y_off=bob_pattern[i])
        frames.append(_finalize(frame))
    return SpriteSheet("player_idle_up", frames, frame_duration_ms=150)


def generate_walk_right() -> SpriteSheet:
    frames = []
    # 8 frames: 2 full step cycles
    bob =       [0, 1, 0, 0, 0, 1, 0, 0]
    leg_offsets = [
        [(6, 13), (9, 12)],  # right foot forward
        [(5, 13), (10, 12)],
        [(6, 12), (9, 13)],  # left foot forward
        [(6, 13), (9, 13)],  # together
        [(7, 12), (8, 13)],
        [(5, 13), (10, 12)],
        [(6, 13), (9, 12)],
        [(6, 13), (9, 13)],
    ]
    arm_swings = [0, 1, 0, -1, 0, 1, 0, -1]

    for i in range(8):
        frame = _draw_player_right(y_off=bob[i], arm_swing=arm_swings[i])
        # Override boots for walk
        b = bob[i]
        for x in range(4, 12):
            put_pixel(frame, x, 13 + b, (0, 0, 0, 0))
            put_pixel(frame, x, 14, (0, 0, 0, 0))
        for pos in leg_offsets[i]:
            put_pixel(frame, pos[0], pos[1] + b, PLAYER.base("boots"))
            put_pixel(frame, pos[0] + 1, pos[1] + b, PLAYER.base("boots"))
        frames.append(_finalize(frame))
    return SpriteSheet("player_walk_right", frames, frame_duration_ms=100)


def generate_walk_down() -> SpriteSheet:
    frames = []
    bob = [0, 1, 0, 0, 0, 1, 0, 0]
    leg_offsets = [
        [(5, 13), (10, 13)],
        [(5, 14), (10, 12)],
        [(6, 13), (9, 13)],
        [(5, 13), (10, 13)],
        [(5, 12), (10, 14)],
        [(5, 13), (10, 13)],
        [(6, 13), (9, 13)],
        [(5, 13), (10, 13)],
    ]
    for i in range(8):
        frame = _draw_player_down(y_off=bob[i])
        b = bob[i]
        for x in range(4, 12):
            put_pixel(frame, x, 13 + b, (0, 0, 0, 0))
        for pos in leg_offsets[i]:
            put_pixel(frame, pos[0], pos[1] + b, PLAYER.base("boots"))
            put_pixel(frame, pos[0] + 1, pos[1] + b, PLAYER.base("boots"))
        frames.append(_finalize(frame))
    return SpriteSheet("player_walk_down", frames, frame_duration_ms=100)


def generate_walk_up() -> SpriteSheet:
    frames = []
    bob = [0, 1, 0, 0, 0, 1, 0, 0]
    for i in range(8):
        frame = _draw_player_up(y_off=bob[i])
        frames.append(_finalize(frame))
    return SpriteSheet("player_walk_up", frames, frame_duration_ms=100)


def _apply_flash(img, intensity: float = 0.7):
    """Apply a white flash effect to a sprite for hit feedback."""
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


# ============================================================
# RUN (8 frames, 80ms — faster walk with exaggerated movement)
# ============================================================

def generate_run_right() -> SpriteSheet:
    frames = []
    bob = [0, 1, 0, -1, 0, 1, 0, -1]  # more dynamic bob than walk
    leg_offsets = [
        [(5, 13), (10, 12)],  # wide stride
        [(4, 13), (11, 11)],  # max extension
        [(6, 12), (9, 13)],   # passing
        [(6, 13), (9, 13)],   # together
        [(10, 13), (5, 12)],  # opposite stride
        [(11, 13), (4, 11)],  # max extension
        [(9, 12), (6, 13)],   # passing
        [(6, 13), (9, 13)],   # together
    ]
    arm_swings = [1, 2, 1, 0, -1, -2, -1, 0]

    for i in range(8):
        frame = _draw_player_right(y_off=bob[i], arm_swing=arm_swings[i])
        b = bob[i]
        for x in range(3, 13):
            put_pixel(frame, x, 13 + b, (0, 0, 0, 0))
            put_pixel(frame, x, 14 + b, (0, 0, 0, 0))
        for pos in leg_offsets[i]:
            put_pixel(frame, pos[0], pos[1] + b, PLAYER.base("boots"))
            put_pixel(frame, pos[0] + 1, pos[1] + b, PLAYER.base("boots"))
        frames.append(_finalize(frame))
    return SpriteSheet("player_run_right", frames, frame_duration_ms=80)


def generate_run_down() -> SpriteSheet:
    frames = []
    bob = [0, 1, 0, -1, 0, 1, 0, -1]
    leg_offsets = [
        [(5, 14), (10, 12)],
        [(5, 13), (10, 13)],
        [(5, 12), (10, 14)],
        [(5, 13), (10, 13)],
        [(5, 12), (10, 14)],
        [(5, 13), (10, 13)],
        [(5, 14), (10, 12)],
        [(5, 13), (10, 13)],
    ]
    for i in range(8):
        frame = _draw_player_down(y_off=bob[i])
        b = bob[i]
        for x in range(4, 12):
            put_pixel(frame, x, 13 + b, (0, 0, 0, 0))
        for pos in leg_offsets[i]:
            put_pixel(frame, pos[0], pos[1] + b, PLAYER.base("boots"))
            put_pixel(frame, pos[0] + 1, pos[1] + b, PLAYER.base("boots"))
        frames.append(_finalize(frame))
    return SpriteSheet("player_run_down", frames, frame_duration_ms=80)


def generate_run_up() -> SpriteSheet:
    frames = []
    bob = [0, 1, 0, -1, 0, 1, 0, -1]
    for i in range(8):
        frame = _draw_player_up(y_off=bob[i])
        frames.append(_finalize(frame))
    return SpriteSheet("player_run_up", frames, frame_duration_ms=80)


# ============================================================
# ATTACK (6 frames, variable timing — 4 directions)
# ============================================================

def _draw_sword_pixels(img, positions, blade_color, guard_color, handle_color):
    """Draw a multi-pixel sword at given positions.
    positions: list of (x,y) from handle to tip."""
    if len(positions) >= 1:
        put_pixel(img, positions[0][0], positions[0][1], handle_color)
    if len(positions) >= 2:
        put_pixel(img, positions[1][0], positions[1][1], guard_color)
    for pos in positions[2:]:
        put_pixel(img, pos[0], pos[1], blade_color)
        # Add blade width (1px adjacent for thicker sword)
        put_pixel(img, pos[0], pos[1] - 1, blade_color)


def generate_attack_right() -> SpriteSheet:
    blade = PLAYER.highlight("belt")
    guard = (130, 85, 45)   # warm brown guard
    handle = (90, 58, 32)   # dark wood handle
    slash = (225, 225, 235)  # white slash trail
    frames = []

    # Frame 0: wind-up — sword behind, arm back
    f = _draw_player_right(arm_swing=-1)
    _draw_sword_pixels(f, [(11, 8), (12, 7), (13, 5), (13, 4), (14, 3)], blade, guard, handle)
    frames.append(_finalize(f))

    # Frame 1: raise overhead
    f = _draw_player_right(arm_swing=-1)
    _draw_sword_pixels(f, [(11, 5), (12, 4), (13, 2), (14, 1), (15, 0)], blade, guard, handle)
    frames.append(_finalize(f))

    # Frame 2: fast downward slash — sword diagonal with trail
    f = _draw_player_right()
    _draw_sword_pixels(f, [(12, 5), (13, 6), (14, 7), (15, 8)], blade, guard, handle)
    # Slash trail arc
    for pos in [(13, 3), (14, 4), (15, 5), (15, 6)]:
        put_pixel(f, pos[0], pos[1], slash)
    frames.append(_finalize(f))

    # Frame 3: impact — sword low, big slash arc
    f = _draw_player_right(arm_swing=1)
    _draw_sword_pixels(f, [(12, 8), (13, 9), (14, 10), (15, 11)], blade, guard, handle)
    # Wider slash trail
    for pos in [(12, 4), (13, 5), (14, 6), (15, 7), (14, 8), (13, 9)]:
        put_pixel(f, pos[0], pos[1], slash)
    frames.append(_finalize(f))

    # Frame 4: follow-through — sword past
    f = _draw_player_right(arm_swing=1)
    _draw_sword_pixels(f, [(12, 10), (13, 11), (14, 12)], blade, guard, handle)
    # Fading trail
    for pos in [(13, 8), (14, 9)]:
        put_pixel(f, pos[0], pos[1], (*slash[:3], 128))
    frames.append(_finalize(f))

    # Frame 5: recovery — sword at side
    f = _draw_player_right()
    _draw_sword_pixels(f, [(11, 7), (12, 8), (13, 9)], blade, guard, handle)
    frames.append(_finalize(f))

    return SpriteSheet("player_attack_right", frames, frame_duration_ms=80, loop=False,
                       frame_durations_ms=[100, 65, 35, 50, 80, 100])


def generate_attack_down() -> SpriteSheet:
    blade = PLAYER.highlight("belt")
    guard = (130, 85, 45)
    handle = (90, 58, 32)
    slash = (225, 225, 235)
    frames = []

    # Frame 0: raise sword overhead
    f = _draw_player_down()
    _draw_sword_pixels(f, [(8, 5), (8, 3), (8, 2), (8, 1), (8, 0)], blade, guard, handle)
    frames.append(_finalize(f))

    # Frame 1: sword wide overhead
    f = _draw_player_down()
    _draw_sword_pixels(f, [(7, 4), (6, 2), (5, 1), (4, 0)], blade, guard, handle)
    put_pixel(f, 10, 2, blade)
    put_pixel(f, 11, 1, blade)
    frames.append(_finalize(f))

    # Frame 2: fast swing down — sword in front with trail
    f = _draw_player_down()
    _draw_sword_pixels(f, [(8, 10), (8, 11), (8, 12), (8, 13), (8, 14)], blade, guard, handle)
    for pos in [(7, 4), (6, 6), (7, 8), (8, 9), (9, 8), (10, 6), (9, 4)]:
        put_pixel(f, pos[0], pos[1], slash)
    frames.append(_finalize(f))

    # Frame 3: impact — sword low, wide slash
    f = _draw_player_down()
    for x in range(4, 12):
        put_pixel(f, x, 14, blade)
        put_pixel(f, x, 15, slash)
    frames.append(_finalize(f))

    # Frame 4: recovery
    f = _draw_player_down()
    _draw_sword_pixels(f, [(11, 8), (12, 9), (13, 10)], blade, guard, handle)
    frames.append(_finalize(f))

    # Frame 5: sheathe
    f = _draw_player_down()
    _draw_sword_pixels(f, [(11, 7), (12, 8)], blade, guard, handle)
    frames.append(_finalize(f))

    return SpriteSheet("player_attack_down", frames, frame_duration_ms=80, loop=False,
                       frame_durations_ms=[100, 65, 35, 50, 80, 100])


def generate_attack_up() -> SpriteSheet:
    blade = PLAYER.highlight("belt")
    guard = (130, 85, 45)
    handle = (90, 58, 32)
    slash = (225, 225, 235)
    frames = []

    # Frame 0: wind-up — sword low behind
    f = _draw_player_up()
    _draw_sword_pixels(f, [(8, 12), (8, 13), (8, 14)], blade, guard, handle)
    frames.append(_finalize(f))

    # Frame 1: raising sword
    f = _draw_player_up()
    _draw_sword_pixels(f, [(8, 8), (8, 6), (8, 4), (8, 3)], blade, guard, handle)
    frames.append(_finalize(f))

    # Frame 2: overhead slash with trail
    f = _draw_player_up()
    _draw_sword_pixels(f, [(8, 4), (7, 2), (6, 1), (5, 0)], blade, guard, handle)
    put_pixel(f, 10, 2, blade)
    put_pixel(f, 11, 1, blade)
    for pos in [(7, 6), (6, 4), (8, 4), (9, 3), (10, 3)]:
        put_pixel(f, pos[0], pos[1], slash)
    frames.append(_finalize(f))

    # Frame 3: wide arc — slash trails
    f = _draw_player_up()
    for x in range(4, 12):
        put_pixel(f, x, 1, blade)
        put_pixel(f, x, 0, slash)
    frames.append(_finalize(f))

    # Frame 4: follow-through
    f = _draw_player_up()
    _draw_sword_pixels(f, [(5, 5), (4, 4), (3, 3)], blade, guard, handle)
    frames.append(_finalize(f))

    # Frame 5: recovery
    f = _draw_player_up()
    _draw_sword_pixels(f, [(5, 7), (4, 8)], blade, guard, handle)
    frames.append(_finalize(f))

    return SpriteSheet("player_attack_up", frames, frame_duration_ms=80, loop=False,
                       frame_durations_ms=[100, 65, 35, 50, 80, 100])


# ============================================================
# JUMP (4 frames, variable timing)
# ============================================================

def generate_jump_right() -> SpriteSheet:
    frames = []
    # Frame 0: crouch (y_off=2 pushes down)
    frame = _draw_player_right(y_off=2)
    frames.append(_finalize(frame))
    # Frame 1: launch (y_off=-2 pushes up, arms up)
    frame = _draw_player_right(y_off=-2, arm_swing=-1)
    frames.append(_finalize(frame))
    # Frame 2: apex (y_off=-3, stretched)
    frame = _draw_player_right(y_off=-3, arm_swing=-1)
    frames.append(_finalize(frame))
    # Frame 3: fall (y_off=-1, legs tucked)
    frame = _draw_player_right(y_off=-1, arm_swing=1)
    frames.append(_finalize(frame))
    return SpriteSheet("player_jump_right", frames, frame_duration_ms=100, loop=False,
                       frame_durations_ms=[100, 80, 80, 120])


def generate_jump_down() -> SpriteSheet:
    frames = []
    offsets = [2, -2, -3, -1]
    for y_off in offsets:
        frame = _draw_player_down(y_off=y_off)
        frames.append(_finalize(frame))
    return SpriteSheet("player_jump_down", frames, frame_duration_ms=100, loop=False,
                       frame_durations_ms=[100, 80, 80, 120])


def generate_jump_up() -> SpriteSheet:
    frames = []
    offsets = [2, -2, -3, -1]
    for y_off in offsets:
        frame = _draw_player_up(y_off=y_off)
        frames.append(_finalize(frame))
    return SpriteSheet("player_jump_up", frames, frame_duration_ms=100, loop=False,
                       frame_durations_ms=[100, 80, 80, 120])


# ============================================================
# HIT (3 frames, variable timing — flash + recoil)
# ============================================================

def generate_hit_right() -> SpriteSheet:
    frames = []
    # Frame 0: white flash
    base = _draw_player_right()
    frames.append(_apply_flash(_finalize(base), 0.7))
    # Frame 1: recoil (shifted left)
    recoil = _draw_player_right(y_off=1)
    frames.append(_finalize(recoil))
    # Frame 2: recovery
    recover = _draw_player_right()
    frames.append(_finalize(recover))
    return SpriteSheet("player_hit_right", frames, frame_duration_ms=80, loop=False,
                       frame_durations_ms=[60, 100, 80])


def generate_hit_down() -> SpriteSheet:
    frames = []
    base = _draw_player_down()
    frames.append(_apply_flash(_finalize(base), 0.7))
    recoil = _draw_player_down(y_off=1)
    frames.append(_finalize(recoil))
    recover = _draw_player_down()
    frames.append(_finalize(recover))
    return SpriteSheet("player_hit_down", frames, frame_duration_ms=80, loop=False,
                       frame_durations_ms=[60, 100, 80])


def generate_hit_up() -> SpriteSheet:
    frames = []
    base = _draw_player_up()
    frames.append(_apply_flash(_finalize(base), 0.7))
    recoil = _draw_player_up(y_off=1)
    frames.append(_finalize(recoil))
    recover = _draw_player_up()
    frames.append(_finalize(recover))
    return SpriteSheet("player_hit_up", frames, frame_duration_ms=80, loop=False,
                       frame_durations_ms=[60, 100, 80])


# ============================================================
# DEATH (6 frames, variable timing — stagger + collapse)
# ============================================================

def generate_death_right() -> SpriteSheet:
    frames = []
    # Frame 0: hit flash
    base = _draw_player_right()
    frames.append(_apply_flash(_finalize(base), 0.5))
    # Frame 1: stagger back
    stagger = _draw_player_right(y_off=1)
    frames.append(_finalize(stagger))
    # Frame 2: knees buckling (lower)
    kneel = _draw_player_right(y_off=2)
    frames.append(_finalize(kneel))
    # Frame 3: falling (more lower, tilted by shifting pixels)
    fall = _draw_player_right(y_off=3)
    frames.append(_finalize(fall))
    # Frame 4: nearly flat — draw collapsed version
    img = new_sprite()
    p = PLAYER
    # Horizontal body on ground
    for x in range(3, 13):
        put_pixel(img, x, 13, p.base("shirt"))
        put_pixel(img, x, 14, p.base("pants"))
    for x in range(3, 6):
        put_pixel(img, x, 13, p.base("skin"))  # head
    put_pixel(img, 4, 12, p.base("hair"))
    put_pixel(img, 3, 12, p.base("hair"))
    frames.append(_finalize(img))
    # Frame 5: flat with fade
    flat = img.copy()
    flat_final = _finalize(flat)
    # Dim the sprite slightly
    w, h = flat_final.size
    dimmed = flat_final.copy()
    for y in range(h):
        for x in range(w):
            px = dimmed.getpixel((x, y))
            if px[3] > 0:
                dimmed.putpixel((x, y), (px[0] // 2, px[1] // 2, px[2] // 2, px[3]))
    frames.append(dimmed)
    return SpriteSheet("player_death_right", frames, frame_duration_ms=100, loop=False,
                       frame_durations_ms=[80, 100, 120, 120, 150, 150])


def generate_death_down() -> SpriteSheet:
    frames = []
    base = _draw_player_down()
    frames.append(_apply_flash(_finalize(base), 0.5))
    frames.append(_finalize(_draw_player_down(y_off=1)))
    frames.append(_finalize(_draw_player_down(y_off=2)))
    frames.append(_finalize(_draw_player_down(y_off=3)))
    # Collapsed
    img = new_sprite()
    p = PLAYER
    for x in range(3, 13):
        put_pixel(img, x, 13, p.base("shirt"))
        put_pixel(img, x, 14, p.base("pants"))
    for x in range(3, 6):
        put_pixel(img, x, 13, p.base("skin"))
    put_pixel(img, 4, 12, p.base("hair"))
    frames.append(_finalize(img))
    # Dimmed
    dimmed = _finalize(img.copy())
    w, h = dimmed.size
    for y in range(h):
        for x in range(w):
            px = dimmed.getpixel((x, y))
            if px[3] > 0:
                dimmed.putpixel((x, y), (px[0] // 2, px[1] // 2, px[2] // 2, px[3]))
    frames.append(dimmed)
    return SpriteSheet("player_death_down", frames, frame_duration_ms=100, loop=False,
                       frame_durations_ms=[80, 100, 120, 120, 150, 150])


def generate_death_up() -> SpriteSheet:
    frames = []
    base = _draw_player_up()
    frames.append(_apply_flash(_finalize(base), 0.5))
    frames.append(_finalize(_draw_player_up(y_off=1)))
    frames.append(_finalize(_draw_player_up(y_off=2)))
    frames.append(_finalize(_draw_player_up(y_off=3)))
    img = new_sprite()
    p = PLAYER
    for x in range(3, 13):
        put_pixel(img, x, 13, p.base("shirt"))
        put_pixel(img, x, 14, p.base("pants"))
    for x in range(10, 13):
        put_pixel(img, x, 13, p.base("hair"))
    frames.append(_finalize(img))
    dimmed = _finalize(img.copy())
    w, h = dimmed.size
    for y in range(h):
        for x in range(w):
            px = dimmed.getpixel((x, y))
            if px[3] > 0:
                dimmed.putpixel((x, y), (px[0] // 2, px[1] // 2, px[2] // 2, px[3]))
    frames.append(dimmed)
    return SpriteSheet("player_death_up", frames, frame_duration_ms=100, loop=False,
                       frame_durations_ms=[80, 100, 120, 120, 150, 150])


# ============================================================
# GENERATE ALL
# ============================================================

def generate_all() -> list:
    """Generate all player sprites. Returns list of SpriteSheet/DirectionalSprite."""
    idle_right = generate_idle_right()
    idle_down = generate_idle_down()
    idle_up = generate_idle_up()

    walk_right = generate_walk_right()
    walk_down = generate_walk_down()
    walk_up = generate_walk_up()

    run_right = generate_run_right()
    run_down = generate_run_down()
    run_up = generate_run_up()

    attack_right = generate_attack_right()
    attack_down = generate_attack_down()
    attack_up = generate_attack_up()

    jump_right = generate_jump_right()
    jump_down = generate_jump_down()
    jump_up = generate_jump_up()

    hit_right = generate_hit_right()
    hit_down = generate_hit_down()
    hit_up = generate_hit_up()

    death_right = generate_death_right()
    death_down = generate_death_down()
    death_up = generate_death_up()

    idle_dir = DirectionalSprite(
        name="player_idle", down=idle_down, up=idle_up, right=idle_right,
    )
    walk_dir = DirectionalSprite(
        name="player_walk", down=walk_down, up=walk_up, right=walk_right,
    )
    run_dir = DirectionalSprite(
        name="player_run", down=run_down, up=run_up, right=run_right,
    )
    attack_dir = DirectionalSprite(
        name="player_attack", down=attack_down, up=attack_up, right=attack_right,
    )
    jump_dir = DirectionalSprite(
        name="player_jump", down=jump_down, up=jump_up, right=jump_right,
    )
    hit_dir = DirectionalSprite(
        name="player_hit", down=hit_down, up=hit_up, right=hit_right,
    )
    death_dir = DirectionalSprite(
        name="player_death", down=death_down, up=death_up, right=death_right,
    )

    return [idle_dir, walk_dir, run_dir, attack_dir, jump_dir, hit_dir, death_dir]
