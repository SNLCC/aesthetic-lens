"""Tests for texture analysis module."""
import os
import tempfile
import cv2
import numpy as np
from .texture import analyze_texture


def test_analyze_texture_returns_expected_keys():
    img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_texture(f.name)
    os.unlink(f.name)

    assert isinstance(result, dict)
    assert "texture_complexity" in result
    assert "glcm_contrast" in result
    assert "surface_type" in result


def test_uniform_texture_low_complexity():
    img = np.full((200, 200, 3), 128, dtype=np.uint8)  # Flat gray
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_texture(f.name)
    os.unlink(f.name)

    assert result["texture_complexity"] < 0.3
