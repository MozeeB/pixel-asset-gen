"""
Texture atlas packer using shelf-packing algorithm.
Packs all sprites into a single atlas image with a JSON coordinate map.
"""

import json
import os
from PIL import Image
from engine.palette import TRANSPARENT
from engine.scaling import scale_nearest


def pack_atlas(sprites: list[tuple[str, Image.Image]], max_width: int = 512,
               padding: int = 1) -> tuple[Image.Image, dict]:
    """Pack sprites into a texture atlas using shelf-packing.

    Args:
        sprites: List of (name, image) tuples.
        max_width: Maximum atlas width.
        padding: Pixels between sprites.

    Returns:
        (atlas_image, coordinate_map) where coordinate_map maps name to {x, y, w, h}.
    """
    if not sprites:
        return Image.new("RGBA", (1, 1), TRANSPARENT), {}

    # Sort by height descending for better packing
    sorted_sprites = sorted(sprites, key=lambda s: s[1].height, reverse=True)

    # Shelf packing
    shelves = []  # list of (y_start, height, items: list of (x, name, img))
    coord_map = {}

    for name, img in sorted_sprites:
        w, h = img.size
        placed = False

        for shelf in shelves:
            shelf_y, shelf_h, items = shelf
            # Check if sprite fits in this shelf
            if h <= shelf_h:
                # Calculate next x position
                next_x = sum(item[2].width + padding for item in items)
                if next_x + w <= max_width:
                    items.append((next_x, name, img))
                    coord_map[name] = {"x": next_x, "y": shelf_y, "w": w, "h": h}
                    placed = True
                    break

        if not placed:
            # Start new shelf
            shelf_y = sum(s[1] + padding for s in shelves)
            shelves.append((shelf_y, h, [(0, name, img)]))
            coord_map[name] = {"x": 0, "y": shelf_y, "w": w, "h": h}

    # Calculate atlas dimensions
    atlas_w = max(
        sum(item[2].width + padding for item in shelf[2]) - padding
        for shelf in shelves
    ) if shelves else 1
    atlas_h = sum(s[1] + padding for s in shelves) - padding if shelves else 1

    # Round up to power of 2 (common for GPU textures)
    def next_pow2(v):
        v -= 1
        v |= v >> 1
        v |= v >> 2
        v |= v >> 4
        v |= v >> 8
        v |= v >> 16
        return v + 1

    atlas_w = next_pow2(atlas_w)
    atlas_h = next_pow2(atlas_h)

    # Create atlas image
    atlas = Image.new("RGBA", (atlas_w, atlas_h), TRANSPARENT)
    for shelf_y, shelf_h, items in shelves:
        for x, name, img in items:
            atlas.paste(img, (x, shelf_y))

    return atlas, coord_map


def save_atlas(atlas: Image.Image, coord_map: dict, output_dir: str,
               name: str = "atlas", scales: list[int] | None = None) -> list[str]:
    """Save atlas image and JSON coordinate map. Optionally save scaled variants.

    Returns list of saved file paths.
    """
    saved = []
    scales = scales or [1]

    for scale in scales:
        suffix = f"_{scale}x" if scale > 1 else ""
        img_path = os.path.join(output_dir, f"{name}{suffix}.png")
        json_path = os.path.join(output_dir, f"{name}{suffix}.json")

        if scale > 1:
            scaled_img = scale_nearest(atlas, scale)
            scaled_map = {
                k: {"x": v["x"] * scale, "y": v["y"] * scale,
                    "w": v["w"] * scale, "h": v["h"] * scale}
                for k, v in coord_map.items()
            }
        else:
            scaled_img = atlas
            scaled_map = coord_map

        scaled_img.save(img_path)
        saved.append(img_path)

        meta = {
            "image": os.path.basename(img_path),
            "width": scaled_img.width,
            "height": scaled_img.height,
            "scale": scale,
            "sprite_count": len(scaled_map),
            "sprites": scaled_map,
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        saved.append(json_path)

    return saved
