"""
JSON metadata exporter for sprite assets.
Writes frame data, hitboxes, anchors, and animation info alongside PNGs.
"""

import json
import os

from engine.sprite import SpriteSheet, DirectionalSprite, StaticSprite


def export_metadata(sprite, output_path: str) -> str:
    """Export JSON metadata for any sprite type. Returns path to JSON file."""
    meta = sprite.to_metadata()
    json_path = os.path.splitext(output_path)[0] + ".json"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return json_path


def export_tileset_metadata(tiles: list[StaticSprite], output_path: str) -> str:
    """Export JSON metadata for a tileset with tile IDs and properties."""
    tile_data = {}
    for i, tile in enumerate(tiles):
        tile_data[tile.name] = {
            "id": i,
            "width": tile.image.width,
            "height": tile.image.height,
            "hitbox": tile.hitbox(),
            "category": tile.category,
            "solid": tile.name in ("stone", "tree", "wood_floor"),
            "walkable": tile.name in ("grass", "dirt", "sand", "snow"),
        }

    meta = {
        "type": "tileset",
        "tile_count": len(tiles),
        "tiles": tile_data,
    }

    json_path = os.path.splitext(output_path)[0] + ".json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return json_path
