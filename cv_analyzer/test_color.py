"""Tests for color analysis module."""
import os
import tempfile
import cv2
import numpy as np
from .color import analyze_color


def create_test_image(width=400, height=400):
    """Create a simple test image with known color blocks."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    # Red block top-left
    img[0:200, 0:200] = [0, 0, 200]  # BGR
    # Green block top-right
    img[0:200, 200:400] = [0, 200, 0]
    # Blue block bottom
    img[200:400, :] = [200, 0, 0]
    return img


def test_analyze_color_returns_expected_keys():
    img = create_test_image()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_color(f.name)
    os.unlink(f.name)

    assert isinstance(result, dict)
    assert "palette_bgr" in result
    assert "palette_hex_rgb" in result
    assert "palette_source" in result
    assert "scheme" in result
    assert "saturation_stats" in result
    assert "lightness_stats" in result


def test_palette_has_3_to_5_colors():
    img = create_test_image()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_color(f.name)
    os.unlink(f.name)

    assert 3 <= len(result["palette_bgr"]) <= 5
    for color in result["palette_bgr"]:
        assert len(color) == 3  # BGR tuple


def test_dominant_colors_are_hex_strings():
    img = create_test_image()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_color(f.name)
    os.unlink(f.name)

    assert len(result["palette_hex_rgb"]) == 5
    for hex_color in result["palette_hex_rgb"]:
        assert hex_color.startswith("#")
        assert len(hex_color) == 7
