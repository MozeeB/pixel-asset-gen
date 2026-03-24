# Asset Generator

Procedural pixel art game asset generator in **Kingdom Rush cel-shaded style**.
Python + Pillow. No external dependencies beyond Pillow.

## Art Style: Kingdom Rush

- **Cel-shaded**: 3-4 muted color tones per surface, hard transitions (no gradients)
- **No pure black**: Darkest color is warm dark brown `KR_OUTLINE = (50, 35, 25)`
- **Thick outlines**: 2px via `draw_outline_thick()`, warm brown
- **Muted palette**: All colors grey-shifted with warm undertones
- **Bold shading**: Highlight +25% / Shadow -30% (stronger than standard pixel art)
- **Texture patterns**: Brick mortar, wood planks, stone cracks, grass spikes, thatch

## Project Structure

```
engine/           Core rendering engine
  drawing.py      Pixel primitives, thick outlines, shading, texture patterns
  sprite.py       SpriteSheet, DirectionalSprite, StaticSprite dataclasses
  palette.py      KR-style color system: muted warm palettes, 3-tier shading
  noise.py        Value noise + fractal noise (deterministic, seeded)
  metadata.py     JSON metadata export
  atlas.py        Texture atlas packing
  quality.py      Mobile/desktop quality profiles + validation
  scaling.py      Nearest-neighbor scaling

sprites/          Asset generators (each has generate_all() -> list)
  player.py       Player animations (7 states x 4 directions, visible sword attack)
  enemies.py      5 enemy types with idle/hit/death
  npcs.py         Villager, merchant
  terrain.py      9 tiles + 32 autotile variants
  items.py        Weapons, potions, gems, misc (static)
  ui.py           Hearts, bars, buttons, inventory
  effects.py      24 visual effects
  objects.py      12 natural object animations (rock, sky, leaf, tree, water, grass)
  weapons.py      29 weapons & shields (melee, ranged, magic, enchanted, rarity)
  buildings.py    21 buildings & structures (houses, castle, shops, animated)

generate_assets.py  Main CLI entry point (full CLI reference below)
```

## Key Commands

### Generate All
```bash
python generate_assets.py
python generate_assets.py --profile mobile
python generate_assets.py --profile desktop
```

### Filter by Category
```bash
python generate_assets.py --only player
python generate_assets.py --only player,objects,effects
python generate_assets.py --only terrain,objects
```

### Filter by Type
```bash
python generate_assets.py --only objects --types rock_idle,tree_sway
python generate_assets.py --only enemies --types slime,skeleton
```

### Exclude Specific Assets
```bash
python generate_assets.py --only enemies --exclude slime_blue,slime_red
```

### Grep / Search
```bash
python generate_assets.py --grep fire --list       # Search + list
python generate_assets.py --grep water             # Search + generate
python generate_assets.py --only objects --grep leaf
```

### Inspection
```bash
python generate_assets.py --list                   # List all with details
python generate_assets.py --count                  # Count summary
python generate_assets.py --info rock_idle          # Detailed asset info
python generate_assets.py --dry-run                 # Preview without writing
python generate_assets.py --validate-only           # Validate quality
```

### Output Control
```bash
python generate_assets.py --output ./my_assets      # Custom output dir
python generate_assets.py --scales 1,2,4,8          # Custom scale factors
python generate_assets.py --no-atlas                # Skip atlas
python generate_assets.py --no-metadata             # Skip JSON metadata
python generate_assets.py --gif                     # Export animated GIFs
python generate_assets.py --gif --gif-scale 8       # GIFs at 8x scale
```

### Procedural Control
```bash
python generate_assets.py --seed 999                # Different seed for variation
python generate_assets.py --hue-shift 120           # Recolor +120 degrees
python generate_assets.py --hue-shift 180 --output ./hell_theme  # Themed variant
```

### Maintenance
```bash
python generate_assets.py --clean                   # Delete output first
python generate_assets.py --clean --only objects    # Clean + regen category
python generate_assets.py -v                        # Verbose (show all scales)
```

### Real-World Combos
```bash
# Biome variants
python generate_assets.py --hue-shift 0 --only terrain,objects --output ./forest
python generate_assets.py --hue-shift 30 --only terrain,objects --output ./desert
python generate_assets.py --hue-shift 200 --only terrain,objects --output ./ice

# Iterate on one asset with GIF preview
python generate_assets.py --only objects --types tree_sway --gif --gif-scale 8 --no-atlas

# CI validation
python generate_assets.py --profile mobile --validate-only

# Full production build
python generate_assets.py --clean --profile mobile
```

