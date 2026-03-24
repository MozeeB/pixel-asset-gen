# Pixel Art Asset Generator - Guide

Production-ready pixel art game asset generator. Produces sprite sheets with animations, JSON metadata, texture atlases, and animated GIFs at multiple scales.

## Quick Start

```bash
# Generate everything
python generate_assets.py

# Generate with mobile quality profile
python generate_assets.py --profile mobile

# Generate with desktop quality profile
python generate_assets.py --profile desktop
```

## CLI Reference

### Filtering

| Flag | Description | Example |
|------|-------------|---------|
| `--only` | Comma-separated categories | `--only player,objects` |
| `--types` | Comma-separated asset names | `--types rock_idle,tree_sway` |
| `--exclude` | Comma-separated names to skip | `--exclude slime_blue,slime_red` |
| `--grep` | Fuzzy search on asset names | `--grep fire` |

### Output Control

| Flag | Description | Example |
|------|-------------|---------|
| `--output`, `-o` | Custom output directory | `--output ./my_assets` |
| `--scales` | Custom scale factors | `--scales 1,2,3,4,8` |
| `--profile` | Quality profile | `--profile mobile` |
| `--no-atlas` | Skip texture atlas | `--no-atlas` |
| `--no-metadata` | Skip JSON metadata | `--no-metadata` |
| `--gif` | Export animated GIFs | `--gif` |
| `--gif-scale N` | GIF scale factor (default: 4) | `--gif-scale 8` |

### Procedural Control

| Flag | Description | Example |
|------|-------------|---------|
| `--seed N` | Global seed offset for variation | `--seed 999` |
| `--hue-shift N` | Recolor all sprites by N degrees | `--hue-shift 120` |

### Inspection

| Flag | Description | Example |
|------|-------------|---------|
| `--list` | List all assets with details | `--list` |
| `--count` | Asset count summary per category | `--count` |
| `--info NAME` | Detailed info for one asset | `--info rock_idle` |
| `--dry-run` | Show what would be generated | `--dry-run` |
| `--validate-only` | Validate sizes only | `--validate-only` |

### Maintenance

| Flag | Description | Example |
|------|-------------|---------|
| `--clean` | Delete output dir before generating | `--clean` |
| `--verbose`, `-v` | Show all scale variants in output | `-v` |

## Usage Examples

### Filtering

```bash
# Generate only player and objects
python generate_assets.py --only player,objects

# Generate specific assets by name
python generate_assets.py --only objects --types rock_idle,tree_sway,water_waves

# Generate all enemies except blue and red slimes
python generate_assets.py --only enemies --exclude slime_blue,slime_red

# Find all fire-related assets across all categories
python generate_assets.py --grep fire --list

# Find all water assets and generate them
python generate_assets.py --grep water

# Combine: objects matching "leaf" only
python generate_assets.py --only objects --grep leaf
```

### Output Control

```bash
# Generate to custom directory
python generate_assets.py --output ./build/sprites

# Custom scale factors (e.g. for retina + ultra-HD)
python generate_assets.py --scales 1,2,4,8

# Generate only 2x and 4x (skip 1x)
python generate_assets.py --scales 2,4

# Mobile profile with specific scales override
python generate_assets.py --profile mobile --scales 2,3,4,6

# Skip atlas for faster iteration
python generate_assets.py --only objects --no-atlas

# Skip metadata JSONs (PNGs only)
python generate_assets.py --no-metadata

# Export animated GIFs alongside PNGs
python generate_assets.py --only effects --gif

# GIFs at 8x scale for preview/documentation
python generate_assets.py --only objects --gif --gif-scale 8

# GIFs only for specific assets
python generate_assets.py --only objects --types tree_sway,water_waves --gif --gif-scale 4
```

### Procedural Control

