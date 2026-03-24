"""
Color palette system with 3-tier shading and hue recoloring.
Every color has highlight / base / shadow variants generated from HSL.
"""

import colorsys
from dataclasses import dataclass, field


RGB = tuple[int, int, int]
RGBA = tuple[int, int, int, int]
TRANSPARENT = (0, 0, 0, 0)


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return h, s, l


def hsl_to_rgb(h: float, s: float, l: float) -> RGB:
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))


def shading_tiers(base: RGB, highlight_boost: float = 0.20, shadow_drop: float = 0.25) -> tuple[RGB, RGB, RGB]:
    """Return (highlight, base, shadow) from a base color by adjusting lightness."""
    h, s, l = rgb_to_hsl(*base)
    highlight = hsl_to_rgb(h, s, _clamp(l + highlight_boost))
    shadow = hsl_to_rgb(h, s, _clamp(l - shadow_drop))
    return highlight, base, shadow


def recolor(color: RGB, hue_shift: float) -> RGB:
    """Shift the hue of a color by `hue_shift` degrees (0-360)."""
    h, s, l = rgb_to_hsl(*color)
    new_h = (h + hue_shift / 360.0) % 1.0
    return hsl_to_rgb(new_h, s, l)


def recolor_palette(palette: dict[str, RGB], hue_shift: float) -> dict[str, RGB]:
    """Shift hue of every color in a palette dict."""
    return {k: recolor(v, hue_shift) for k, v in palette.items()}


@dataclass(frozen=True)
class ShadedColor:
    """A color with pre-computed highlight/base/shadow tiers."""
    highlight: RGB
    base: RGB
    shadow: RGB

    @classmethod
    def from_base(cls, base: RGB, highlight_boost: float = 0.20, shadow_drop: float = 0.25) -> "ShadedColor":
        h, s, l = rgb_to_hsl(*base)
        return cls(
            highlight=hsl_to_rgb(h, s, _clamp(l + highlight_boost)),
            base=base,
            shadow=hsl_to_rgb(h, s, _clamp(l - shadow_drop)),
        )


@dataclass(frozen=True)
class PaletteSet:
    """Named palette with shaded tiers for each color."""
    name: str
    colors: dict[str, ShadedColor] = field(default_factory=dict)

    def base(self, key: str) -> RGB:
        return self.colors[key].base

    def highlight(self, key: str) -> RGB:
        return self.colors[key].highlight

    def shadow(self, key: str) -> RGB:
        return self.colors[key].shadow

    def recolored(self, hue_shift: float) -> "PaletteSet":
        new_colors = {}
        for k, sc in self.colors.items():
            new_colors[k] = ShadedColor(
                highlight=recolor(sc.highlight, hue_shift),
                base=recolor(sc.base, hue_shift),
                shadow=recolor(sc.shadow, hue_shift),
            )
        return PaletteSet(name=f"{self.name}_hue{int(hue_shift)}", colors=new_colors)


def _build_palette(name: str, raw: dict[str, RGB]) -> PaletteSet:
    colors = {k: ShadedColor.from_base(v) for k, v in raw.items()}
    return PaletteSet(name=name, colors=colors)


# ============================================================
# PALETTE DEFINITIONS
# ============================================================

PLAYER = _build_palette("player", {
    "skin": (255, 206, 158),
    "hair": (101, 67, 33),
    "shirt": (52, 152, 219),
    "pants": (44, 62, 80),
    "boots": (90, 50, 30),
    "outline": (30, 30, 30),
    "eyes": (30, 30, 30),
    "belt": (170, 130, 50),
})

TERRAIN = _build_palette("terrain", {
    "grass": (106, 190, 48),
    "dirt": (143, 107, 65),
    "stone": (140, 140, 140),
    "water": (52, 152, 219),
    "sand": (236, 217, 159),
    "wood": (139, 90, 43),
    "leaves": (46, 139, 87),
    "snow": (240, 240, 255),
    "lava": (255, 80, 20),
    "lava_bright": (255, 160, 40),
})

