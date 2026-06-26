"""Schema for AI aesthetic interpretation (AI_FILLS).

Defines valid values, optional fields, and validation logic for the
11 AI_FILLS fields that the LLM must populate.

Usage::

    from cv_analyzer.ai_fills_schema import validate_ai_fills
    valid = validate_ai_fills({
        "color_scheme": "complementary",
        "composition_layout_type": "centered",
        ...
    })
"""

from typing import Any, Dict, List, Literal, Optional, get_args

# ------------------------------------------------------------------
# allowed values per field
# ------------------------------------------------------------------
COLOR_SCHEMES = {"complementary", "analogous", "monochrome", "triadic"}
LAYOUT_TYPES = {"centered", "rule-of-thirds", "diagonal", "asymmetric"}
SURFACE_TYPES = {"smooth", "rough", "patterned", "grainy"}
LIGHT_QUALITIES = {"soft", "harsh", "golden-hour", "flat", "dramatic"}
SPACING_PRINCIPLES = {"breathing", "dense", "balanced", "spacious"}
HIERARCHIES = {"3-level", "2-level", "uniform", "complex"}
LINE_SPACINGS = {"tight", "medium", "loose"}
TEXT_DENSITIES = {"sparse", "medium", "dense"}
ALIGNMENTS = {"left", "center", "right", "justified", "mixed"}
FONT_STYLES = {"serif", "sans-serif", "hand-drawn", "mixed", "monospace"}
CONFIDENCE_LEVELS = {"high", "medium", "low"}

# Field -> set of allowed values (None = free text)
SCHEMA: Dict[str, Optional[set]] = {
    "color_scheme": COLOR_SCHEMES,
    "composition_layout_type": LAYOUT_TYPES,
    "texture_surface_type": SURFACE_TYPES,
    "lighting_light_quality": LIGHT_QUALITIES,
    "spacing_spacing_principle": SPACING_PRINCIPLES,
    "components_component_roles": None,  # free-form list
    "typography_hierarchy": HIERARCHIES,
    "typography_line_spacing": LINE_SPACINGS,
    "typography_text_density": TEXT_DENSITIES,
    "typography_alignment": ALIGNMENTS,
    "typography_font_style": FONT_STYLES,
}

REQUIRED_AI_KEYS = list(SCHEMA.keys())

# optional meta fields
META_KEYS = {
    "ai_confidence": dict,       # {"color_scheme": "high", ...}
    "ai_method": str,            # "llm_vision" | "cv_heuristic" | "hybrid"
    "ai_visual_access": bool,
    "ai_visual_access_note": str,
    "ai_filler_model": str,      # e.g. "claude-opus-4-5"
}


def validate_ai_fills(
    data: Dict[str, Any],
    strict: bool = False,
) -> Dict[str, Any]:
    """Validate AI interpretation data.

    Parameters
    ----------
    data : dict
        AI_FILLS fields (flat, e.g. ``{"color_scheme": "monochrome", ...}``).
    strict : bool
        If True, raise ValueError on invalid values.
        If False (default), return a ``_warnings`` list instead.

    Returns
    -------
    dict
        Same as input, with ``_warnings`` appended if ``strict=False``.
    """
    warnings: List[str] = []

    for key, allowed in SCHEMA.items():
        if key not in data:
            continue
        val = data[key]
        if allowed is not None and val not in allowed and val:
            msg = (
                f"{key}='{val}' not in {sorted(allowed)}"
            )
            warnings.append(msg)
            if strict:
                raise ValueError(msg)

    if warnings:
        data["_warnings"] = warnings
    return data


def ai_fills_blank(ai_method: str = "llm_vision") -> Dict[str, Any]:
    """Return a blank AI_FILLS template with meta fields."""
    template: Dict[str, Any] = {k: "" for k in SCHEMA}
    template["components_component_roles"] = []
    template["ai_method"] = ai_method
    template["ai_visual_access"] = True
    template["ai_confidence"] = {}
    return template