```bash
# Different seed for variation (all procedural assets change)
python generate_assets.py --seed 999

# Another variation
python generate_assets.py --seed 42 --only terrain,objects

# Recolor everything +120 degrees (green becomes blue-ish)
python generate_assets.py --hue-shift 120

# Recolor enemies only (e.g. make purple enemies)
python generate_assets.py --only enemies --hue-shift 270

# Create a "winter" palette shift
python generate_assets.py --hue-shift -30 --only objects,terrain

# Create red-tinted "hell" variant
python generate_assets.py --hue-shift 180 --output ./assets_hell

# Combine seed + hue for unique variant sets
python generate_assets.py --seed 777 --hue-shift 60 --output ./assets_variant_1
python generate_assets.py --seed 888 --hue-shift 180 --output ./assets_variant_2
```

### Inspection

```bash
# List everything with frame counts, FPS, dimensions
python generate_assets.py --list

# Search and list matching assets
python generate_assets.py --grep water --list

# Count all assets by category
python generate_assets.py --count

# Get detailed info about a specific asset
python generate_assets.py --info rock_idle
python generate_assets.py --info player_idle
python generate_assets.py --info explosion

# Dry run: see what would be generated without writing
python generate_assets.py --dry-run
python generate_assets.py --only objects --grep leaf --dry-run

# Validate against mobile profile
python generate_assets.py --profile mobile --validate-only
```

### Maintenance

```bash
# Clean and regenerate everything
python generate_assets.py --clean

# Clean and regenerate specific category
python generate_assets.py --clean --only objects

# Verbose output showing all scale variants
python generate_assets.py --only objects -v

# Clean, generate for mobile, with GIFs, verbose
python generate_assets.py --clean --profile mobile --gif -v
```

### Real-World Workflows

```bash
# Quick prototype: just player + terrain for level design
python generate_assets.py --only player,terrain --profile mobile --no-atlas

# Pre-production: test all animations as GIFs for review
python generate_assets.py --gif --gif-scale 4 --no-atlas

# Build multiple themed tilesets for different biomes
python generate_assets.py --hue-shift 0 --only terrain,objects --output ./biome_forest
python generate_assets.py --hue-shift 30 --only terrain,objects --output ./biome_desert
python generate_assets.py --hue-shift 200 --only terrain,objects --output ./biome_ice
python generate_assets.py --hue-shift 330 --only terrain,objects --output ./biome_volcanic

# Generate enemy color variants for difficulty levels
python generate_assets.py --only enemies --hue-shift 0 --output ./enemies_normal
python generate_assets.py --only enemies --hue-shift 120 --output ./enemies_elite
python generate_assets.py --only enemies --hue-shift 240 --output ./enemies_boss

# CI/CD: validate all assets pass mobile quality
python generate_assets.py --profile mobile --validate-only

# Production build: clean, mobile profile, all assets
python generate_assets.py --clean --profile mobile

# Development: iterate on one asset quickly
python generate_assets.py --only objects --types tree_sway --gif --gif-scale 8 --no-atlas
```

## Available Categories

| Category | Key | Assets | Description |
|----------|-----|--------|-------------|
| Player | `player` | 7 x 4 dirs | idle, walk, run, attack, jump, hit, death |
| Enemies | `enemies` | 21 | 5 types x idle/hit/death (slime x3, skeleton, bat, ghost, goblin) |
| NPCs | `npcs` | 4 | villager, merchant with animations |
| Terrain | `terrain` | 42 | 9 tile types + 32 autotile edge variants |
| Items | `items` | 13 | weapons, potions, gems, misc (static) |
| UI | `ui` | 13 | hearts, bars, buttons, inventory (static) |
| Effects | `effects` | 24 | explosions, magic, particles, combos |
| Objects | `objects` | 12 | rock, sky, leaf, tree, water, grass animations |

**Total: 136 assets (70 animated, 66 static)**

## Quality Profiles

| Setting | Mobile | Desktop |
|---------|--------|---------|
| Scales | 2x, 3x, 4x | 1x, 2x, 4x |
| Target DPI | 326 | 96 |
| Max atlas | 2048x2048 | 4096x4096 |
| Min sprite | 16px | 16px |
| POT atlas | Yes | Yes |

