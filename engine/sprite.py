"""
Sprite and animation dataclasses for managing frames, directions, and metadata.
"""

from dataclasses import dataclass, field
from PIL import Image
from engine.drawing import create_spritesheet, mirror_horizontal


@dataclass
class SpriteSheet:
    """A named sequence of animation frames."""
    name: str
    frames: list[Image.Image]
    frame_duration_ms: int = 120
    loop: bool = True
    # Per-frame durations for variable timing (overrides frame_duration_ms when set)
    frame_durations_ms: list[int] | None = None

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def frame_width(self) -> int:
        return self.frames[0].width if self.frames else 0

    @property
    def frame_height(self) -> int:
        return self.frames[0].height if self.frames else 0

    @property
    def total_duration_ms(self) -> int:
        """Total animation duration in milliseconds."""
        if self.frame_durations_ms:
            return sum(self.frame_durations_ms)
        return self.frame_count * self.frame_duration_ms

    @property
    def effective_fps(self) -> float:
        """Effective animation FPS based on total duration."""
        if self.total_duration_ms <= 0:
            return 0.0
        return self.frame_count / (self.total_duration_ms / 1000.0)

    def to_spritesheet(self, columns: int | None = None) -> Image.Image:
        return create_spritesheet(self.frames, columns)

    def hitbox(self) -> dict:
        """Auto-calculate hitbox from non-transparent pixel bounding box."""
        if not self.frames:
            return {"x": 0, "y": 0, "w": 0, "h": 0}
        frame = self.frames[0]
        bbox = frame.getbbox()
        if bbox is None:
            return {"x": 0, "y": 0, "w": frame.width, "h": frame.height}
        return {"x": bbox[0], "y": bbox[1], "w": bbox[2] - bbox[0], "h": bbox[3] - bbox[1]}

    def anchor(self) -> dict:
        """Bottom-center anchor point."""
        return {"x": self.frame_width // 2, "y": self.frame_height - 1}

    def to_metadata(self) -> dict:
        meta = {
            "name": self.name,
            "frame_width": self.frame_width,
            "frame_height": self.frame_height,
            "frame_count": self.frame_count,
            "frame_duration_ms": self.frame_duration_ms,
            "loop": self.loop,
            "hitbox": self.hitbox(),
            "anchor": self.anchor(),
            "total_duration_ms": self.total_duration_ms,
            "effective_fps": round(self.effective_fps, 1),
            "recommended_fps": {
                "mobile": min(12, max(8, round(self.effective_fps))),
                "desktop": min(15, max(8, round(self.effective_fps))),
            },
        }
        if self.frame_durations_ms:
            meta["frame_durations_ms"] = self.frame_durations_ms
        return meta


@dataclass
class DirectionalSprite:
    """Holds sprite sheets for 4 directions. Left auto-generated from right mirror."""
    name: str
    down: SpriteSheet | None = None
    up: SpriteSheet | None = None
    right: SpriteSheet | None = None
    _left: SpriteSheet | None = field(default=None, repr=False)

    @property
    def left(self) -> SpriteSheet | None:
        if self._left is not None:
            return self._left
        if self.right is not None:
            mirrored = [mirror_horizontal(f) for f in self.right.frames]
            return SpriteSheet(
                name=f"{self.right.name}_left",
                frames=mirrored,
                frame_duration_ms=self.right.frame_duration_ms,
                loop=self.right.loop,
            )
        return None

    def all_sheets(self) -> list[SpriteSheet]:
        sheets = []
        for direction in [self.down, self.up, self.right, self.left]:
            if direction is not None:
                sheets.append(direction)
        return sheets

    def to_metadata(self) -> dict:
        directions = []
        if self.down:
            directions.append("down")
        if self.up:
            directions.append("up")
        if self.right:
            directions.append("right")
        if self.left:
            directions.append("left")
        return {
            "name": self.name,
            "directions": directions,
            "sheets": {s.name: s.to_metadata() for s in self.all_sheets()},
        }


@dataclass
class StaticSprite:
    """A single non-animated sprite with metadata."""
    name: str
    image: Image.Image
    category: str = ""

    def hitbox(self) -> dict:
        bbox = self.image.getbbox()
        if bbox is None:
            return {"x": 0, "y": 0, "w": self.image.width, "h": self.image.height}
        return {"x": bbox[0], "y": bbox[1], "w": bbox[2] - bbox[0], "h": bbox[3] - bbox[1]}

    def to_metadata(self) -> dict:
        return {
            "name": self.name,
            "width": self.image.width,
            "height": self.image.height,
            "hitbox": self.hitbox(),
            "category": self.category,
        }
