"""
Terrain tiles with fractal noise and auto-tile edge variants.
"""

from engine.drawing import new_sprite, put_pixel, dither_fill, draw_outline_thick
from engine.palette import TERRAIN, TRANSPARENT
from engine.noise import noise_map, fractal_noise
from engine.sprite import SpriteSheet, StaticSprite


def _noise_tile(name: str, color_key: str, seed: int, octaves: int = 3,
                base_scale: float = 0.3) -> StaticSprite:
    """Generate a 16x16 terrain tile using fractal noise for variation."""
    t = TERRAIN
    img = new_sprite()
    nmap = noise_map(16, 16, seed=seed, octaves=octaves, base_scale=base_scale)

    for y in range(16):
        for x in range(16):
            v = nmap[y][x]
            if v < 0.33:
                color = t.shadow(color_key)
            elif v < 0.66:
                color = t.base(color_key)
            else:
                color = t.highlight(color_key)
            put_pixel(img, x, y, color)

    return StaticSprite(name, img, "terrain")


def generate_grass(seed: int = 42) -> StaticSprite:
    tile = _noise_tile("grass", "grass", seed, base_scale=0.25)
    # Add grass blade details
    nmap = noise_map(16, 16, seed=seed + 100, octaves=1, base_scale=0.5)
    for x in range(0, 16, 2):
        for y in range(0, 16, 3):
            if nmap[y][x] > 0.6:
                put_pixel(tile.image, x, y, TERRAIN.highlight("grass"))
    return tile


def generate_dirt(seed: int = 100) -> StaticSprite:
    tile = _noise_tile("dirt", "dirt", seed, base_scale=0.3)
    # Pebble details
    nmap = noise_map(16, 16, seed=seed + 50, octaves=1, base_scale=0.6)
    for y in range(16):
        for x in range(16):
            if nmap[y][x] > 0.8:
                put_pixel(tile.image, x, y, TERRAIN.shadow("stone"))
    return tile


def generate_stone(seed: int = 200) -> StaticSprite:
    tile = _noise_tile("stone", "stone", seed, base_scale=0.2)
    # Crack details
    for i in range(3, 9):
        v = fractal_noise(i, 7, seed + 300, 1, 0.5, 0.4)
        crack_y = 7 + int(v * 2)
        put_pixel(tile.image, i, crack_y, TERRAIN.shadow("stone"))
    return tile


def generate_sand(seed: int = 300) -> StaticSprite:
    return _noise_tile("sand", "sand", seed, base_scale=0.35)


def generate_wood_floor(seed: int = 400) -> StaticSprite:
    t = TERRAIN
    img = new_sprite()
    nmap = noise_map(16, 16, seed=seed, octaves=2, base_scale=0.15)

    for y in range(16):
        for x in range(16):
            # Wood grain: vertical lines with noise variation
            base_v = nmap[y][x]
            if x % 4 == 0:
                color = t.shadow("wood")
            elif base_v < 0.4:
                color = t.shadow("wood")
            elif base_v > 0.7:
                color = t.highlight("wood")
            else:
                color = t.base("wood")
            put_pixel(img, x, y, color)

    # Plank lines
    for y in [0, 5, 10, 15]:
        for x in range(16):
            put_pixel(img, x, y, t.shadow("wood"))

    return StaticSprite("wood_floor", img, "terrain")


def generate_snow(seed: int = 500) -> StaticSprite:
    return _noise_tile("snow", "snow", seed, base_scale=0.2)


def generate_tree() -> StaticSprite:
    t = TERRAIN
    img = new_sprite()

    # Trunk with shading
    for y in range(9, 15):
        put_pixel(img, 7, y, t.base("wood"))
        put_pixel(img, 8, y, t.shadow("wood"))
    put_pixel(img, 6, 14, t.shadow("wood"))
    put_pixel(img, 9, 14, t.shadow("wood"))

    # Leaves (rounded canopy with shading)
    leaf_rows = [
        (6, 10, 2),   # y, cx, r
        (5, 10, 3),
        (4, 10, 4),
        (4, 10, 4),
        (4, 10, 4),
        (5, 10, 3),
        (6, 10, 2),
    ]
    for i, (start_x, _, half_w) in enumerate(leaf_rows):
        y = 2 + i
        for x in range(8 - half_w, 8 + half_w):
            if (x + y) % 3 == 0:
                put_pixel(img, x, y, t.shadow("leaves"))
            elif (x + y) % 3 == 1:
                put_pixel(img, x, y, t.base("leaves"))
            else:
                put_pixel(img, x, y, t.highlight("leaves"))

    return StaticSprite("tree", img, "terrain")


# ============================================================
# ANIMATED TILES
# ============================================================

