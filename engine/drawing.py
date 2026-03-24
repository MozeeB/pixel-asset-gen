"""
Drawing primitives for pixel art: line, circle, fill, outline, shading, dithering.
Kingdom Rush style: thick warm outlines, texture patterns, cel-shaded volumes.
All operations work on Pillow RGBA images and never mutate — they return new images.
"""

from PIL import Image
from engine.palette import RGB, RGBA, TRANSPARENT, ShadedColor, KR_OUTLINE


def new_sprite(width: int = 16, height: int = 16) -> Image.Image:
    """Create a new transparent RGBA image."""
    return Image.new("RGBA", (width, height), TRANSPARENT)


def put_pixel(img: Image.Image, x: int, y: int, color: RGB | RGBA) -> None:
    """Draw a single pixel with bounds checking. Mutates img in place."""
    if 0 <= x < img.width and 0 <= y < img.height:
        if len(color) == 3:
            color = (*color, 255)
        img.putpixel((x, y), color)


def get_pixel(img: Image.Image, x: int, y: int) -> RGBA:
    """Get pixel color with bounds checking."""
    if 0 <= x < img.width and 0 <= y < img.height:
        return img.getpixel((x, y))
    return TRANSPARENT


def draw_pixels(img: Image.Image, pixel_map: dict[tuple[int, int], RGB | RGBA]) -> None:
    """Draw multiple pixels from a coordinate-color dict."""
    for (x, y), color in pixel_map.items():
        put_pixel(img, x, y, color)


