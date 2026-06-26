"""Unified CV analysis entry point — aggregates all 6 analysis modules.

Runs color, composition, texture, lighting, spacing, and component analysis
on a single image and returns a consolidated result dict.
"""

from typing import Any, Dict, Optional

from ._utils import imread_unchanged
from .classify import classify
from .color import analyze_color
from .components import analyze_components
from .composition import analyze_composition
from .lighting import analyze_lighting
from .spacing import analyze_spacing
from .texture import analyze_texture


def _get_image_metadata(image_path: str) -> Optional[Dict[str, Any]]:
    """Read basic image metadata (width, height, channels) from disk.

    Returns None if the image cannot be read.
    """
    image = imread_unchanged(image_path)
    if image is None:
        return None
    height, width = image.shape[:2]
    channels = image.shape[2] if len(image.shape) > 2 else 1
    return {
        "width": width,
        "height": height,
        "channels": channels,
    }


def analyze(image_path: str) -> Dict[str, Any]:
    """Run all 6 CV analyses on an image and return a unified result.

    The returned dict has:
        - ``status``: ``"ok"``, ``"degraded"``, or ``"error"``
        - ``error``: error message (only present when status is ``"error"``)
        - ``degraded_modules``: list of failed module names (only when ``"degraded"``)
        - ``ai_fills_required``: list of fields the downstream AI should populate
        - ``cv_classification``: first-pass style/content-type guess (see ``classify.py``)
        - ``metadata``: dict with *width*, *height*, *channels*
        - top-level keys from each sub-analysis:
            *color*, *composition*, *texture*, *lighting*, *spacing*, *components*

    If a sub-analysis fails, its value is a dict with a single ``"error"`` key
    rather than crashing the whole call.  The top-level ``status`` is still
    ``"ok"`` as long as at least one sub-analysis succeeded; only when the
    image itself cannot be read does ``status`` become ``"error"``.

    Parameters
    ----------
    image_path : str
        Path to the image file (supported formats: JPEG, PNG, TIFF, WebP, …).

    Returns
    -------
    Dict[str, Any]
        Consolidated analysis results.
    """
    metadata = _get_image_metadata(image_path)
    if metadata is None:
        return {
            "status": "error",
            "error": f"Cannot read image: {image_path}",
        }

    analyses: Dict[str, Any] = {
        "metadata": metadata,
    }

    # Run each sub-analysis, catching failures per-module
    modules = [
        ("color", analyze_color),
        ("composition", analyze_composition),
        ("texture", analyze_texture),
        ("lighting", analyze_lighting),
        ("spacing", analyze_spacing),
        ("components", analyze_components),
    ]

    for name, func in modules:
        try:
            analyses[name] = func(image_path)
        except Exception as exc:
            analyses[name] = {"error": str(exc)}

    # First-pass classification from CV data alone
    analyses["cv_classification"] = classify(analyses)

    # Determine overall status
    any_ok = any(
        isinstance(v, dict) and "error" not in v
        for v in analyses.values()
        if isinstance(v, dict)
    )
    analyses["status"] = "ok" if any_ok else "degraded"
    if not any_ok:
        failed = [k for k, v in analyses.items() if isinstance(v, dict) and "error" in v]
        analyses["degraded_modules"] = failed

    # Expose AI-fill-required fields so downstream can discover them
    analyses["ai_fills_required"] = [
        "color.scheme",
        "composition.layout_type",
        "texture.surface_type",
        "lighting.light_quality",
        "spacing.spacing_principle",
        "components.component_roles",
        # Typography (LLM vision only, no CV pre-processing)
        "typography.hierarchy",
        "typography.line_spacing",
        "typography.text_density",
        "typography.alignment",
        "typography.font_style",
    ]
    return analyses