def generate_water(seed: int = 600) -> SpriteSheet:
    t = TERRAIN
    frames = []
    for f in range(8):
        img = new_sprite()
        nmap = noise_map(16, 16, seed=seed + f * 10, octaves=3, base_scale=0.25)
        for y in range(16):
            for x in range(16):
                v = nmap[y][x]
                if v < 0.3:
                    color = t.shadow("water")
                elif v < 0.6:
                    color = t.base("water")
                else:
                    color = t.highlight("water")
                put_pixel(img, x, y, color)
        # Wave highlights
        for x in range(0, 16, 3):
            wx = (x + f * 2) % 16
            put_pixel(img, wx, 4, (140, 210, 255))
            put_pixel(img, (wx + 8) % 16, 11, (140, 210, 255))
        frames.append(img)
    return SpriteSheet("water", frames, frame_duration_ms=200)


def generate_lava(seed: int = 700) -> SpriteSheet:
    t = TERRAIN
    frames = []
    for f in range(8):
        img = new_sprite()
        nmap = noise_map(16, 16, seed=seed + f * 15, octaves=3, base_scale=0.3)
        for y in range(16):
            for x in range(16):
                v = nmap[y][x]
                if v < 0.3:
                    color = t.shadow("lava")
                elif v < 0.6:
                    color = t.base("lava")
                elif v < 0.8:
                    color = t.base("lava_bright")
                else:
                    color = t.highlight("lava_bright")
                put_pixel(img, x, y, color)
        frames.append(img)
    return SpriteSheet("lava", frames, frame_duration_ms=150)


# ============================================================
# AUTO-TILE GENERATION (4-bit bitmask: N, E, S, W)
# ============================================================

def generate_autotile_set(base_tile: StaticSprite, edge_color: tuple,
                          name: str) -> list[StaticSprite]:
    """Generate 16 auto-tile variants using 4-bit edge bitmask.

    Bit 0 = North edge, Bit 1 = East edge, Bit 2 = South edge, Bit 3 = West edge.
    An edge bit = 1 means "no neighbor on that side" (draw border).
    """
    variants = []
    for mask in range(16):
        img = base_tile.image.copy()
        has_n = mask & 1
        has_e = mask & 2
        has_s = mask & 4
        has_w = mask & 8

        # Draw edges
        if has_n:
            for x in range(16):
                put_pixel(img, x, 0, edge_color)
                put_pixel(img, x, 1, edge_color)
        if has_s:
            for x in range(16):
                put_pixel(img, x, 14, edge_color)
                put_pixel(img, x, 15, edge_color)
        if has_w:
            for y in range(16):
                put_pixel(img, 0, y, edge_color)
                put_pixel(img, 1, y, edge_color)
        if has_e:
            for y in range(16):
                put_pixel(img, 14, y, edge_color)
                put_pixel(img, 15, y, edge_color)

        # Corner fills where two edges meet
        corners = [
            (has_n and has_w, 0, 0),
            (has_n and has_e, 14, 0),
            (has_s and has_w, 0, 14),
            (has_s and has_e, 14, 14),
        ]
        for condition, cx, cy in corners:
            if condition:
                for dx in range(2):
                    for dy in range(2):
                        put_pixel(img, cx + dx, cy + dy, edge_color)

        variants.append(StaticSprite(f"{name}_{mask:04b}", img, "terrain_autotile"))

    return variants


def generate_tileset() -> list[StaticSprite]:
    """Generate combined tileset of all static terrain tiles."""
    from engine.drawing import create_spritesheet
    tiles = [
        generate_grass(), generate_dirt(), generate_stone(),
        generate_sand(), generate_wood_floor(), generate_snow(),
    ]
    sheet = create_spritesheet([t.image for t in tiles], columns=3)
    return [StaticSprite("tileset", sheet, "terrain")] + tiles


def generate_all() -> list:
    """Generate all terrain assets."""
    results = []

    # Static tiles
    grass = generate_grass()
    dirt = generate_dirt()
    stone = generate_stone()
    results.extend([grass, dirt, stone, generate_sand(),
                    generate_wood_floor(), generate_snow(), generate_tree()])

    # Animated tiles
    results.extend([generate_water(), generate_lava()])

    # Tileset
    from engine.drawing import create_spritesheet
    static_tiles = [grass.image, dirt.image, stone.image,
                    generate_sand().image, generate_wood_floor().image, generate_snow().image]
    results.append(StaticSprite("tileset", create_spritesheet(static_tiles, columns=3), "terrain"))

    # Auto-tile sets for grass and stone
    grass_autotiles = generate_autotile_set(grass, TERRAIN.shadow("dirt"), "grass_autotile")
    stone_autotiles = generate_autotile_set(stone, TERRAIN.shadow("stone"), "stone_autotile")
    results.extend(grass_autotiles)
    results.extend(stone_autotiles)

    return results
