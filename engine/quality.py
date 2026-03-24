"""
Quality profiles for different target platforms.

Defines minimum quality settings for mobile games and desktop games,
including scale factors, atlas limits, and validation rules.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class QualityProfile:
    """Defines minimum quality requirements for a target platform."""
    name: str
    description: str
    # Scale factors to generate (e.g., [1, 2, 4])
    scale_factors: tuple[int, ...]
    # Minimum scale factor — sprites below this won't be exported
    min_scale: int
    # Maximum texture atlas dimension (width or height)
    max_atlas_size: int
    # Minimum sprite size in pixels (at base 1x) for characters
    min_sprite_size: int
    # Minimum sprite size for UI elements
    min_ui_size: int
    # Minimum rendered size (width or height at min_scale) before warning
    min_rendered_size: int
    # Whether to enforce power-of-2 atlas dimensions
    pot_atlas: bool
    # Maximum total atlas file size hint in KB (0 = no limit)
    max_atlas_kb: int
    # Recommended DPI for the target display
    target_dpi: int


MOBILE = QualityProfile(
    name="mobile",
    description="Mobile games (iOS/Android) — touch-friendly, GPU-safe atlas sizes",
    scale_factors=(2, 3, 4),
    min_scale=2,
    max_atlas_size=2048,
    min_sprite_size=16,
    min_ui_size=16,
    min_rendered_size=32,
    pot_atlas=True,
    max_atlas_kb=4096,
    target_dpi=326,
)

DESKTOP = QualityProfile(
    name="desktop",
    description="Desktop games (PC/Mac/Linux) — crisp pixel art at native resolution",
    scale_factors=(1, 2, 4),
    min_scale=1,
    max_atlas_size=4096,
    min_sprite_size=16,
    min_ui_size=16,
    min_rendered_size=16,
    pot_atlas=True,
    max_atlas_kb=0,
    target_dpi=96,
)

# All profiles available by name
PROFILES: dict[str, QualityProfile] = {
    "mobile": MOBILE,
    "desktop": DESKTOP,
}


def get_profile(name: str) -> QualityProfile:
    """Get a quality profile by name. Raises ValueError if not found."""
    profile = PROFILES.get(name.lower())
    if profile is None:
        valid = ", ".join(PROFILES.keys())
        raise ValueError(f"Unknown profile '{name}'. Valid profiles: {valid}")
    return profile


def validate_sprite_size(width: int, height: int, profile: QualityProfile,
                         sprite_type: str = "sprite") -> list[str]:
    """Check if a sprite meets the minimum quality for the given profile.

    Returns a list of warning messages (empty if all good).
    """
    warnings = []
    min_size = profile.min_ui_size if sprite_type == "ui" else profile.min_sprite_size

    if width < min_size or height < min_size:
        warnings.append(
            f"[{profile.name}] {sprite_type} {width}x{height} is below "
            f"minimum {min_size}x{min_size}"
        )

    # At the minimum scale, check if the rendered size is usable
    rendered_w = width * profile.min_scale
    rendered_h = height * profile.min_scale

    if rendered_w < profile.min_rendered_size or rendered_h < profile.min_rendered_size:
        warnings.append(
            f"[{profile.name}] {sprite_type} renders at {rendered_w}x{rendered_h} "
            f"(at {profile.min_scale}x) — minimum {profile.min_rendered_size}px for {profile.name}"
        )

    return warnings


def validate_atlas_size(width: int, height: int, profile: QualityProfile) -> list[str]:
    """Check if atlas dimensions are within profile limits."""
    warnings = []

    if width > profile.max_atlas_size or height > profile.max_atlas_size:
        warnings.append(
            f"[{profile.name}] Atlas {width}x{height} exceeds max "
            f"{profile.max_atlas_size}x{profile.max_atlas_size}"
        )

    if profile.pot_atlas:
        if (width & (width - 1)) != 0 or (height & (height - 1)) != 0:
            warnings.append(
                f"[{profile.name}] Atlas {width}x{height} is not power-of-2"
            )

    return warnings
