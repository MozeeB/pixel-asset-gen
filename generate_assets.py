"""
Production-Ready Pixel Art Game Asset Generator

Generates a complete set of game-ready assets with full CLI control.

Usage:
  python generate_assets.py                                    # Generate all
  python generate_assets.py --only player,objects              # Specific categories
  python generate_assets.py --only objects --types rock_idle,tree_sway
  python generate_assets.py --profile mobile                   # Mobile quality
  python generate_assets.py --list                             # Show all assets
  python generate_assets.py --only effects --gif               # Export animated GIFs
  python generate_assets.py --hue-shift 120                    # Recolor everything
  python generate_assets.py --seed 999 --only objects          # Custom seed
  python generate_assets.py --grep fire                        # Find matching assets
"""

import argparse
import glob as _glob_mod
import json
import math as _math
import os
import shutil
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image

from engine.scaling import scale_nearest
from engine.metadata import export_metadata, export_tileset_metadata
from engine.atlas import pack_atlas, save_atlas
from engine.sprite import SpriteSheet, DirectionalSprite, StaticSprite
from engine.drawing import create_spritesheet
from engine.quality import get_profile, validate_sprite_size, validate_atlas_size, QualityProfile, PROFILES
from engine.palette import recolor

from sprites import player, enemies, npcs, items, terrain, effects, ui, objects, weapons, buildings

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
SCALE_FACTORS = [1, 2, 4]

# All available categories and their modules
CATEGORIES = {
    "player": "Characters (Player)",
    "enemies": "Characters (Enemies)",
    "npcs": "Characters (NPCs)",
    "terrain": "Terrain",
    "items": "Items",
    "ui": "UI",
    "effects": "Effects",
    "objects": "Objects (Natural)",
    "weapons": "Weapons & Shields",
    "buildings": "Buildings & Structures",
}

GENERATORS = {
    "player": player.generate_all,
    "enemies": enemies.generate_all,
    "npcs": npcs.generate_all,
    "terrain": terrain.generate_all,
    "items": items.generate_all,
    "ui": ui.generate_all,
    "effects": effects.generate_all,
    "objects": objects.generate_all,
    "weapons": weapons.generate_all,
    "buildings": buildings.generate_all,
}


# ============================================================
# HELPERS
# ============================================================

def create_dirs(categories: set[str], output_dir: str):
    """Create output directories for requested categories."""
    category_dirs = {
        "player": ["characters/player"],
        "enemies": ["characters/enemies"],
        "npcs": ["characters/npcs"],
        "terrain": ["terrain", "terrain/autotile"],
        "items": ["items/weapons", "items/potions", "items/gems", "items/misc"],
        "ui": ["ui"],
        "effects": ["effects"],
        "objects": ["objects"],
        "weapons": ["weapons"],
        "buildings": ["buildings"],
    }
    dirs = ["atlas"]
    for cat in categories:
        dirs.extend(category_dirs.get(cat, []))
    for d in dirs:
        os.makedirs(os.path.join(output_dir, d), exist_ok=True)


def save_png(img, rel_path, output_dir, scale_factors=None):
    """Save a PNG and its scaled variants. Returns list of saved paths."""
    factors = scale_factors or SCALE_FACTORS
    saved = []
    for scale in factors:
        suffix = f"_{scale}x" if scale > 1 else ""
        base, ext = os.path.splitext(rel_path)
        full_path = os.path.join(output_dir, f"{base}{suffix}{ext}")
        if scale > 1:
            scaled = scale_nearest(img, scale)
        else:
            scaled = img
        scaled.save(full_path)
        saved.append(f"{base}{suffix}{ext}")
    return saved


