"""Tests for component structure analysis module."""
import os
import tempfile
import cv2
import numpy as np
from .components import analyze_components


def test_analyze_components_returns_expected_keys():
    img = np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_components(f.name)
    os.unlink(f.name)

    assert isinstance(result, dict)
    assert "roi_segments" in result
    assert "horizontal_slices" in result


def test_horizontal_regions_detected():
    """Image with clear top/bottom regions."""
    img = np.zeros((300, 400, 3), dtype=np.uint8)
    img[0:100, :] = [200, 200, 200]  # Top: light
    img[100:200, :] = [100, 100, 100]  # Middle: mid
    img[200:300, :] = [30, 30, 30]  # Bottom: dark
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_components(f.name)
    os.unlink(f.name)

    assert len(result["horizontal_slices"]) >= 2


def test_roi_segments_contains_regions():
    """Image with distinct shapes should produce contour regions."""
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255  # White background
    # Draw a dark rectangle
    img[50:150, 50:150] = [30, 30, 30]
    # Draw another dark rectangle
    img[180:250, 200:350] = [50, 50, 50]
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_components(f.name)
    os.unlink(f.name)

    assert len(result["roi_segments"]) >= 1
    for seg in result["roi_segments"]:
        assert "x" in seg
        assert "y" in seg
        assert "width" in seg
        assert "height" in seg
        assert "area_ratio" in seg
        assert "aspect_ratio" in seg


def test_component_roles_is_list():
    """component_roles should be a list (placeholder for AI fill)."""
    img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        result = analyze_components(f.name)
    os.unlink(f.name)

    assert isinstance(result["component_roles"], list)
    assert len(result["component_roles"]) == 0


def test_analyze_components_raises_on_missing_file():
    """Should raise ValueError for non-existent path."""
    try:
        analyze_components("/nonexistent/image.png")
        assert False, "Expected ValueError"
    except ValueError:
        pass
