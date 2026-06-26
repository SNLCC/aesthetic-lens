"""pipeline — one-shot e2e entry: CV analysis + AI interpretation → L1 JSON.

Usage::

    from cv_analyzer.pipeline import assemble_l1

    path = assemble_l1(
        image_path="test.jpg",
        ai_interpretation={"color_scheme": "monochrome", ...},
        tags={"styles": ["暗黑文学风"]},
    )
"""

from typing import Any, Dict, List, Optional

from .analyze import analyze
from .write_raw import write_raw


def assemble_l1(
    image_path: str,
    ai_interpretation: Optional[Dict[str, Any]] = None,
    tags: Optional[Dict[str, List[str]]] = None,
    run_cv: bool = True,
    cv_data: Optional[Dict[str, Any]] = None,
    mode: str = "upsert",
) -> str:
    """One-shot: run CV (optionally), merge with AI fills, write L1.

    Parameters
    ----------
    image_path : str
        Path to the image file.
    ai_interpretation : dict or None
        AI_FILLS fields.  If absent, L1 is marked ``incomplete: true``.
    tags : dict or None
        e.g. ``{"styles": ["极简"], "content_types": ["教程"]}``.
    run_cv : bool
        If True, run ``cv_analyzer.analyze()``.
        If False, *cv_data* must be provided.
    cv_data : dict or None
        Pre-computed CV data.  Used when ``run_cv=False``.
    mode : str
        Passed to ``write_raw()``.  ``"upsert"`` by default so re-runs
        on the same image overwrite instead of piling up duplicate L1s.

    Returns
    -------
    str
        Absolute path to the written L1 JSON file.
    """
    if run_cv:
        cv_data = analyze(image_path)
    elif cv_data is None:
        raise ValueError("run_cv=False requires cv_data to be provided")

    return write_raw(
        image_path=image_path,
        cv_data=cv_data,
        ai_interpretation=ai_interpretation,
        tags=tags,
        mode=mode,
    )
