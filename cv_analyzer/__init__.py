"""Aesthetic Lens — CV-based image aesthetic analysis.

All dependencies are BSD/MIT/PSF licensed (commercially safe).
Measurements output structured dicts consumed by Reasonix AI interpretation.
"""

from .analyze import analyze
from .build_library import build
from .classify import classify
from .color import analyze_color
from .components import analyze_components
from .composition import analyze_composition
from .lighting import analyze_lighting
from .spacing import analyze_spacing
from .texture import analyze_texture
from .write_raw import write_raw, get_library_dir

__all__ = [
    "analyze",
    "analyze_color",
    "analyze_components",
    "analyze_composition",
    "analyze_lighting",
    "analyze_spacing",
    "analyze_texture",
    "build",
    "classify",
    "get_library_dir",
    "write_raw",
]
