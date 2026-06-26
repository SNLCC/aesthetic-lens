"""Component structure analysis — region segmentation, layout detection.

Uses: OpenCV contour detection, horizontal/vertical projection.
All dependencies BSD/MIT licensed.
"""

from typing import Dict, List

import cv2
import numpy as np

from ._utils import imread_color


def _detect_horizontal_slices(image: np.ndarray, n_slices: int = 5) -> List[Dict]:
    """Detect horizontal regions by analyzing row-wise brightness variance."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    slice_h = h // n_slices

    slices = []
    for i in range(n_slices):
        y0 = i * slice_h
        y1 = (i + 1) * slice_h if i < n_slices - 1 else h
        region = gray[y0:y1, :]
        slices.append({
            "y_start": y0,
            "y_end": y1,
            "mean_brightness": float(np.mean(region)),
            "brightness_std": float(np.std(region)),
            "edge_density": float(np.count_nonzero(cv2.Canny(region, 50, 150)) / max(region.size, 1)),
        })

    return slices


def _detect_contour_regions(image: np.ndarray) -> List[Dict]:
    """Detect distinct content regions via contour analysis."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Threshold to find content blobs
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Invert if background is white
    if np.mean(thresh) > 127:
        thresh = cv2.bitwise_not(thresh)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    h, w = gray.shape
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        area_ratio = (cw * ch) / (h * w)
        if area_ratio > 0.01:  # Filter out tiny noise
            regions.append({
                "x": int(x),
                "y": int(y),
                "width": int(cw),
                "height": int(ch),
                "area_ratio": float(area_ratio),
                "aspect_ratio": float(cw / max(ch, 1)),
            })

    return sorted(regions, key=lambda r: r["area_ratio"], reverse=True)


def analyze_components(image_path: str) -> Dict:
    """Analyze component structure of an image.

    Returns dict with:
        - roi_segments: List of detected contour regions
        - horizontal_slices: List of horizontal region analyses
        - component_roles: List[str] (AI_FILLS)
    """
    image = imread_color(image_path)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")

    h_slices = _detect_horizontal_slices(image)
    contours = _detect_contour_regions(image)

    return {
        "roi_segments": contours,
        "horizontal_slices": h_slices,
        "component_roles": [],  # AI_FILLS: e.g. hero, background, decor, frame, texture
    }