def save_gif(sheet: SpriteSheet, rel_path: str, output_dir: str, scale: int = 1):
    """Export a SpriteSheet as an animated GIF."""
    base, _ = os.path.splitext(rel_path)
    suffix = f"_{scale}x" if scale > 1 else ""
    gif_path = os.path.join(output_dir, f"{base}{suffix}.gif")

    frames_rgba = []
    for frame in sheet.frames:
        f = frame if scale <= 1 else scale_nearest(frame, scale)
        frames_rgba.append(f.convert("RGBA"))

    if not frames_rgba:
        return []

    # Compute per-frame durations
    if sheet.frame_durations_ms:
        durations = list(sheet.frame_durations_ms)
    else:
        durations = [sheet.frame_duration_ms] * sheet.frame_count

    # GIF needs P mode; convert via quantize
    gif_frames = []
    for f in frames_rgba:
        # Create white background, paste frame on it
        bg = Image.new("RGBA", f.size, (0, 0, 0, 0))
        bg.paste(f, (0, 0))
        gif_frames.append(bg.convert("P", palette=Image.ADAPTIVE, colors=256))

    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=durations,
        loop=0 if sheet.loop else 1,
        transparency=0,
        disposal=2,
    )
    return [f"{base}{suffix}.gif"]


def save_spritesheet(sheet: SpriteSheet, rel_path: str, all_sprites: list,
                     output_dir: str, scale_factors=None, export_gif: bool = False,
                     gif_scale: int = 1):
    """Save a SpriteSheet as PNG + JSON metadata + scaled variants + optional GIF."""
    img = sheet.to_spritesheet()
    saved = save_png(img, rel_path, output_dir, scale_factors)
    # Metadata
    meta_path = os.path.join(output_dir, rel_path)
    export_metadata(sheet, meta_path)
    # GIF
    if export_gif:
        saved.extend(save_gif(sheet, rel_path, output_dir, gif_scale))
    # Collect for atlas
    all_sprites.append((sheet.name, img))
    return saved


