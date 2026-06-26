"""Tests for lighting analysis module."""
import os
import tempfile
import cv2
import numpy as np
from .lighting import analyze_lighting


def test_analyze_lighting_returns_expected_keys():
    img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_lighting(f.name)
    os.unlink(f.name)

    assert isinstance(result, dict)
    assert "histogram" in result
    assert "brightness_stats" in result
    assert "contrast" in result


def test_high_contrast_image():
    """An image with both very bright and very dark regions."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[0:100, :] = [255, 255, 255]  # Top half white
    # Bottom half stays black
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_lighting(f.name)
    os.unlink(f.name)

    assert result["contrast"] >= 0.5
