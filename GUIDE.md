# Pixel Art Asset Generator - Guide

Production-ready pixel art game asset generator in **Kingdom Rush cel-shaded style**. Produces sprite sheets with animations, JSON metadata, texture atlases, and animated GIFs at multiple scales.

## Art Style

All assets use a Kingdom Rush-inspired cel-shaded look:

- **Thick outlines**: 2px warm dark brown `(50, 35, 25)` via `draw_outline_thick()`
- **Muted colors**: Grey-shifted with warm undertones, no pure black anywhere
- **Bold shading**: Highlight +25% / Shadow -30% (stronger contrast than flat pixel art)
- **Texture patterns**: Brick mortar, wood planks, stone cracks, grass spikes
- **Cel-shaded volumes**: 3-4 tones per surface with hard transitions (no gradients)

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

# Combine: objects matching "leaf" only
python generate_assets.py --only objects --grep leaf
```

### Procedural Control

```bash
# Different seed for variation
python generate_assets.py --seed 999

# Recolor everything +120 degrees
python generate_assets.py --hue-shift 120

# Create themed biome variants
python generate_assets.py --hue-shift 0 --only terrain,objects --output ./biome_forest
python generate_assets.py --hue-shift 30 --only terrain,objects --output ./biome_desert
python generate_assets.py --hue-shift 200 --only terrain,objects --output ./biome_ice
python generate_assets.py --hue-shift 330 --only terrain,objects --output ./biome_volcanic

# Enemy difficulty color variants
python generate_assets.py --only enemies --hue-shift 0 --output ./enemies_normal
python generate_assets.py --only enemies --hue-shift 120 --output ./enemies_elite
python generate_assets.py --only enemies --hue-shift 240 --output ./enemies_boss
```

### Real-World Workflows

```bash
# Quick prototype: just player + terrain
python generate_assets.py --only player,terrain --profile mobile --no-atlas

# Preview all animations as GIFs for review
python generate_assets.py --gif --gif-scale 8 --no-atlas

# CI/CD: validate all assets pass mobile quality
python generate_assets.py --profile mobile --validate-only

# Production build: clean, mobile profile, all assets
python generate_assets.py --clean --profile mobile

# Iterate on one asset quickly
python generate_assets.py --only objects --types tree_sway --gif --gif-scale 8 --no-atlas
```

## Available Categories

| Category | Key | Assets | Description |
|----------|-----|--------|-------------|
| Player | `player` | 7 x 4 dirs | idle, walk, run, attack (visible sword), jump, hit, death |
| Enemies | `enemies` | 21 | 5 types x idle/hit/death (slime x3, skeleton, bat, ghost, goblin) |
| NPCs | `npcs` | 4 | villager, merchant with animations |
| Terrain | `terrain` | 42 | 9 tile types + 32 autotile edge variants |
| Items | `items` | 13 | weapons, potions, gems, misc (static) |
| UI | `ui` | 13 | hearts, bars, buttons, inventory (static) |
| Effects | `effects` | 24 | explosions, magic, particles, combos |
| Objects | `objects` | 12 | rock, sky, leaf, tree, water, grass animations |
| Weapons | `weapons` | 29 | melee, ranged, magic, shields, enchanted, rarity |
| Buildings | `buildings` | 21 | houses, castle, shops, church, windmill, ruins |

**Total: 186 assets (96 animated, 90 static)**

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
  weapons/           # 29 weapons, shields, enchanted
  buildings/         # 21 buildings & structures
  atlas/             # texture atlas + mappings
```

## Architecture

```
engine/
  drawing.py    # Pixel primitives, thick outlines, texture patterns, shading
  sprite.py     # SpriteSheet, DirectionalSprite, StaticSprite
  palette.py    # KR-style muted warm palettes, 3-tier shading, KR_OUTLINE
  noise.py      # Value noise + fractal noise for procedural generation
  metadata.py   # JSON export
  atlas.py      # Texture atlas packing
  quality.py    # Quality profiles and validation
  scaling.py    # Nearest-neighbor scaling

sprites/
  player.py     # Player animations (7 states x 4 directions, visible sword)
  enemies.py    # 5 enemy types with variants
  npcs.py       # Villager, merchant
  terrain.py    # 9 tiles + 32 autotiles
  items.py      # Weapons, potions, gems, misc
  ui.py         # Health bars, buttons, inventory
  effects.py    # 24 visual effects
  objects.py    # 12 natural object animations
  weapons.py    # 29 weapons, shields, enchanted, rarity
  buildings.py  # 21 buildings & structures
```

### Key Engine Functions

**Drawing (engine/drawing.py):**
- `new_sprite(w, h)` — create transparent canvas
- `put_pixel(img, x, y, color)` — draw single pixel
- `draw_outline_thick(img, color, thickness)` — KR-style 2px outline
- `draw_brick_pattern(img, ...)` — brick wall texture
- `draw_plank_pattern(img, ...)` — wood plank texture
- `draw_stone_texture(img, ...)` — stone crack texture
- `draw_grass_spikes(img, ...)` — KR-style grass blades
- `draw_thatch_pattern(img, ...)` — roof thatch texture
- `apply_shading_auto(img, palette_map)` — cel-shaded volume
- `composite_layers(*layers)` — layer composition

**Palette (engine/palette.py):**
- `KR_OUTLINE = (50, 35, 25)` — warm dark brown, never black
- `mute_color(rgb, factor)` — shift toward grey
- `warm_shift(rgb, amount)` — shift toward warm
- 9 palettes: PLAYER, TERRAIN, WEAPONS, ITEMS, UI, ENEMIES, OBJECTS, EFFECTS, BUILDINGS

### Adding New Assets

1. Create a generator function in the appropriate `sprites/*.py` module
2. Return a `SpriteSheet` (animated) or `StaticSprite` (static)
3. Add it to that module's `generate_all()` function
4. The main pipeline auto-discovers via `generate_all()`

```python
from engine.drawing import new_sprite, put_pixel, draw_outline_thick
from engine.palette import OBJECTS
from engine.sprite import SpriteSheet

def generate_my_animation() -> SpriteSheet:
    frames = []
    for f in range(8):
        img = new_sprite()  # 16x16 transparent
        put_pixel(img, 7, 7, OBJECTS.base("rock_gray"))
        img = draw_outline_thick(img)  # 2px KR outline
        frames.append(img)
    return SpriteSheet("my_animation", frames, frame_duration_ms=100, loop=True)
```

### Palette System

Colors use KR-style muted 3-tier shading:

```python
from engine.palette import _build_palette

MY_PALETTE = _build_palette("my_palette", {
    "primary": (100, 150, 200),   # Muted RGB base
    "accent": (200, 100, 50),     # Warm accent
})

MY_PALETTE.highlight("primary")  # +25% lightness
MY_PALETTE.base("primary")       # Original muted color
MY_PALETTE.shadow("primary")     # -30% lightness
```

## Godot 4.6 Integration

A complete sample Godot project demonstrates all assets working together:

**World:** 50x40 tiles with village, castle, nature, adventure zones
**Player:** 7 animations, weapon switching (Q/E), held weapon sprite
**Enemies:** 10 enemies with wandering AI, idle/hit/death
**Buildings:** 21 structures at 3x-6x scale
**Viewport:** 1280x720 HD landscape, 1.5x camera zoom

Controls: Arrow keys (move), Shift (run), Space (attack), Q/E (switch weapon)