## Categories

player, enemies, npcs, terrain, items, ui, effects, objects, weapons, buildings

Total: 186 assets (96 animated, 90 static)

## CLI Flags Reference

| Flag | Type | Description |
|------|------|-------------|
| `--only` | filter | Comma-separated categories |
| `--types` | filter | Comma-separated asset names |
| `--exclude` | filter | Comma-separated names to skip |
| `--grep` | filter | Substring search on names |
| `--output`, `-o` | output | Custom output directory |
| `--scales` | output | Custom scale factors (e.g. 1,2,4,8) |
| `--profile` | output | mobile or desktop quality profile |
| `--no-atlas` | output | Skip texture atlas |
| `--no-metadata` | output | Skip JSON metadata |
| `--gif` | output | Export animated GIFs |
| `--gif-scale` | output | GIF scale factor (default: 4) |
| `--seed` | procedural | Global seed offset for variation |
| `--hue-shift` | procedural | Recolor by N degrees (0-360) |
| `--list` | inspect | List all assets with details |
| `--count` | inspect | Asset count per category |
| `--info NAME` | inspect | Detailed info for one asset |
| `--dry-run` | inspect | Preview without writing files |
| `--validate-only` | inspect | Validate against profile |
| `--clean` | maint | Delete output dir before generating |
| `--verbose`, `-v` | maint | Show all scale variants |

## Architecture Patterns

- **Kingdom Rush cel-shading**: 3-4 muted tones, thick warm outlines, no pure black
- **Immutable sprites**: All drawing functions return new images, never mutate
- **Bold 3-tier shading**: highlight +25% / base / shadow -30% via HSL
- **Texture patterns**: `draw_brick_pattern()`, `draw_plank_pattern()`, `draw_stone_texture()`, `draw_grass_spikes()`, `draw_thatch_pattern()`
- **Thick outlines**: `draw_outline_thick(img)` for 2px warm brown outlines
- **Deterministic noise**: Seeded value noise for reproducible procedural textures
- **generate_all() convention**: Each sprites/*.py exports generate_all() returning list
- **Palette separation**: Colors defined in engine/palette.py, referenced by key name
- **Hue shift pipeline**: Any asset can be recolored via --hue-shift without code changes

## Adding New Assets

1. Add generator function in appropriate `sprites/*.py` module
2. Use `new_sprite()` for 16x16 transparent canvas
3. Draw with `put_pixel()`, `draw_outline_thick()`, `draw_circle()`, etc.
4. Return `SpriteSheet(name, frames, frame_duration_ms, loop)` for animations
5. Return `StaticSprite(name, image, category)` for static sprites
6. Add to that module's `generate_all()` list
7. If new palette needed, add to `engine/palette.py` using `_build_palette()`

## Adding New Categories

1. Create `sprites/newcat.py` with `generate_all()` function
2. Add entry to `CATEGORIES` dict in `generate_assets.py`
3. Add directory mapping in `create_dirs()` category_dirs
4. Add to `GENERATORS` dict in `generate_assets.py`
5. Add to `cat_dirs` and `cat_sprite_types` dicts in `main()`
6. Import in `generate_assets.py`

## Output Format

Each sprite produces:
- `name.png` (1x), `name_2x.png`, `name_4x.png`
- `name.json` (metadata: frames, timing, hitbox, anchor, fps)
- `name_4x.gif` (animated preview, with `--gif`)

## Code Style

- Pure Python + Pillow only, no other dependencies
- Functions < 50 lines, files < 800 lines
- Pixel coordinates are (x, y) with origin top-left
- All colors are RGB tuples `(r, g, b)` or RGBA `(r, g, b, a)`
- No pure black — use `KR_OUTLINE` (50, 35, 25) for darkest color
- Seeds are explicit integers for deterministic output
- Use `math.sin`/`math.cos` for procedural animation curves
- Use `noise_map()` / `fractal_noise()` for organic textures

## Godot Integration

Godot MCP server configured for Godot 4.6. Assets are designed for Godot import:
- PNG sprite sheets with JSON metadata
- Texture atlas with coordinate mappings
- 16x16 base size (standard tile size)
- Nearest-neighbor scaling preserves pixel art crispness
- Sample Godot project at `../godot-game/game-test-assets/`
  - 50x40 tile world with village, castle, adventure zones
  - Player with weapon switching (Q/E), visible held weapon
  - 10 enemies with wandering AI + idle/hit/death animations
  - NPCs, items, effects, buildings all placed and working
  - 1280x720 landscape viewport, 1.5x camera zoom