def draw_line(img: Image.Image, x0: int, y0: int, x1: int, y1: int, color: RGB | RGBA) -> None:
    """Bresenham's line algorithm."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    while True:
        put_pixel(img, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def draw_circle(img: Image.Image, cx: int, cy: int, r: int,
                color: RGB | RGBA, filled: bool = False) -> None:
    """Midpoint circle algorithm, optionally filled."""
    x = r
    y = 0
    d = 1 - r

    while x >= y:
        if filled:
            for xi in range(cx - x, cx + x + 1):
                put_pixel(img, xi, cy + y, color)
                put_pixel(img, xi, cy - y, color)
            for xi in range(cx - y, cx + y + 1):
                put_pixel(img, xi, cy + x, color)
                put_pixel(img, xi, cy - x, color)
        else:
            for sx, sy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                put_pixel(img, cx + sx * x, cy + sy * y, color)
                put_pixel(img, cx + sx * y, cy + sy * x, color)

        y += 1
        if d <= 0:
            d += 2 * y + 1
        else:
            x -= 1
            d += 2 * (y - x) + 1


def draw_rect(img: Image.Image, x: int, y: int, w: int, h: int,
              color: RGB | RGBA, filled: bool = True) -> None:
    """Draw a rectangle, optionally filled."""
    if filled:
        for py in range(y, y + h):
            for px in range(x, x + w):
                put_pixel(img, px, py, color)
    else:
        draw_line(img, x, y, x + w - 1, y, color)
        draw_line(img, x, y + h - 1, x + w - 1, y + h - 1, color)
        draw_line(img, x, y, x, y + h - 1, color)
        draw_line(img, x + w - 1, y, x + w - 1, y + h - 1, color)


def draw_ellipse_filled(img: Image.Image, cx: int, cy: int, rx: int, ry: int,
                        color: RGB | RGBA) -> None:
    """Draw a filled ellipse."""
    for y in range(-ry, ry + 1):
        for x in range(-rx, rx + 1):
            if rx > 0 and ry > 0:
                if (x * x * ry * ry + y * y * rx * rx) <= (rx * rx * ry * ry):
                    put_pixel(img, cx + x, cy + y, color)


def flood_fill(img: Image.Image, x: int, y: int, color: RGB | RGBA) -> None:
    """Simple flood fill from (x, y)."""
    if not (0 <= x < img.width and 0 <= y < img.height):
        return
    target = img.getpixel((x, y))
    if len(color) == 3:
        color = (*color, 255)
    if target == color:
        return
    stack = [(x, y)]
    visited = set()
    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in visited:
            continue
        if not (0 <= cx < img.width and 0 <= cy < img.height):
            continue
        if img.getpixel((cx, cy)) != target:
            continue
        visited.add((cx, cy))
        img.putpixel((cx, cy), color)
        stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])


def draw_outline(img: Image.Image, outline_color: RGB = KR_OUTLINE) -> Image.Image:
    """Return a new image with a 1px outline around all non-transparent pixels.
    Default: Kingdom Rush warm dark brown outline."""
    result = img.copy()
    oc = (*outline_color, 255) if len(outline_color) == 3 else outline_color
    w, h = img.size
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for y in range(h):
        for x in range(w):
            px = img.getpixel((x, y))
            if px[3] > 0:
                continue
            for dx, dy in offsets:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    neighbor = img.getpixel((nx, ny))
                    if neighbor[3] > 0:
                        result.putpixel((x, y), oc)
                        break
    return result


def draw_outline_thick(img: Image.Image, outline_color: RGB = KR_OUTLINE,
                       thickness: int = 2) -> Image.Image:
    """Return a new image with a thick outline (KR style 2px default).
    Checks pixels within `thickness` radius of non-transparent pixels."""
    result = img.copy()
    oc = (*outline_color, 255) if len(outline_color) == 3 else outline_color
    w, h = img.size

    # Build set of non-transparent pixel coords
    filled = set()
    for y in range(h):
        for x in range(w):
            if img.getpixel((x, y))[3] > 0:
                filled.add((x, y))

    # For each transparent pixel, check if any filled pixel is within range
    for y in range(h):
        for x in range(w):
            if (x, y) in filled:
                continue
            found = False
            for dy in range(-thickness, thickness + 1):
                for dx in range(-thickness, thickness + 1):
                    if dx == 0 and dy == 0:
                        continue
                    if abs(dx) + abs(dy) > thickness:
                        continue  # Manhattan distance check
                    if (x + dx, y + dy) in filled:
                        found = True
                        break
                if found:
                    break
            if found:
                result.putpixel((x, y), oc)
    return result


# ============================================================
# TEXTURE PATTERN HELPERS (Kingdom Rush style)
# ============================================================

def draw_brick_pattern(img: Image.Image, x: int, y: int, w: int, h: int,
                       brick_color: RGB, mortar_color: RGB,
                       brick_h: int = 3, brick_w: int = 5) -> None:
    """Fill area with brick pattern — mortar lines every brick_h/brick_w pixels."""
    for py in range(y, y + h):
        for px in range(x, x + w):
            row = (py - y) // brick_h
            # Offset every other row
            offset = (brick_w // 2) * (row % 2)
            col_pos = ((px - x) + offset) % brick_w
            row_pos = (py - y) % brick_h
            # Mortar on edges
            if row_pos == brick_h - 1 or col_pos == brick_w - 1:
                put_pixel(img, px, py, mortar_color)
            else:
                put_pixel(img, px, py, brick_color)


def draw_plank_pattern(img: Image.Image, x: int, y: int, w: int, h: int,
                       plank_color: RGB, gap_color: RGB,
                       plank_w: int = 4, vertical: bool = True) -> None:
    """Fill with wood plank pattern — 1px gaps between planks."""
    for py in range(y, y + h):
        for px in range(x, x + w):
            if vertical:
                is_gap = ((px - x) % plank_w) == plank_w - 1
            else:
                is_gap = ((py - y) % plank_w) == plank_w - 1
            put_pixel(img, px, py, gap_color if is_gap else plank_color)


def draw_stone_texture(img: Image.Image, x: int, y: int, w: int, h: int,
                       base_color: RGB, crack_color: RGB, seed: int = 42) -> None:
    """Noise-based stone with crack lines for KR style."""
    import math
    for py in range(y, y + h):
        for px in range(x, x + w):
            # Simple deterministic noise
            n = math.sin(px * 12.9898 + py * 78.233 + seed) * 43758.5453
            n = n - int(n)
            if abs(n) < 0.12:
                put_pixel(img, px, py, crack_color)
            else:
                put_pixel(img, px, py, base_color)


def draw_grass_spikes(img: Image.Image, base_y: int,
                      colors: list[RGB], seed: int = 0) -> None:
    """Kingdom Rush style grass: pointed triangular blades rising from base_y."""
    import math
    w = img.width
    for i in range(0, w, 2):
        # Vary height per blade
        n = math.sin(i * 7.13 + seed * 3.7) * 0.5 + 0.5
        blade_h = int(3 + n * 4)
        color_idx = int(n * len(colors)) % len(colors)
        color = colors[color_idx]
        # Draw triangular blade
        tip_x = i + (1 if n > 0.5 else 0)
        for h in range(blade_h):
            y = base_y - h
            half_w = max(0, (blade_h - h) // 2)
            for dx in range(-half_w, half_w + 1):
                put_pixel(img, tip_x + dx, y, color)


def draw_thatch_pattern(img: Image.Image, x: int, y: int, w: int, h: int,
                        color1: RGB, color2: RGB) -> None:
    """Cross-hatch thatch roof pattern."""
    for py in range(y, y + h):
        for px in range(x, x + w):
            if ((px - x) + (py - y)) % 3 == 0:
                put_pixel(img, px, py, color2)
            else:
                put_pixel(img, px, py, color1)


# ============================================================
# SHADING & COMPOSITION
# ============================================================

def apply_shading(img: Image.Image, base_color: RGB, shaded: ShadedColor,
                  light_dir: str = "top_left") -> Image.Image:
    """Replace all pixels matching base_color with shaded tiers based on position.
    KR style: bold 3-tier cel shading, hard transitions."""
    result = img.copy()
    w, h = img.size

    # Find bounding box of matching pixels
    min_x, min_y, max_x, max_y = w, h, 0, 0
    matching = []
    for y in range(h):
        for x in range(w):
            px = result.getpixel((x, y))
            if px[:3] == base_color and px[3] > 0:
                matching.append((x, y))
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if not matching:
        return result

    range_x = max(max_x - min_x, 1)
    range_y = max(max_y - min_y, 1)

    for x, y in matching:
        nx = (x - min_x) / range_x
        ny = (y - min_y) / range_y

        if light_dir == "top_left":
            t = (nx + ny) / 2.0
        elif light_dir == "top":
            t = ny
        else:
            t = (nx + ny) / 2.0

        if t < 0.33:
            result.putpixel((x, y), (*shaded.highlight, 255))
        elif t < 0.66:
            result.putpixel((x, y), (*shaded.base, 255))
        else:
            result.putpixel((x, y), (*shaded.shadow, 255))

    return result


def apply_shading_auto(img: Image.Image, palette_colors: dict[RGB, ShadedColor],
                       light_dir: str = "top_left") -> Image.Image:
    """Apply shading for multiple colors at once."""
    result = img.copy()
    for base_color, shaded in palette_colors.items():
        result = apply_shading(result, base_color, shaded, light_dir)
    return result


def dither_fill(img: Image.Image, x: int, y: int, w: int, h: int,
                color1: RGB | RGBA, color2: RGB | RGBA, pattern: str = "checker") -> None:
    """Fill area with dithered pattern using two colors."""
    for py in range(y, y + h):
        for px in range(x, x + w):
            if pattern == "checker":
                use_first = (px + py) % 2 == 0
            elif pattern == "horizontal":
                use_first = py % 2 == 0
            elif pattern == "vertical":
                use_first = px % 2 == 0
            else:
                use_first = (px + py) % 2 == 0
            put_pixel(img, px, py, color1 if use_first else color2)


def mirror_horizontal(img: Image.Image) -> Image.Image:
    """Return a horizontally flipped copy."""
    return img.transpose(Image.FLIP_LEFT_RIGHT)


def create_spritesheet(frames: list[Image.Image], columns: int | None = None) -> Image.Image:
    """Combine frames into a single spritesheet image."""
    if not frames:
        return new_sprite()
    w, h = frames[0].size
    cols = columns or len(frames)
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGBA", (w * cols, h * rows), TRANSPARENT)
    for i, frame in enumerate(frames):
        col = i % cols
        row = i // cols
        sheet.paste(frame, (col * w, row * h))
    return sheet


def composite_layers(*layers: Image.Image) -> Image.Image:
    """Composite multiple same-size layers from bottom to top."""
    if not layers:
        return new_sprite()
    result = layers[0].copy()
    for layer in layers[1:]:
        result = Image.alpha_composite(result, layer)
    return result
