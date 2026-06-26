"""Lighting analysis — brightness distribution, contrast, histogram features.

Uses: OpenCV histogram analysis and brightness statistics.
All dependencies BSD/MIT licensed.
"""

from typing import Dict, List

import cv2
import numpy as np

from ._utils import imread_color


def _compute_brightness_stats(gray: np.ndarray) -> Dict:
    """Compute brightness statistics from grayscale image."""
    brightness = gray.flatten()
    return {
        "mean": float(np.mean(brightness)),
        "std": float(np.std(brightness)),
        "median": float(np.median(brightness)),
        "min": int(np.min(brightness)),
        "max": int(np.max(brightness)),
    }


def _compute_contrast(gray: np.ndarray) -> float:
    """Compute RMS contrast (standard deviation of normalized pixel intensities)."""
    normalized = gray / 255.0
    return float(np.std(normalized))


def _compute_histogram(gray: np.ndarray) -> List[int]:
    """Compute 256-bin histogram."""
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    return [int(h) for h in hist.flatten()]


def _estimate_light_source(gray: np.ndarray) -> Dict:
    """Estimate light source direction based on brightness gradient."""
    h, w = gray.shape
    # Divide into quadrants and compare brightness
    quadrants = {
        "top_left": np.mean(gray[0:h//2, 0:w//2]),
        "top_right": np.mean(gray[0:h//2, w//2:w]),
        "bottom_left": np.mean(gray[h//2:h, 0:w//2]),
        "bottom_right": np.mean(gray[h//2:h, w//2:w]),
    }
    brightest = max(quadrants, key=quadrants.get)
    return {
        "brightest_quadrant": brightest,
        "quadrant_means": quadrants,
    }


def analyze_lighting(image_path: str) -> Dict:
    """Analyze lighting properties of an image.

    Returns dict with:
        - brightness_stats: mean, std, median, min, max
        - contrast: float (RMS contrast)
        - histogram: List[int] (256-bin)
        - light_source: dict with brightest quadrant estimate
        - light_quality: str (AI_FILLS)
    """
    image = imread_color(image_path)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return {
        "brightness_stats": _compute_brightness_stats(gray),
        "contrast": _compute_contrast(gray),
        "histogram": _compute_histogram(gray),
        "light_source": _estimate_light_source(gray),
        "light_quality": "",  # AI_FILLS: e.g. soft, harsh, golden-hour, flat, dramatic
    }