def save_directional(dsprite: DirectionalSprite, base_dir: str, all_sprites: list,
                     output_dir: str, scale_factors=None, export_gif: bool = False,
                     gif_scale: int = 1):
    """Save all directions of a DirectionalSprite."""
    saved = []
    for sheet in dsprite.all_sheets():
        rel = f"{base_dir}/{sheet.name}.png"
        saved.extend(save_spritesheet(sheet, rel, all_sprites, output_dir,
                                      scale_factors, export_gif, gif_scale))
    # Directional metadata
    meta_path = os.path.join(output_dir, base_dir, f"{dsprite.name}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(dsprite.to_metadata(), f, indent=2)
    return saved


def save_static(sprite: StaticSprite, rel_path: str, all_sprites: list,
                output_dir: str, scale_factors=None):
    """Save a static sprite as PNG + JSON metadata + scaled variants."""
    saved = save_png(sprite.image, rel_path, output_dir, scale_factors)
    meta_path = os.path.join(output_dir, rel_path)
    export_metadata(sprite, meta_path)
    all_sprites.append((sprite.name, sprite.image))
    return saved


def _get_asset_name(asset) -> str:
    """Extract name from any asset type."""
    if hasattr(asset, "name"):
        return asset.name
    return ""


def _filter_assets(assets: list, type_filter: set[str] | None,
                   exclude_filter: set[str] | None,
                   grep_pattern: str | None) -> list:
    """Filter assets by name, exclusion, or pattern match."""
    result = assets
    if type_filter is not None:
        result = [a for a in result if _get_asset_name(a) in type_filter]
    if exclude_filter is not None:
        result = [a for a in result if _get_asset_name(a) not in exclude_filter]
    if grep_pattern is not None:
        pattern = grep_pattern.lower()
        result = [a for a in result if pattern in _get_asset_name(a).lower()]
    return result


def _apply_hue_shift(asset, hue_shift: float):
    """Apply hue shift to all frames/image of an asset. Returns new asset."""
    if hue_shift == 0:
        return asset

    def _shift_image(img: Image.Image) -> Image.Image:
        new_img = img.copy()
        pixels = new_img.load()
        for y in range(new_img.height):
            for x in range(new_img.width):
                r, g, b, a = pixels[x, y]
                if a > 0:
                    nr, ng, nb = recolor((r, g, b), hue_shift)
                    pixels[x, y] = (nr, ng, nb, a)
        return new_img

    if isinstance(asset, SpriteSheet):
        new_frames = [_shift_image(f) for f in asset.frames]
        return SpriteSheet(
            name=asset.name,
            frames=new_frames,
            frame_duration_ms=asset.frame_duration_ms,
            loop=asset.loop,
            frame_durations_ms=asset.frame_durations_ms,
        )
    elif isinstance(asset, DirectionalSprite):
        def _shift_sheet(s):
            if s is None:
                return None
            new_frames = [_shift_image(f) for f in s.frames]
            return SpriteSheet(
                name=s.name, frames=new_frames,
                frame_duration_ms=s.frame_duration_ms,
                loop=s.loop, frame_durations_ms=s.frame_durations_ms,
            )
        return DirectionalSprite(
            name=asset.name,
            down=_shift_sheet(asset.down),
            up=_shift_sheet(asset.up),
            right=_shift_sheet(asset.right),
            _left=_shift_sheet(asset._left) if asset._left else None,
        )
    elif isinstance(asset, StaticSprite):
        return StaticSprite(
            name=asset.name,
            image=_shift_image(asset.image),
            category=asset.category,
        )
    return asset


# ============================================================
# LIST / GREP / COUNT
# ============================================================

def list_assets(grep_pattern: str | None = None):
    """Print all available categories and asset names."""
    print("=" * 55)
    title = "Available Asset Categories & Types"
    if grep_pattern:
        title += f"  (filter: '{grep_pattern}')"
    print(f"  {title}")
    print("=" * 55)

    total_count = 0
    for cat, label in CATEGORIES.items():
        try:
            raw_assets = GENERATORS[cat]()
            filtered = _filter_assets(raw_assets, None, None, grep_pattern)
            if not filtered and grep_pattern:
                continue
            print(f"\n  [{cat}] {label}  ({len(filtered)} assets)")
            for asset in filtered:
                name = _get_asset_name(asset)
                if isinstance(asset, DirectionalSprite):
                    dirs = ", ".join(d for d in ["down", "up", "right", "left"]
                                    if getattr(asset, d, None) is not None)
                    print(f"    - {name}  (directional: {dirs})")
                elif isinstance(asset, SpriteSheet):
                    fc = asset.frame_count
                    dur = asset.total_duration_ms
                    loop = "loop" if asset.loop else "once"
                    fps = round(asset.effective_fps, 1)
                    w, h = asset.frame_width, asset.frame_height
                    print(f"    - {name}  ({fc} frames, {dur}ms, {fps}fps, {w}x{h}, {loop})")
                elif isinstance(asset, StaticSprite):
                    w, h = asset.image.width, asset.image.height
                    cat_label = f", {asset.category}" if asset.category else ""
                    print(f"    - {name}  (static {w}x{h}{cat_label})")
                total_count += 1
        except Exception as e:
            print(f"    (error listing: {e})")

    print()
    print(f"  Total: {total_count} assets")
    print()
    print("=" * 55)
    print("  Usage Examples:")
    print("  python generate_assets.py --only player")
    print("  python generate_assets.py --only objects,effects")
    print("  python generate_assets.py --only objects --types rock_idle,tree_sway")
    print("  python generate_assets.py --grep fire")
    print("  python generate_assets.py --count")
    print("=" * 55)


def count_assets():
    """Print asset counts per category."""
    print("=" * 45)
    print("  Asset Count Summary")
    print("=" * 45)
    grand = 0
    animated = 0
    static_count = 0
    for cat, label in CATEGORIES.items():
        try:
            assets = GENERATORS[cat]()
            count = len(assets)
            a_count = sum(1 for a in assets if isinstance(a, (SpriteSheet, DirectionalSprite)))
            s_count = count - a_count
            grand += count
            animated += a_count
            static_count += s_count
            print(f"  {label:<25} {count:>4}  ({a_count} animated, {s_count} static)")
        except Exception as e:
            print(f"  {label:<25}  error: {e}")
    print("  " + "-" * 43)
    print(f"  {'TOTAL':<25} {grand:>4}  ({animated} animated, {static_count} static)")
    print("=" * 45)


def show_info(asset_name: str):
    """Show detailed info about a specific asset."""
    for cat in CATEGORIES:
        try:
            assets = GENERATORS[cat]()
            for asset in assets:
                name = _get_asset_name(asset)
                if name == asset_name:
                    print(f"  Asset: {name}")
                    print(f"  Category: {cat} ({CATEGORIES[cat]})")
                    if isinstance(asset, DirectionalSprite):
                        print(f"  Type: DirectionalSprite")
                        for sheet in asset.all_sheets():
                            print(f"    Direction: {sheet.name}")
                            _print_sheet_info(sheet, indent=6)
                    elif isinstance(asset, SpriteSheet):
                        print(f"  Type: SpriteSheet")
                        _print_sheet_info(asset, indent=4)
                    elif isinstance(asset, StaticSprite):
                        print(f"  Type: StaticSprite")
                        print(f"    Size: {asset.image.width}x{asset.image.height}")
                        print(f"    Sub-category: {asset.category}")
                        print(f"    Hitbox: {asset.hitbox()}")
                    return
        except Exception:
            continue
    print(f"  Asset '{asset_name}' not found. Use --list to see available assets.")


def _print_sheet_info(sheet: SpriteSheet, indent: int = 4):
    pad = " " * indent
    print(f"{pad}Frame size: {sheet.frame_width}x{sheet.frame_height}")
    print(f"{pad}Frame count: {sheet.frame_count}")
    print(f"{pad}Duration: {sheet.total_duration_ms}ms")
    print(f"{pad}FPS: {round(sheet.effective_fps, 1)}")
    print(f"{pad}Loop: {sheet.loop}")
    if sheet.frame_durations_ms:
        print(f"{pad}Per-frame timing: {sheet.frame_durations_ms}")
    else:
        print(f"{pad}Frame duration: {sheet.frame_duration_ms}ms")
    print(f"{pad}Hitbox: {sheet.hitbox()}")
    print(f"{pad}Anchor: {sheet.anchor()}")
    meta = sheet.to_metadata()
    print(f"{pad}Recommended FPS: mobile={meta['recommended_fps']['mobile']}, "
          f"desktop={meta['recommended_fps']['desktop']}")


# ============================================================
# CLI
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Production Pixel Art Asset Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Filtering:
  %(prog)s --only player,objects            Category filter
  %(prog)s --only objects --types rock_idle  Specific assets
  %(prog)s --exclude slime_blue,slime_red   Skip specific assets
  %(prog)s --grep fire                      Fuzzy name search
  %(prog)s --grep water --list              Search + list details

Output Control:
  %(prog)s --output ./my_assets             Custom output directory
  %(prog)s --scales 1,2,3,4,8              Custom scale factors
  %(prog)s --no-atlas                       Skip texture atlas
  %(prog)s --no-metadata                    Skip JSON metadata
  %(prog)s --gif                            Export animated GIFs
  %(prog)s --gif --gif-scale 4              GIFs at 4x scale

Procedural Control:
  %(prog)s --seed 999                       Custom global seed offset
  %(prog)s --hue-shift 120                  Recolor all sprites +120 degrees
  %(prog)s --hue-shift -30 --only enemies   Recolor enemies only

Inspection:
  %(prog)s --list                           List all assets with details
  %(prog)s --count                          Asset counts per category
  %(prog)s --info rock_idle                 Detailed info for one asset
  %(prog)s --dry-run                        Show what would be generated

Maintenance:
  %(prog)s --clean                          Delete output dir before generating
  %(prog)s --clean --only objects           Clean then regenerate objects only
        """,
    )

    # --- Filtering ---
    filt = parser.add_argument_group("Filtering")
    filt.add_argument(
        "--only",
        default=None,
        help="Comma-separated categories: " + ", ".join(CATEGORIES.keys()),
    )
    filt.add_argument(
        "--types",
        default=None,
        help="Comma-separated asset names within selected categories.",
    )
    filt.add_argument(
        "--exclude",
        default=None,
        help="Comma-separated asset names to skip.",
    )
    filt.add_argument(
        "--grep",
        default=None,
        help="Filter assets by substring match on name (case-insensitive).",
    )

    # --- Output Control ---
    out = parser.add_argument_group("Output Control")
    out.add_argument(
        "--output", "-o",
        default=None,
        help="Custom output directory. Default: ./assets",
    )
    out.add_argument(
        "--scales",
        default=None,
        help="Comma-separated scale factors. e.g. '1,2,4' or '2,3,4,8'",
    )
    out.add_argument(
        "--profile",
        choices=list(PROFILES.keys()),
        default=None,
        help="Quality profile: 'mobile' or 'desktop'.",
    )
    out.add_argument(
        "--no-atlas",
        action="store_true",
        help="Skip texture atlas generation.",
    )
    out.add_argument(
        "--no-metadata",
        action="store_true",
        help="Skip JSON metadata export.",
    )
    out.add_argument(
        "--gif",
        action="store_true",
        help="Also export animated GIFs for all SpriteSheet assets.",
    )
    out.add_argument(
        "--gif-scale",
        type=int,
        default=4,
        help="Scale factor for GIF exports. Default: 4",
    )

    # --- Procedural Control ---
    proc = parser.add_argument_group("Procedural Control")
    proc.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Global seed offset added to all generators for variation.",
    )
    proc.add_argument(
        "--hue-shift",
        type=float,
        default=0.0,
        help="Shift hue of all generated sprites by N degrees (0-360).",
    )

    # --- Inspection ---
    insp = parser.add_argument_group("Inspection")
    insp.add_argument(
        "--list",
        action="store_true",
        help="List all available assets with frame/size details.",
    )
    insp.add_argument(
        "--count",
        action="store_true",
        help="Show asset count summary per category.",
    )
    insp.add_argument(
        "--info",
        default=None,
        help="Show detailed info for a specific asset by name.",
    )
    insp.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing files.",
    )
    insp.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate sprites against profile without generating.",
    )

    # --- Maintenance ---
    maint = parser.add_argument_group("Maintenance")
    maint.add_argument(
        "--clean",
        action="store_true",
        help="Delete output directory before generating.",
    )
    maint.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show all scale variants in output (not just 1x).",
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main():
    args = parse_args()

    # --- Inspection-only modes ---
    if args.count:
        count_assets()
        return

    if args.info:
        show_info(args.info)
        return

    if args.list:
        list_assets(grep_pattern=args.grep)
        return

    # --- Parse filters ---
    if args.only:
        selected_categories = set(c.strip() for c in args.only.split(","))
        unknown = selected_categories - set(CATEGORIES.keys())
        if unknown:
            print(f"ERROR: Unknown categories: {', '.join(unknown)}")
            print(f"Available: {', '.join(CATEGORIES.keys())}")
            sys.exit(1)
    else:
        selected_categories = set(CATEGORIES.keys())

    type_filter = set(t.strip() for t in args.types.split(",")) if args.types else None
    exclude_filter = set(e.strip() for e in args.exclude.split(",")) if args.exclude else None
    grep_pattern = args.grep

    # --- Output config ---
    output_dir = args.output or OUTPUT_DIR
    if args.output:
        output_dir = os.path.abspath(args.output)

    profile = get_profile(args.profile) if args.profile else None

    if args.scales:
        scale_factors = sorted(set(int(s.strip()) for s in args.scales.split(",")))
    elif profile:
        scale_factors = list(profile.scale_factors)
    else:
        scale_factors = SCALE_FACTORS

    hue_shift = args.hue_shift
    export_gif = args.gif
    gif_scale = args.gif_scale
    no_metadata = args.no_metadata
    verbose = args.verbose
    seed_offset = args.seed or 0

    # --- Clean ---
    if args.clean and os.path.exists(output_dir):
        print(f"  Cleaning {output_dir}...")
        shutil.rmtree(output_dir)

    # --- Header ---
    print("=" * 55)
    print("  Production Pixel Art Asset Generator")
    if profile:
        print(f"  Profile: {profile.name} — {profile.description}")
    if args.only:
        print(f"  Categories: {', '.join(sorted(selected_categories))}")
    if type_filter:
        print(f"  Types: {', '.join(sorted(type_filter))}")
    if exclude_filter:
        print(f"  Exclude: {', '.join(sorted(exclude_filter))}")
    if grep_pattern:
        print(f"  Grep: '{grep_pattern}'")
    print(f"  Scales: {', '.join(f'{s}x' for s in scale_factors)}")
    if hue_shift:
        print(f"  Hue shift: {hue_shift} degrees")
    if seed_offset:
        print(f"  Seed offset: +{seed_offset}")
    if export_gif:
        print(f"  GIF export: {gif_scale}x")
    if args.dry_run:
        print(f"  MODE: DRY RUN (no files written)")
    elif args.validate_only:
        print(f"  MODE: VALIDATE ONLY")
    print(f"  Output: {output_dir}")
    print("=" * 55)
    print()

    quality_warnings = []

    if not args.dry_run and not args.validate_only:
        create_dirs(selected_categories, output_dir)

    all_sprites = []
    total_files = 0
    asset_manifest = []  # for dry-run

    def _validate(name, img, sprite_type="sprite"):
        if profile:
            return validate_sprite_size(img.width, img.height, profile, sprite_type)
        return []

    def _should_print(s):
        if verbose:
            return True
        return not any(f"_{sc}x" in s for sc in scale_factors if sc > 1)

    # --- Generation helper ---
    def _process_category(cat_key, cat_dir, sprite_type="sprite"):
        nonlocal total_files
        assets = GENERATORS[cat_key]()
        assets = _filter_assets(assets, type_filter, exclude_filter, grep_pattern)

        if not assets:
            return

        print(f">> {CATEGORIES[cat_key]}")

        for asset in assets:
            # Apply hue shift
            processed = _apply_hue_shift(asset, hue_shift) if hue_shift else asset
            name = _get_asset_name(processed)

            if args.dry_run:
                asset_manifest.append({"name": name, "category": cat_key,
                                       "type": type(asset).__name__})
                print(f"  [DRY] {name}")
                continue

            if isinstance(processed, DirectionalSprite):
                for sheet in processed.all_sheets():
                    quality_warnings.extend(_validate(sheet.name, sheet.frames[0], sprite_type))
                if not args.validate_only:
                    saved = save_directional(processed, cat_dir, all_sprites,
                                             output_dir, scale_factors, export_gif, gif_scale)
                    total_files += len(saved)
                    for s in saved:
                        if _should_print(s):
                            print(f"  [OK] {s}")

            elif isinstance(processed, SpriteSheet):
                quality_warnings.extend(_validate(name, processed.frames[0], sprite_type))
                if not args.validate_only:
                    saved = save_spritesheet(processed, f"{cat_dir}/{name}.png",
                                             all_sprites, output_dir, scale_factors,
                                             export_gif, gif_scale)
                    total_files += len(saved)
                    for s in saved:
                        if _should_print(s):
                            print(f"  [OK] {s}")

            elif isinstance(processed, StaticSprite):
                quality_warnings.extend(_validate(name, processed.image, sprite_type))
                if not args.validate_only:
                    sub_cat = getattr(processed, "category", "")
                    if "autotile" in sub_cat:
                        saved = save_png(processed.image, f"{cat_dir}/autotile/{name}.png",
                                         output_dir, scale_factors)
                        all_sprites.append((name, processed.image))
                    else:
                        rel_dir = cat_dir
                        # Items have sub-categories
                        if cat_key == "items" and sub_cat:
                            rel_dir = f"{cat_dir}/{sub_cat}"
                        saved = save_static(processed, f"{rel_dir}/{name}.png",
                                            all_sprites, output_dir, scale_factors)
                    total_files += len(saved)
                    for s in saved:
                        if _should_print(s) and "autotile" not in s:
                            print(f"  [OK] {s}")

    # --- Process each category ---
    cat_dirs = {
        "player": "characters/player",
        "enemies": "characters/enemies",
        "npcs": "characters/npcs",
        "terrain": "terrain",
        "items": "items",
        "ui": "ui",
        "effects": "effects",
        "objects": "objects",
        "weapons": "weapons",
        "buildings": "buildings",
    }
    cat_sprite_types = {
        "player": "character", "enemies": "character", "npcs": "character",
        "terrain": "terrain", "items": "item", "ui": "ui",
        "effects": "effect", "objects": "object", "weapons": "weapon",
        "buildings": "building",
    }

    for cat_key in CATEGORIES:
        if cat_key not in selected_categories:
            continue
        _process_category(cat_key, cat_dirs[cat_key], cat_sprite_types[cat_key])

        # Terrain-specific: autotile summary + tileset metadata
        if cat_key == "terrain" and not args.dry_run and not args.validate_only:
            autotile_count = sum(1 for n, _ in all_sprites if "autotile" in n)
            if autotile_count:
                print(f"  [OK] {autotile_count} auto-tile variants")
            terrain_tiles = [(n, img) for n, img in all_sprites
                             if not any(kw in n for kw in ("autotile", "tileset", "water", "lava"))]
            if terrain_tiles and not no_metadata:
                static_tiles = [StaticSprite(n, img) for n, img in terrain_tiles
                                if img.width == 16 and img.height == 16]
                if static_tiles:
                    export_tileset_metadata(static_tiles, os.path.join(output_dir, "terrain/tileset.png"))

    # --- Texture Atlas ---
    if (not args.validate_only and not args.no_atlas and not args.dry_run
            and all_sprites):
        print("\n>> Texture Atlas")
        max_atlas = profile.max_atlas_size if profile else 512
        atlas_sprites = [(n, img) for n, img in all_sprites
                         if img.width <= 20 and img.height <= 20]
        if atlas_sprites:
            _total_area = sum(im.width * im.height for _, im in atlas_sprites)
            _pack_width = min(max_atlas, max(128, int(_math.sqrt(_total_area) * 1.5)))
            atlas_img, atlas_map = pack_atlas(atlas_sprites, max_width=_pack_width, padding=1)
            atlas_files = save_atlas(atlas_img, atlas_map, os.path.join(output_dir, "atlas"),
                                     name="atlas", scales=scale_factors)
            total_files += len(atlas_files)
            print(f"  [OK] atlas.png ({atlas_img.width}x{atlas_img.height}, {len(atlas_sprites)} sprites)")
            for scale in scale_factors:
                if scale > 1:
                    sw, sh = atlas_img.width * scale, atlas_img.height * scale
                    print(f"  [OK] atlas_{scale}x.png ({sw}x{sh})")

            if profile:
                for scale in scale_factors:
                    aw = atlas_img.width * scale
                    ah = atlas_img.height * scale
                    quality_warnings.extend(validate_atlas_size(aw, ah, profile))

    # --- Quality Report ---
    if quality_warnings:
        print()
        print("=" * 55)
        print(f"  QUALITY WARNINGS ({len(quality_warnings)})")
        print("=" * 55)
        for w in quality_warnings:
            print(f"  [!] {w}")

    # --- Summary ---
    print()
    print("=" * 55)
    if args.dry_run:
        print(f"  DRY RUN: Would generate {len(asset_manifest)} assets")
        for item in asset_manifest:
            print(f"    {item['category']}/{item['name']}  ({item['type']})")
    elif args.validate_only:
        status = "PASS" if not quality_warnings else f"WARN ({len(quality_warnings)} issues)"
        print(f"  VALIDATION: {status}")
        if profile:
            print(f"  Profile: {profile.name}")
    else:
        print(f"  DONE! Generated {total_files}+ files")
        print(f"  Output: {output_dir}")
    print("=" * 55)

    if not args.validate_only and not args.dry_run and all_sprites:
        scale_label = ", ".join(f"{s}x" for s in scale_factors)
        print(f"\n  Unique sprites: {len(all_sprites)}")
        print(f"  Scale variants: {scale_label}")
        if not args.no_atlas:
            atlas_count = sum(1 for _, img in all_sprites if img.width <= 20 and img.height <= 20)
            print(f"  Atlas: {atlas_count} sprites packed")
        if export_gif:
            gif_count = sum(1 for n, _ in all_sprites)
            print(f"  GIFs: {gif_count} animated exports ({gif_scale}x)")
        print(f"  Metadata: {'JSON alongside every asset' if not no_metadata else 'SKIPPED'}")
        if hue_shift:
            print(f"  Hue shift: {hue_shift} degrees applied")
        if profile:
            print(f"  Profile: {profile.name}")
            print(f"  Quality: {'PASS' if not quality_warnings else f'{len(quality_warnings)} warnings'}")


if __name__ == "__main__":
    main()
