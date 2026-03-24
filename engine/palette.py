"""
Color palette system with 3-tier shading and hue recoloring.
Kingdom Rush style: muted warm colors, no pure blacks, grey undertones.
Every color has highlight / base / shadow variants generated from HSL.
"""

import colorsys
from dataclasses import dataclass, field


RGB = tuple[int, int, int]
RGBA = tuple[int, int, int, int]
TRANSPARENT = (0, 0, 0, 0)

# Kingdom Rush style outline — warm dark brown, NEVER pure black
KR_OUTLINE = (50, 35, 25)
KR_OUTLINE_LIGHT = (80, 60, 45)


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return h, s, l


def hsl_to_rgb(h: float, s: float, l: float) -> RGB:
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))


def mute_color(color: RGB, grey_factor: float = 0.15) -> RGB:
    """Shift a color toward grey (desaturate) by grey_factor. KR style muting."""
    r, g, b = color
    grey = int(0.299 * r + 0.587 * g + 0.114 * b)
    return (
        int(r + (grey - r) * grey_factor),
        int(g + (grey - g) * grey_factor),
        int(b + (grey - b) * grey_factor),
    )


def warm_shift(color: RGB, amount: float = 0.05) -> RGB:
    """Shift color slightly warmer (toward orange/red)."""
    r, g, b = color
    return (
        min(255, int(r + 255 * amount)),
        g,
        max(0, int(b - 255 * amount * 0.5)),
    )


def shading_tiers(base: RGB, highlight_boost: float = 0.25,
                  shadow_drop: float = 0.30) -> tuple[RGB, RGB, RGB]:
    """Return (highlight, base, shadow) — KR style bold contrast."""
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
    def from_base(cls, base: RGB, highlight_boost: float = 0.25,
                  shadow_drop: float = 0.30) -> "ShadedColor":
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
# KINGDOM RUSH STYLE PALETTE DEFINITIONS
# Muted, warm, grey-shifted — no pure blacks
# ============================================================

PLAYER = _build_palette("player", {
    "skin": (210, 170, 135),
    "hair": (95, 65, 35),
    "shirt": (140, 80, 65),
    "pants": (65, 55, 50),
    "boots": (85, 55, 35),
    "outline": KR_OUTLINE,
    "eyes": (50, 35, 25),
    "belt": (165, 130, 55),
})

TERRAIN = _build_palette("terrain", {
    "grass": (95, 155, 65),
    "dirt": (155, 120, 75),
    "stone": (140, 135, 125),
    "water": (55, 115, 165),
    "sand": (215, 195, 145),
    "wood": (130, 85, 45),
    "leaves": (65, 125, 75),
    "snow": (225, 225, 235),
    "lava": (215, 85, 30),
    "lava_bright": (235, 150, 50),
})

WEAPONS = _build_palette("weapons", {
    # Metals — warm steel, no cold blue
    "iron": (145, 140, 135),
    "steel": (165, 165, 160),
    "gold_metal": (195, 170, 85),
    "dark_metal": (65, 55, 50),
    "crystal": (135, 170, 210),
    "bone": (200, 190, 165),
    # Handles — warm wood tones
    "wood": (130, 85, 45),
    "dark_wood": (90, 58, 32),
    "leather": (140, 95, 50),
    "grip_wrap": (110, 78, 42),
    # Enchantments — muted magic
    "fire": (235, 135, 40),
    "fire_bright": (245, 205, 85),
    "ice": (110, 175, 220),
    "ice_bright": (185, 215, 235),
    "lightning": (235, 225, 100),
    "lightning_bright": (245, 240, 185),
    "poison": (95, 185, 70),
    "shadow": (85, 50, 105),
    # Magic — muted
    "magic_blue": (70, 110, 210),
    "magic_purple": (145, 65, 200),
    "magic_white": (215, 215, 230),
    # Rarity — muted glows
    "common": (155, 150, 145),
    "uncommon": (70, 170, 65),
    "rare": (65, 100, 210),
    "epic": (145, 60, 210),
    "legendary": (225, 155, 45),
    # Bow/string
    "string": (190, 180, 160),
    "arrow_shaft": (150, 115, 60),
    "fletching": (180, 60, 55),
})

ITEMS = _build_palette("items", {
    "gold": (195, 170, 85),
    "gem_red": (175, 55, 50),
    "gem_blue": (65, 105, 180),
    "gem_green": (60, 165, 80),
    "potion_red": (175, 50, 45),
    "potion_blue": (55, 90, 175),
    "potion_green": (50, 155, 65),
    "metal": (165, 165, 175),
    "handle": (130, 85, 45),
})

