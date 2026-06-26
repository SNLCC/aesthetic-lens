"""Texture analysis — LBP, GLCM contrast, surface type classification.

Uses: scikit-image for LBP and GLCM, OpenCV for preprocessing.
All dependencies BSD/MIT licensed.
"""

from typing import Dict

import cv2
import numpy as np
from skimage.feature import local_binary_pattern, graycomatrix, graycoprops

from ._utils import imread_color


def _compute_lbp_complexity(gray: np.ndarray) -> float:
    """Compute texture complexity using Local Binary Pattern entropy."""
    radius = 3
    n_points = 8 * radius
    lbp = local_binary_pattern(gray, n_points, radius, method="uniform")
    # Entropy as complexity measure
    hist, _ = np.histogram(lbp, bins=n_points + 2, range=(0, n_points + 2), density=True)
    hist = hist[hist > 0]
    entropy = -np.sum(hist * np.log2(hist))
    # Normalize to 0-1
    max_entropy = np.log2(n_points + 2)
    return float(min(entropy / max_entropy, 1.0))


def _compute_glcm_contrast(gray: np.ndarray) -> float:
    """Compute GLCM contrast as a texture complexity indicator."""
    # Quantize to 16 levels for speed
    gray_q = (gray / 16).astype(np.uint8)
    glcm = graycomatrix(gray_q, distances=[1], angles=[0], levels=16, symmetric=True, normed=True)
    contrast = graycoprops(glcm, "contrast")[0, 0]
    return float(contrast)


def analyze_texture(image_path: str) -> Dict:
    """Analyze texture properties of an image.

    Returns dict with:
        - texture_complexity: float (0-1)
        - glcm_contrast: float
        - surface_type: str (AI_FILLS)
    """
    image = imread_color(image_path)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    lbp_entropy = _compute_lbp_complexity(gray)
    glcm_contrast = _compute_glcm_contrast(gray)

    return {
        "texture_complexity": lbp_entropy,
        "glcm_contrast": glcm_contrast,
        "surface_type": "",  # AI_FILLS: e.g. smooth, rough, patterned, grainy
    }
