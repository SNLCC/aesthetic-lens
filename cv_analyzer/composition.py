"""Composition analysis — symmetry, edge density, rule-of-thirds, saliency.

Uses: OpenCV edge detection, saliency, and image processing.
All dependencies BSD/MIT licensed.
"""

from typing import Dict

import cv2
import numpy as np

from ._utils import imread_color


def _compute_symmetry(image: np.ndarray) -> float:
    """Compute horizontal symmetry score (0.0 = asymmetric, 1.0 = perfectly symmetric)."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    mid = w // 2

    left = gray[:, :mid]
    right = gray[:, mid:mid + left.shape[1]]  # Mirror by width
    right_flipped = cv2.flip(right, 1)

    # Resize if different widths
    if left.shape[1] != right_flipped.shape[1]:
        min_w = min(left.shape[1], right_flipped.shape[1])
        left = left[:, :min_w]
        right_flipped = right_flipped[:, :min_w]

    diff = cv2.absdiff(left, right_flipped)
    score = 1.0 - (np.mean(diff) / 255.0)
    return float(score)


def _compute_edge_density(image: np.ndarray) -> Dict:
    """Compute edge density and distribution."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    total_pixels = edges.shape[0] * edges.shape[1]
    edge_pixels = np.count_nonzero(edges)

    # Divide into 3x3 grid for rule-of-thirds analysis
    h, w = edges.shape
    grid = []
    for row in range(3):
        for col in range(3):
            y0, y1 = row * h // 3, (row + 1) * h // 3
            x0, x1 = col * w // 3, (col + 1) * w // 3
            cell_edges = np.count_nonzero(edges[y0:y1, x0:x1])
            grid.append(float(cell_edges / max(edge_pixels, 1)))

    return {
        "density": float(edge_pixels / max(total_pixels, 1)),
        "rule_of_thirds_grid": grid,
    }


def _compute_saliency(image: np.ndarray) -> Dict:
    """Compute static saliency using OpenCV's saliency detector."""
    saliency = cv2.saliency.StaticSaliencyFineGrained_create()
    (success, saliency_map) = saliency.computeSaliency(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    if not success:
        return {"has_saliency": False, "mean": 0.0, "std": 0.0}

    return {
        "has_saliency": True,
        "mean": float(np.mean(saliency_map)),
        "std": float(np.std(saliency_map)),
        "shape": list(saliency_map.shape),
    }


def analyze_composition(image_path: str) -> Dict:
    """Analyze composition of an image.

    Returns dict with:
        - symmetry_score: float (0-1)
        - edge_density: float
        - rule_of_thirds: 3x3 grid edge distribution
        - saliency_map_shape: [height, width] or None
        - layout_type: str (AI_FILLS)
    """
    image = imread_color(image_path)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")

    symmetry = _compute_symmetry(image)
    edge_data = _compute_edge_density(image)
    saliency = _compute_saliency(image)

    return {
        "symmetry_score": symmetry,
        "edge_density": edge_data["density"],
        "rule_of_thirds": edge_data["rule_of_thirds_grid"],
        "saliency_map_shape": saliency.get("shape"),
        "layout_type": "",  # AI_FILLS: e.g. centered, rule-of-thirds, diagonal, asymmetric
    }
