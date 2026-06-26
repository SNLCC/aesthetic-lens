"""Style & content-type classifier — translates CV measurements into
descriptive traits that the AI can use for tag naming.

⚠️  This module does NOT assign style names like "极简文艺" or "复古胶片".
It outputs **numerical/descriptive indicators** (e.g. "low_saturation",
"high_symmetry") that the AI interprets into free-form tags.

There are no preset labels anywhere in the pipeline.  Tags are always
assigned by the AI in ``tags.styles`` / ``tags.content_types``, and
``build_library()`` discovers them dynamically.
"""

from typing import Any, Dict, List


def _trait(val: float, low: float, high: float) -> str:
    if val <= low:
        return "low"
    if val >= high:
        return "high"
    return "mid"


def classify(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Return descriptive traits from CV data.

    Returns dict with keys:
        - ``traits``: dict of descriptive indicators (no preset label names)
        - ``confidence``: ``"high"`` | ``"medium"`` | ``"low"``
    """
    color = cv_data.get("color", {}) or {}
    composition = cv_data.get("composition", {}) or {}
    lighting = cv_data.get("lighting", {}) or {}
    spacing = cv_data.get("spacing", {}) or {}
    texture = cv_data.get("texture", {}) or {}

    sat = color.get("saturation_stats", {}) or {}
    lit = color.get("lightness_stats", {}) or {}
    mean_sat = sat.get("mean", 128)
    mean_lit = lit.get("mean", 128)
    sym = composition.get("symmetry_score", 0)
    neg = spacing.get("negative_space_ratio", 0)
    tex = texture.get("texture_complexity", 0)
    contrast = lighting.get("contrast", 0)

    traits: Dict[str, str] = {}

    # Color traits
    if mean_sat < 80:
        traits["saturation"] = "low"
    elif mean_sat > 140:
        traits["saturation"] = "high"
    else:
        traits["saturation"] = "mid"

    if mean_lit < 80:
        traits["lightness"] = "dark"
    elif mean_lit > 180:
        traits["lightness"] = "bright"
    else:
        traits["lightness"] = "mid"

    # Composition traits
    if sym > 0.65:
        traits["symmetry"] = "high"
    elif sym < 0.35:
        traits["symmetry"] = "low"
    else:
        traits["symmetry"] = "mid"

    traits["contrast"] = _trait(contrast, 0.25, 0.4)
    traits["negative_space"] = _trait(neg, 0.3, 0.5)
    traits["texture"] = _trait(tex, 0.3, 0.6)

    # Confidence based on how many traits are "mid" (boring/ambiguous) vs extreme
    extremes = sum(1 for v in traits.values() if v in ("low", "high"))
    if extremes >= 3:
        confidence = "high"
    elif extremes >= 1:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "traits": traits,
        "confidence": confidence,
    }
