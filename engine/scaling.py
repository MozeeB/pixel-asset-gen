"""
Nearest-neighbor scaling for pixel art (preserves crisp pixels).
"""

from PIL import Image


def scale_nearest(img: Image.Image, factor: int) -> Image.Image:
    """Scale image by integer factor using nearest-neighbor interpolation."""
    w, h = img.size
    return img.resize((w * factor, h * factor), Image.NEAREST)
