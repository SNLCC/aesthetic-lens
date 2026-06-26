"""Tests for composition analysis module."""
import os
import tempfile
import cv2
import numpy as np
from .composition import analyze_composition


def create_symmetrical_image(width=400, height=400):
    """Create a horizontally symmetrical image."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    # Left half: white circle
    cv2.circle(img, (100, 200), 80, (255, 255, 255), -1)
    # Right half: mirrored white circle
    cv2.circle(img, (300, 200), 80, (255, 255, 255), -1)
    return img


def test_analyze_composition_returns_expected_keys():
    img = create_symmetrical_image()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_composition(f.name)
    os.unlink(f.name)

    assert isinstance(result, dict)
    assert "symmetry_score" in result
    assert "edge_density" in result
    assert "rule_of_thirds" in result
    assert "saliency_map_shape" in result


def test_symmetrical_image_high_symmetry():
    img = create_symmetrical_image()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_composition(f.name)
    os.unlink(f.name)

    assert result["symmetry_score"] > 0.5
