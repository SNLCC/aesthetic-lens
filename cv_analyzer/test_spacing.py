"""Tests for spacing analysis module."""
import os
import tempfile
import cv2
import numpy as np
from .spacing import analyze_spacing


def test_analyze_spacing_returns_expected_keys():
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_spacing(f.name)
    os.unlink(f.name)

    assert isinstance(result, dict)
    assert "negative_space_ratio" in result
    assert "content_distribution" in result


def test_mostly_empty_image_high_negative_space():
    """A mostly white image should have high negative space ratio."""
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    # Small content in center
    cv2.rectangle(img, (80, 80), (120, 120), (0, 0, 0), -1)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_spacing(f.name)
    os.unlink(f.name)

    assert result["negative_space_ratio"] > 0.5


def test_full_content_image_low_negative_space():
    """An image fully filled with content should have low negative space ratio."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    # Fill entire image with noise (content)
    img[:] = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_spacing(f.name)
    os.unlink(f.name)

    assert result["negative_space_ratio"] < 0.5


def test_content_distribution_has_grid():
    """The content distribution should include a 4x4 grid."""
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_spacing(f.name)
    os.unlink(f.name)

    dist = result["content_distribution"]
    assert "grid_4x4" in dist
    assert isinstance(dist["grid_4x4"], list)
    assert len(dist["grid_4x4"]) == 16