UI = _build_palette("ui", {
    "heart": (185, 55, 45),
    "mana": (60, 105, 185),
    "stamina": (65, 155, 75),
    "bg_dark": (55, 45, 35),
    "bg_light": (75, 65, 55),
    "border": (165, 155, 145),
    "text": (225, 220, 210),
})

ENEMIES = _build_palette("enemies", {
    "slime": (110, 165, 75),
    "skeleton": (200, 190, 165),
    "bat": (105, 65, 130),
    "ghost": (200, 200, 215),
    "goblin": (105, 145, 65),
    "eyes_red": (190, 55, 45),
    "eyes_yellow": (215, 195, 55),
})

OBJECTS = _build_palette("objects", {
    "rock_gray": (150, 140, 130),
    "rock_brown": (130, 105, 80),
    "rock_moss": (90, 115, 65),
    "sky_day": (130, 180, 220),
    "sky_sunset": (225, 140, 85),
    "sky_night": (35, 35, 55),
    "cloud": (225, 225, 230),
    "star": (240, 235, 195),
    "leaf_green": (90, 150, 60),
    "leaf_autumn": (195, 130, 45),
    "leaf_red": (175, 60, 40),
    "trunk": (115, 80, 45),
    "bark": (90, 65, 40),
    "canopy": (75, 130, 65),
    "canopy_light": (100, 160, 70),
    "water_deep": (40, 85, 145),
    "water_mid": (60, 120, 180),
    "water_foam": (190, 215, 230),
    "grass_green": (95, 155, 60),
    "grass_dark": (70, 120, 45),
    "grass_tip": (130, 185, 75),
    "fire_core": (245, 235, 185),
    "fire_inner": (240, 190, 60),
    "fire_outer": (205, 85, 30),
    "ember": (235, 140, 40),
})

EFFECTS = _build_palette("effects", {
    "fire_hot": (245, 210, 65),
    "fire_mid": (235, 155, 40),
    "fire_cool": (205, 85, 30),
    "smoke": (130, 125, 120),
    "magic_blue": (85, 145, 220),
    "magic_purple": (145, 85, 215),
    "spark": (240, 235, 220),
    # Advanced — muted
    "ghost_blue": (105, 135, 215),
    "ghost_cyan": (120, 195, 225),
    "slash_white": (225, 225, 235),
    "slash_light": (190, 200, 225),
    "heal_green": (90, 210, 115),
    "heal_light": (155, 225, 185),
    "shield_gold": (230, 190, 65),
    "shield_white": (240, 230, 195),
    "charge_yellow": (240, 225, 85),
    "charge_orange": (235, 175, 50),
    "shock_cyan": (105, 215, 230),
    "shock_white": (210, 230, 235),
    "portal_purple": (135, 65, 195),
    "portal_pink": (200, 100, 225),
    "levelup_gold": (240, 210, 65),
    "levelup_white": (240, 240, 210),
    "flash_white": (245, 240, 235),
    "dust_tan": (175, 155, 125),
    "dust_light": (200, 185, 165),
    "hit_orange": (235, 175, 55),
    "hit_yellow": (240, 225, 100),
})

BUILDINGS = _build_palette("buildings", {
    # Walls — warm, textured
    "stone_wall": (170, 160, 145),
    "stone_dark": (120, 110, 100),
    "brick": (165, 100, 65),
    "brick_dark": (135, 75, 50),
    "wood_wall": (155, 110, 60),
    "wood_dark": (110, 75, 42),
    "plaster": (210, 200, 180),
    "plaster_crack": (180, 170, 155),
    # Roofs — muted
    "roof_red": (160, 60, 45),
    "roof_blue": (60, 80, 125),
    "roof_thatch": (185, 160, 85),
    "roof_slate": (100, 95, 90),
    # Doors & windows
    "door_wood": (125, 80, 40),
    "door_dark": (85, 55, 30),
    "window_glass": (130, 175, 205),
    "window_glow": (240, 220, 135),
    "window_frame": (95, 75, 55),
    # Details
    "chimney": (135, 125, 115),
    "chimney_smoke": (170, 165, 160),
    "lantern": (240, 200, 80),
    "sign_wood": (140, 100, 55),
    "flag": (185, 55, 45),
    "banner": (65, 55, 125),
    # Special
    "crystal_wall": (125, 160, 200),
    "crystal_glow": (170, 200, 235),
    "dark_stone": (60, 55, 50),
    "lava_glow": (230, 100, 35),
    "ice_wall": (170, 205, 225),
    "ice_shine": (210, 225, 240),
    "gold_trim": (205, 175, 50),
    "iron_bar": (110, 105, 100),
})
