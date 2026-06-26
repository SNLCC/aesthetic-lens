"""Spacing analysis — negative space, content density, breathing room.

Uses: OpenCV edge detection and content density estimation.
All dependencies BSD/MIT licensed.
"""

from typing import Dict, List

import cv2
import numpy as np

from ._utils import imread_color


def _compute_negative_space(image: np.ndarray) -> Dict:
    """Compute negative space ratio and distribution."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Edge detection to find content boundaries
    edges = cv2.Canny(gray, 30, 100)
    # Dilate edges to connect nearby content
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)
    # Content pixels = dilated edge pixels
    total_pixels = dilated.shape[0] * dilated.shape[1]
    content_pixels = np.count_nonzero(dilated)
    negative_ratio = 1.0 - (content_pixels / max(total_pixels, 1))

    return {
        "negative_space_ratio": float(negative_ratio),
        "content_pixel_ratio": float(content_pixels / max(total_pixels, 1)),
    }


def _content_distribution(image: np.ndarray) -> Dict:
    """Analyze how content is distributed across the image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 30, 100)

    h, w = edges.shape
    # Divide into 4x4 grid to measure content distribution
    grid_values = []
    for row in range(4):
        for col in range(4):
            y0, y1 = row * h // 4, (row + 1) * h // 4
            x0, x1 = col * w // 4, (col + 1) * w // 4
            density = float(np.count_nonzero(edges[y0:y1, x0:x1]) / max((y1 - y0) * (x1 - x0), 1))
            grid_values.append(density)

    return {
        "grid_4x4": grid_values,
        "concentration_center": float(np.mean(grid_values[5:11])),  # Center 6 cells
        "concentration_edges": float(
            (grid_values[0] + grid_values[3] + grid_values[12] + grid_values[15]) / 4
        ),
    }


def analyze_spacing(image_path: str) -> Dict:
    """Analyze spacing and negative space of an image.

    Returns dict with:
        - negative_space_ratio: float (0-1)
        - content_pixel_ratio: float
        - content_distribution: dict with 4x4 grid
        - spacing_principle: str (AI_FILLS)
    """
    image = imread_color(image_path)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")

    space = _compute_negative_space(image)
    dist = _content_distribution(image)

    return {
        "negative_space_ratio": space["negative_space_ratio"],
        "content_pixel_ratio": space["content_pixel_ratio"],
        "content_distribution": dist,
        "spacing_principle": "",  # AI_FILLS: e.g. breathing, dense, balanced, spacious
    }
