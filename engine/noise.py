"""
Value noise and fractal noise for procedural terrain generation.
Pure Python, deterministic via seed, no external dependencies.
"""

import math
import random


def _hash_2d(x: int, y: int, seed: int) -> float:
    """Deterministic pseudo-random value for grid point (x, y)."""
    n = x + y * 57 + seed * 131
    n = (n << 13) ^ n
    return 1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7FFFFFFF) / 1073741824.0


def _lerp(a: float, b: float, t: float) -> float:
    return a + t * (b - a)


def _smooth(t: float) -> float:
    """Smoothstep interpolation."""
    return t * t * (3 - 2 * t)


def value_noise_2d(x: float, y: float, seed: int = 42, scale: float = 1.0) -> float:
    """2D value noise returning a value in [-1, 1].

    Args:
        x, y: World coordinates.
        seed: Deterministic seed.
        scale: Noise frequency (smaller = larger features).
    """
    x_scaled = x * scale
    y_scaled = y * scale

    xi = int(math.floor(x_scaled))
    yi = int(math.floor(y_scaled))

    xf = x_scaled - xi
    yf = y_scaled - yi

    xf = _smooth(xf)
    yf = _smooth(yf)

    v00 = _hash_2d(xi, yi, seed)
    v10 = _hash_2d(xi + 1, yi, seed)
    v01 = _hash_2d(xi, yi + 1, seed)
    v11 = _hash_2d(xi + 1, yi + 1, seed)

    ix0 = _lerp(v00, v10, xf)
    ix1 = _lerp(v01, v11, xf)

    return _lerp(ix0, ix1, yf)


def fractal_noise(x: float, y: float, seed: int = 42, octaves: int = 3,
                  persistence: float = 0.5, base_scale: float = 0.2) -> float:
    """Layered fractal noise combining multiple octaves.

    Returns value roughly in [-1, 1] (amplitude-normalized).
    """
    total = 0.0
    amplitude = 1.0
    max_amplitude = 0.0
    scale = base_scale

    for _ in range(octaves):
        total += value_noise_2d(x, y, seed, scale) * amplitude
        max_amplitude += amplitude
        amplitude *= persistence
        scale *= 2.0
        seed += 1

    return total / max_amplitude if max_amplitude > 0 else 0.0


def noise_map(width: int, height: int, seed: int = 42, octaves: int = 3,
              persistence: float = 0.5, base_scale: float = 0.2) -> list[list[float]]:
    """Generate a 2D noise map normalized to [0, 1]."""
    raw = []
    min_v, max_v = float("inf"), float("-inf")
    for y in range(height):
        row = []
        for x in range(width):
            v = fractal_noise(x, y, seed, octaves, persistence, base_scale)
            row.append(v)
            min_v = min(min_v, v)
            max_v = max(max_v, v)
        raw.append(row)

    # Normalize to [0, 1]
    range_v = max_v - min_v if max_v > min_v else 1.0
    return [[(v - min_v) / range_v for v in row] for row in raw]
