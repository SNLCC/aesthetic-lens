"""Tests for the unified CV analysis entry point (analyze.py)."""

import os
import tempfile

import cv2
import numpy as np
import pytest

from .analyze import analyze, _get_image_metadata


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_synthetic_image(width=400, height=300, seed=42) -> np.ndarray:
    """Create a reproducible synthetic image with varied content."""
    rng = np.random.RandomState(seed)
    img = rng.randint(0, 255, (height, width, 3), dtype=np.uint8)
    # Add a few solid-colour blocks for deterministic patterns
    img[50:150, 50:150] = (20, 40, 200)   # red-ish block
    img[150:250, 200:350] = (200, 180, 40)  # blue-ish block
    return img


def _temp_image(img: np.ndarray, suffix=".png") -> str:
    """Write *img* to a temporary file and return its path.

    The caller is responsible for deleting the file.
    """
    f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    cv2.imwrite(f.name, img)
    return f.name


# ---------------------------------------------------------------------------
# Tests for _get_image_metadata
# ---------------------------------------------------------------------------

class TestGetImageMetadata:
    def test_returns_correct_dimensions(self):
        img = np.zeros((200, 300, 3), dtype=np.uint8)
        path = _temp_image(img)
        try:
            meta = _get_image_metadata(path)
        finally:
            os.unlink(path)

        assert meta is not None
        assert meta["width"] == 300
        assert meta["height"] == 200
        assert meta["channels"] == 3

    def test_returns_none_for_missing_file(self):
        assert _get_image_metadata("/nonexistent/path.png") is None

    def test_grayscale_image(self):
        img = np.zeros((100, 100), dtype=np.uint8)
        path = _temp_image(img)
        try:
            meta = _get_image_metadata(path)
        finally:
            os.unlink(path)

        assert meta is not None
        assert meta["channels"] == 1


# ---------------------------------------------------------------------------
# Tests for analyze()
# ---------------------------------------------------------------------------

class TestAnalyze:
    def test_successful_analysis_returns_all_sections(self):
        img = _make_synthetic_image()
        path = _temp_image(img)
        try:
            result = analyze(path)
        finally:
            os.unlink(path)

        assert result["status"] == "ok"
        assert "error" not in result

        # Metadata
        assert result["metadata"]["width"] == 400
        assert result["metadata"]["height"] == 300
        assert result["metadata"]["channels"] == 3

        # All 6 sub-modules present
        for key in ("color", "composition", "texture", "lighting", "spacing", "components"):
            assert key in result, f"Missing key: {key}"
            assert isinstance(result[key], dict), f"{key} should be a dict"

    def test_color_section_structure(self):
        img = _make_synthetic_image()
        path = _temp_image(img)
        try:
            result = analyze(path)
        finally:
            os.unlink(path)

        c = result["color"]
        assert "palette_bgr" in c
        assert "palette_hex_rgb" in c
        assert "palette_source" in c
        assert "saturation_stats" in c
        assert "lightness_stats" in c
        assert "scheme" in c

        for hex_c in c["palette_hex_rgb"]:
            assert hex_c.startswith("#")
            assert len(hex_c) == 7

    def test_composition_section_structure(self):
        img = _make_synthetic_image()
        path = _temp_image(img)
        try:
            result = analyze(path)
        finally:
            os.unlink(path)

        c = result["composition"]
        assert "symmetry_score" in c
        assert "edge_density" in c
        assert "rule_of_thirds" in c
        assert "layout_type" in c
        assert 0.0 <= c["symmetry_score"] <= 1.0

    def test_texture_section_structure(self):
        img = _make_synthetic_image()
        path = _temp_image(img)
        try:
            result = analyze(path)
        finally:
            os.unlink(path)

        t = result["texture"]
        assert "texture_complexity" in t
        assert "glcm_contrast" in t
        assert "surface_type" in t
        assert 0.0 <= t["texture_complexity"] <= 1.0

    def test_lighting_section_structure(self):
        img = _make_synthetic_image()
        path = _temp_image(img)
        try:
            result = analyze(path)
        finally:
            os.unlink(path)

        l = result["lighting"]
        assert "brightness_stats" in l
        assert "contrast" in l
        assert "histogram" in l
        assert "light_source" in l
        assert "light_quality" in l
        assert isinstance(l["histogram"], list)
        assert len(l["histogram"]) == 256

    def test_spacing_section_structure(self):
        img = _make_synthetic_image()
        path = _temp_image(img)
        try:
            result = analyze(path)
        finally:
            os.unlink(path)

        s = result["spacing"]
        assert "negative_space_ratio" in s
        assert "content_pixel_ratio" in s
        assert "content_distribution" in s
        assert "spacing_principle" in s
        assert 0.0 <= s["negative_space_ratio"] <= 1.0

    def test_components_section_structure(self):
        img = _make_synthetic_image()
        path = _temp_image(img)
        try:
            result = analyze(path)
        finally:
            os.unlink(path)

        c = result["components"]
        assert "roi_segments" in c
        assert "horizontal_slices" in c
        assert "component_roles" in c
        assert isinstance(c["roi_segments"], list)
        assert isinstance(c["horizontal_slices"], list)

    def test_error_on_nonexistent_file(self):
        result = analyze("/this/does/not/exist.jpg")
        assert result["status"] == "error"
        assert "error" in result
        assert "Cannot read image" in result["error"]

    def test_sub_module_error_is_isolated(self, monkeypatch):
        """If one sub-module raises, the others still produce results."""
        import sys as _sys

        # cv_analyzer.analyze is shadowed by the analyze() function in the
        # package namespace, so we access the real module via sys.modules.
        _analyze_mod = _sys.modules["cv_analyzer.analyze"]

        def _broken_color(*args, **kwargs):
            raise RuntimeError("color module crash")

        monkeypatch.setattr(_analyze_mod, "analyze_color", _broken_color)

        img = _make_synthetic_image()
        path = _temp_image(img)
        try:
            result = analyze(path)
        finally:
            os.unlink(path)

        assert result["status"] == "ok"
        assert "error" in result["color"]
        assert "color module crash" in result["color"]["error"]

        # Other modules should still be healthy
        for key in ("composition", "texture", "lighting", "spacing", "components"):
            assert key in result
            assert "error" not in result[key], f"{key} should not have error"

    def test_uniform_image_produces_stable_results(self):
        """A completely uniform image should still produce valid output."""
        img = np.full((200, 200, 3), 128, dtype=np.uint8)
        path = _temp_image(img)
        try:
            result = analyze(path)
        finally:
            os.unlink(path)

        assert result["status"] == "ok"
        # All sections present
        for key in ("color", "composition", "texture", "lighting", "spacing", "components"):
            assert key in result

    def test_different_image_formats(self):
        """Test with PNG and JPEG formats."""
        img = _make_synthetic_image()
        formats = [(".png", cv2.IMREAD_COLOR), (".jpg", cv2.IMREAD_COLOR)]
        for suffix, _ in formats:
            path = _temp_image(img, suffix=suffix)
            try:
                result = analyze(path)
                assert result["status"] == "ok"
            finally:
                os.unlink(path)