## Output Structure

```
assets/
  characters/
    player/          # 7 directional animations (4 dirs each)
    enemies/         # 5 enemy types x 3 states
    npcs/            # 2 NPCs with animations
  terrain/
    autotile/        # 32 auto-tile variants
  items/
    weapons/         # sword, shield, bow, axe
    potions/         # health, mana, stamina
    gems/            # ruby, sapphire, emerald
    misc/            # coin, key, chest
  ui/                # hearts, bars, buttons, inventory
  effects/           # 24 visual effects
  objects/           # 12 natural object animations
  atlas/             # texture atlas + mappings
```

Each sprite generates:
- `name.png` — base scale spritesheet
- `name_2x.png`, `name_4x.png` — scaled variants
- `name.json` — metadata (frames, timing, hitbox, anchor, fps)
- `name_4x.gif` — animated preview (with `--gif`)

## JSON Metadata Format

```json
{
  "name": "rock_idle",
  "frame_width": 16,
  "frame_height": 16,
  "frame_count": 8,
  "frame_duration_ms": 200,
  "loop": true,
  "hitbox": { "x": 2, "y": 4, "w": 12, "h": 8 },
  "anchor": { "x": 8, "y": 15 },
  "total_duration_ms": 1600,
  "effective_fps": 5.0,
  "recommended_fps": { "mobile": 8, "desktop": 8 }
}
```

## Architecture

```
engine/
  drawing.py    # Pixel primitives, outlines, shading, composition
  sprite.py     # SpriteSheet, DirectionalSprite, StaticSprite
  palette.py    # Color system with 3-tier shading (highlight/base/shadow)
  noise.py      # Value noise + fractal noise for procedural generation
  metadata.py   # JSON export
  atlas.py      # Texture atlas packing
  quality.py    # Quality profiles and validation
  scaling.py    # Nearest-neighbor scaling

sprites/
  player.py     # Player animations (7 states x 4 directions)
  enemies.py    # 5 enemy types with variants
  npcs.py       # Villager, merchant
  terrain.py    # 9 tiles + 32 autotiles
  items.py      # Weapons, potions, gems, misc
  ui.py         # Health bars, buttons, inventory
  effects.py    # 24 visual effects
  objects.py    # 12 natural object animations
```

### Adding New Assets

1. Create a generator function in the appropriate `sprites/*.py` module
2. Return a `SpriteSheet` (animated) or `StaticSprite` (static)
3. Add it to that module's `generate_all()` function
4. The main pipeline auto-discovers via `generate_all()`

```python
from engine.drawing import new_sprite, put_pixel, draw_outline
from engine.palette import OBJECTS
from engine.sprite import SpriteSheet

def generate_my_animation() -> SpriteSheet:
    frames = []
    for f in range(8):
        img = new_sprite()  # 16x16 transparent
        put_pixel(img, 7, 7, OBJECTS.base("rock_gray"))
        draw_outline(img)
        frames.append(img)
    return SpriteSheet("my_animation", frames, frame_duration_ms=100, loop=True)
```

### Palette System

Colors use 3-tier shading generated from a base color:

```python
from engine.palette import _build_palette

MY_PALETTE = _build_palette("my_palette", {
    "primary": (100, 150, 200),   # RGB base color
    "accent": (200, 100, 50),
})

MY_PALETTE.highlight("primary")  # Lighter version
MY_PALETTE.base("primary")       # Original color
MY_PALETTE.shadow("primary")     # Darker version
```

### Noise System

Procedural noise for organic textures:

```python
from engine.noise import noise_map, fractal_noise

# 2D noise map normalized to [0, 1]
nmap = noise_map(16, 16, seed=42, octaves=3, base_scale=0.3)
value = nmap[y][x]  # 0.0 to 1.0

# Single point query (returns [-1, 1])
v = fractal_noise(x, y, seed=42, octaves=3, persistence=0.5, base_scale=0.2)
```
