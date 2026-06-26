"""Aesthetic Lens — CV-based image aesthetic analysis.

All dependencies are BSD/MIT/PSF licensed (commercially safe).
Measurements output structured dicts consumed by Reasonix AI interpretation.
"""

from .ai_fills_schema import validate_ai_fills, ai_fills_blank
from .analyze import analyze
from .build_library import build
from .classify import classify
from .color import analyze_color
from .components import analyze_components
from .composition import analyze_composition
from .lighting import analyze_lighting
from .spacing import analyze_spacing
from .texture import analyze_texture
from .pipeline import assemble_l1
from .write_raw import write_raw, find_l1_by_source, get_library_dir

__all__ = [
    "ai_fills_blank",
    "analyze",
    "analyze_color",
    "analyze_components",
    "analyze_composition",
    "analyze_lighting",
    "analyze_spacing",
    "analyze_texture",
    "assemble_l1",
    "build",
    "classify",
    "find_l1_by_source",
    "get_library_dir",
    "validate_ai_fills",
    "write_raw",
]
