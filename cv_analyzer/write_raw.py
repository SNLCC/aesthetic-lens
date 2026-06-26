"""L1 Raw profile writer — merges CV measurements + AI interpretation into a
persistent L1 JSON file under a platform-appropriate data directory.

**Data location (inside the skill directory, follows install location):**

- Development: ``aesthetic-lens/library/raw/``
- Project install: ``.reasonix/skills/aesthetic-lens/library/raw/``
- Global install: ``.../reasonix/skills/aesthetic-lens/library/raw/``
- Override: ``export AESTHETIC_LENS_DATA_DIR=/custom/path``

This path is **not** under the skill install directory, so it survives
``install_source`` re-installs.

Usage::

    from cv_analyzer.write_raw import write_raw

    cv_data = analyze("path/to/image.jpg")
    l1_path = write_raw(
        image_path="path/to/image.jpg",
        cv_data=cv_data,
        ai_interpretation={
            "color_scheme": "complementary",
            "layout_type": "centered",
        },
        tags={"styles": ["极简文艺"], "content_types": ["教程"]},
    )
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _get_data_dir() -> str:
    """Return the root data directory for aesthetic-lens.

    Data lives **inside the skill directory** — wherever the skill is
    installed (global, project-local, or development), the library follows.

    Resolution order:
    1. ``$AESTHETIC_LENS_DATA_DIR`` — env var override
    2. Skill-relative: ``<skill-root>/`` (same dir as ``skill.md``)
    """
    override = os.environ.get("AESTHETIC_LENS_DATA_DIR")
    if override:
        return override
    # write_raw.py is at <skill-root>/cv_analyzer/write_raw.py
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_library_dir() -> str:
    """Return the library root (contains raw/, styles/, index.json, …).

    This path lives inside the skill directory, so it follows wherever
    the skill is installed (global or project-local).
    """
    return os.path.join(_get_data_dir(), "library")


RAW_DIR = os.path.join(get_library_dir(), "raw")


def _sanitize_filename(name: str) -> str:
    """Strip/replace characters unsafe for filenames."""
    safe = "".join(c if c.isalnum() or c in " _-." else "_" for c in name)
    return safe.strip().replace(" ", "_")


def write_raw(
    image_path: str,
    cv_data: Dict[str, Any],
    ai_interpretation: Optional[Dict[str, str]] = None,
    tags: Optional[Dict[str, List[str]]] = None,
) -> str:
    """Write a L1 raw profile and return its file path.

    Parameters
    ----------
    image_path : str
        Original image path (used for filename derivation only).
    cv_data : dict
        Output from ``cv_analyzer.analyze()`` — must contain ``metadata``
        and at least one sub-analysis dict.
    ai_interpretation : dict or None
        AI-supplied interpretations for the fields listed in
        ``cv_data["ai_fills_required"]`` (if absent, the L1 record is
        marked ``incomplete: true``).
    tags : dict or None
        Categorisation tags, e.g. ``{"styles": ["极简"], "content_types": ["教程"]}``.

    Returns
    -------
    str
        Absolute path to the written JSON file.
    """
    os.makedirs(RAW_DIR, exist_ok=True)

    # Derive a unique file name (UUID prevents same-second overwrites)
    base = _sanitize_filename(os.path.splitext(os.path.basename(image_path))[0])
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:8]
    filename = f"{base}_{ts}_{uid}.json"
    dest = os.path.join(RAW_DIR, filename)

    # Build the L1 record — CV data first, then AI overlay
    record: Dict[str, Any] = {
        "l1_version": "1.0.0",
        "source_image": os.path.basename(image_path),
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "cv_data": cv_data,
    }

    if ai_interpretation:
        record["ai_interpretation"] = ai_interpretation
        record["incomplete"] = False
    else:
        # AI interpretation (requires LLM vision) was not provided
        record["incomplete"] = True
        record["incomplete_reason"] = (
            "AI aesthetic interpretation not provided. "
            "LLM vision capability required to fill ai_fills_required fields."
        )

    if tags:
        record["tags"] = tags

    with open(dest, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    return os.path.abspath(dest)
