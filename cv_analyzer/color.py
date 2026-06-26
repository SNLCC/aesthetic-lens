"""Color analysis — extract palette, dominant colors, saturation/lightness stats.

Uses: OpenCV (K-Means clustering), ColorThief for palette extraction.
All dependencies BSD/MIT licensed.
"""

from typing import Dict, List, Tuple

import cv2
import numpy as np
from colorthief import ColorThief

from ._utils import imread_color


def _bgr_to_hex(bgr: Tuple[int, int, int]) -> str:
    """Convert OpenCV BGR tuple to hex string."""
    r, g, b = int(bgr[2]), int(bgr[1]), int(bgr[0])
    return f"#{r:02x}{g:02x}{b:02x}"


def _extract_palette_kmeans(image: np.ndarray, n_colors: int = 5) -> List[Tuple[int, int, int]]:
    """Extract dominant colors using K-Means clustering (BGR tuples)."""
    pixels = image.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = centers.astype(int)
    # Sort by frequency (most dominant first)
    counts = np.bincount(labels.flatten())
    sorted_indices = np.argsort(-counts)
    return [tuple(centers[i]) for i in sorted_indices]


def _compute_saturation_lightness(image: np.ndarray) -> Dict:
    """Compute saturation and lightness statistics in HSL space.

    ⚠️ HLS saturation is unreliable when lightness is near 0 (pure black)
    or 255 (pure white) — these edge values can produce misleading stats.
    For very dark images, rely more on contrast/brightness from lighting.py.
    """
    hls = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    saturation = hls[:, :, 2].flatten()
    lightness = hls[:, :, 1].flatten()

    return {
        "mean_saturation": float(np.mean(saturation)),
        "std_saturation": float(np.std(saturation)),
        "mean_lightness": float(np.mean(lightness)),
        "std_lightness": float(np.std(lightness)),
        "saturation_range": [int(np.min(saturation)), int(np.max(saturation))],
        "lightness_range": [int(np.min(lightness)), int(np.max(lightness))],
    }


def analyze_color(image_path: str) -> Dict:
    """Analyze color composition of an image.

    Returns dict with:
        - palette_bgr: List of BGR tuples (K-Means, 5 dominant colors)
        - palette_hex_rgb: List of RGB hex strings (ColorThief or K-Means fallback)
        - palette_source: ``"colorthief"`` or ``"kmeans"``
        - scheme: Inferred color scheme type (AI_FILLS)
        - saturation_stats: Saturation statistics in HSL space
        - lightness_stats: Lightness statistics in HSL space
    """
    image = imread_color(image_path)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")

    # Palette via K-Means
    palette_bgr = _extract_palette_kmeans(image, n_colors=5)

    # Palette via ColorThief for complementary extraction
    palette_rgb_hex = []
    ct_success = False
    try:
        ct = ColorThief(image_path)
        palette_rgb = ct.get_palette(color_count=5, quality=10)
        palette_rgb_hex = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in palette_rgb]
        ct_success = True
    except Exception:
        # Fallback to K-Means hex
        palette_rgb_hex = [_bgr_to_hex(c) for c in palette_bgr]

    # HSL stats
    stats = _compute_saturation_lightness(image)

    return {
        "palette_bgr": [tuple(int(c) for c in color) for color in palette_bgr],  # K-Means, BGR
        "palette_hex_rgb": palette_rgb_hex,  # ColorThief (or K-Means fallback), RGB hex
        "palette_source": "colorthief" if ct_success else "kmeans",
        "scheme": "",  # AI_FILLS: e.g. complementary, analogous, monochrome, triadic
        "saturation_stats": {
            "mean": stats["mean_saturation"],
            "std": stats["std_saturation"],
            "range": stats["saturation_range"],
        },
        "lightness_stats": {
            "mean": stats["mean_lightness"],
            "std": stats["std_lightness"],
            "lightness_range": stats["lightness_range"],
        },
    }