WEAPONS = _build_palette("weapons", {
    # Metals
    "iron": (140, 140, 155),
    "steel": (180, 180, 200),
    "gold_metal": (210, 170, 40),
    "dark_metal": (60, 50, 70),
    "crystal": (150, 190, 240),
    "bone": (210, 200, 170),
    # Handles
    "wood": (120, 80, 40),
    "dark_wood": (85, 55, 30),
    "leather": (140, 95, 50),
    "grip_wrap": (100, 70, 35),
    # Enchantments
    "fire": (255, 140, 30),
    "fire_bright": (255, 220, 80),
    "ice": (120, 200, 255),
    "ice_bright": (200, 235, 255),
    "lightning": (255, 255, 100),
    "lightning_bright": (255, 255, 200),
    "poison": (80, 220, 60),
    "shadow": (80, 40, 120),
    # Magic
    "magic_blue": (60, 120, 255),
    "magic_purple": (160, 60, 240),
    "magic_white": (230, 230, 255),
    # Rarity glows
    "common": (160, 160, 160),
    "uncommon": (50, 200, 50),
    "rare": (50, 100, 255),
    "epic": (160, 50, 255),
    "legendary": (255, 160, 30),
    # Bow/string
    "string": (200, 190, 170),
    "arrow_shaft": (160, 120, 60),
    "fletching": (200, 50, 50),
})

ITEMS = _build_palette("items", {
    "gold": (255, 215, 0),
    "gem_red": (220, 40, 40),
    "gem_blue": (40, 100, 220),
    "gem_green": (40, 200, 80),
    "potion_red": (200, 30, 30),
    "potion_blue": (30, 80, 200),
    "potion_green": (30, 180, 60),
    "metal": (180, 180, 200),
    "handle": (139, 90, 43),
})

UI = _build_palette("ui", {
    "heart": (220, 40, 60),
    "mana": (50, 120, 220),
    "stamina": (50, 180, 80),
    "bg_dark": (30, 30, 40),
    "bg_light": (60, 60, 80),
    "border": (180, 180, 200),
    "text": (240, 240, 240),
})

ENEMIES = _build_palette("enemies", {
    "slime": (80, 200, 80),
    "skeleton": (220, 210, 190),
    "bat": (120, 60, 160),
    "ghost": (220, 220, 240),
    "goblin": (100, 160, 60),
    "eyes_red": (220, 40, 40),
    "eyes_yellow": (240, 220, 40),
})

OBJECTS = _build_palette("objects", {
    "rock_gray": (140, 135, 130),
    "rock_brown": (120, 100, 75),
    "rock_moss": (80, 120, 60),
    "sky_day": (135, 200, 255),
    "sky_sunset": (255, 140, 80),
    "sky_night": (25, 25, 60),
    "cloud": (240, 240, 250),
    "star": (255, 255, 200),
    "leaf_green": (80, 170, 50),
    "leaf_autumn": (210, 130, 30),
    "leaf_red": (190, 50, 30),
    "trunk": (110, 75, 40),
    "bark": (85, 60, 35),
    "canopy": (55, 145, 75),
    "canopy_light": (90, 180, 60),
    "water_deep": (30, 90, 170),
    "water_mid": (50, 130, 210),
    "water_foam": (200, 230, 255),
    "grass_green": (90, 180, 50),
    "grass_dark": (60, 130, 35),
    "grass_tip": (130, 210, 70),
    "fire_core": (255, 255, 200),
    "fire_inner": (255, 200, 50),
    "fire_outer": (220, 80, 20),
    "ember": (255, 140, 30),
})

EFFECTS = _build_palette("effects", {
    "fire_hot": (255, 220, 50),
    "fire_mid": (255, 160, 30),
    "fire_cool": (220, 80, 20),
    "smoke": (120, 120, 130),
    "magic_blue": (80, 160, 255),
    "magic_purple": (160, 80, 255),
    "spark": (255, 255, 240),
    # Advanced effect colors
    "ghost_blue": (100, 140, 255),
    "ghost_cyan": (120, 220, 255),
    "slash_white": (240, 245, 255),
    "slash_light": (200, 220, 255),
    "heal_green": (80, 240, 120),
    "heal_light": (160, 255, 200),
    "shield_gold": (255, 200, 60),
    "shield_white": (255, 240, 200),
    "charge_yellow": (255, 240, 80),
    "charge_orange": (255, 180, 40),
    "shock_cyan": (100, 240, 255),
    "shock_white": (220, 250, 255),
    "portal_purple": (140, 60, 220),
    "portal_pink": (220, 100, 255),
    "levelup_gold": (255, 220, 60),
    "levelup_white": (255, 255, 220),
    "flash_white": (255, 255, 255),
    "dust_tan": (180, 160, 130),
    "dust_light": (210, 195, 170),
    "hit_orange": (255, 180, 50),
    "hit_yellow": (255, 240, 100),
})
