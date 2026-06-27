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

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .ai_fills_schema import validate_ai_fills
from ._json_utils import safe_json_dump


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


def find_l1_by_hash(image_hash: str, raw_dir: str = RAW_DIR) -> List[str]:
    """Return paths of L1 JSONs whose ``image_hash`` matches."""
    if not os.path.isdir(raw_dir):
        return []
    matches = []
    for fn in sorted(os.listdir(raw_dir)):
        if not fn.endswith(".json"):
            continue
        fp = os.path.join(raw_dir, fn)
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("image_hash") == image_hash:
                matches.append(fp)
        except (json.JSONDecodeError, OSError):
            continue
    return matches


def find_l1_by_source(source_name: str, raw_dir: str = RAW_DIR) -> List[str]:
    """Return paths of all L1 JSONs whose source_image matches (legacy)."""
    if not os.path.isdir(raw_dir):
        return []
    matches = []
    for fn in sorted(os.listdir(raw_dir)):
        if not fn.endswith(".json"):
            continue
        fp = os.path.join(raw_dir, fn)
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("source_image") == source_name:
                matches.append(fp)
        except (json.JSONDecodeError, OSError):
            continue
    return matches


def write_raw(
    image_path: str,
    cv_data: Dict[str, Any],
    ai_interpretation: Optional[Dict[str, str]] = None,
    tags: Optional[Dict[str, List[str]]] = None,
    mode: str = "append",
) -> str:
    """Write a L1 raw profile and return its file path.

    Parameters
    ----------
    image_path : str
        Original image path (used for filename derivation only).
    cv_data : dict
        Output from ``cv_analyzer.analyze()``.
    ai_interpretation : dict or None
        AI-supplied interpretations.
    tags : dict or None
        Categorisation tags.
    mode : str
        ``"append"`` — always create a new file (default, backward compatible).
        ``"upsert"`` — if a L1 with the same source_image exists, overwrite it.
        ``"overwrite"`` — same as upsert (alias).

    Returns
    -------
    str
        Absolute path to the written JSON file.
    """
    os.makedirs(RAW_DIR, exist_ok=True)

    source_name = os.path.basename(image_path)

    # upsert/overwrite: reuse existing file by image content hash
    if mode in ("upsert", "overwrite"):
        # Compute hash of actual image bytes (not filename!)
        try:
            with open(image_path, "rb") as f:
                img_hash = hashlib.sha256(f.read()).hexdigest()[:16]
        except OSError:
            img_hash = None
        if img_hash:
            existing = find_l1_by_hash(img_hash)
            if existing:
                dest = existing[-1]
                record = _build_record(source_name, img_hash, cv_data, ai_interpretation, tags)
                with open(dest, "w", encoding="utf-8") as f:
                    safe_json_dump(record, f, indent=2)
                return os.path.abspath(dest)

    # append: always create new file
    base = _sanitize_filename(os.path.splitext(source_name)[0])
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:8]
    filename = f"{base}_{ts}_{uid}.json"
    dest = os.path.join(RAW_DIR, filename)

    # Compute image hash for fingerprinting
    try:
        with open(image_path, "rb") as f:
            img_hash = hashlib.sha256(f.read()).hexdigest()[:16]
    except OSError:
        img_hash = None

    record = _build_record(source_name, img_hash, cv_data, ai_interpretation, tags)
    with open(dest, "w", encoding="utf-8") as f:
    safe_json_dump(record, f, indent=2)

    return os.path.abspath(dest)


def _build_record(
    source_name: str,
    image_hash: Optional[str],
    cv_data: Dict[str, Any],
    ai_interpretation: Optional[Dict[str, str]],
    tags: Optional[Dict[str, List[str]]],
) -> Dict[str, Any]:
    """Construct the L1 record dict (shared by append and upsert paths)."""
    record: Dict[str, Any] = {
        "l1_version": "1.2.0",
        "source_image": source_name,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "cv_data": cv_data,
    }
    if image_hash:
        record["image_hash"] = image_hash

    if ai_interpretation:
        # Validate against schema before writing
        ai_interpretation = validate_ai_fills(ai_interpretation)
        record["ai_interpretation"] = ai_interpretation
        record["incomplete"] = False
    else:
        record["incomplete"] = True
        record["incomplete_reason"] = (
            "AI aesthetic interpretation not provided. "
            "LLM vision capability required to fill ai_fills_required fields."
        )

    if tags:
        record["tags"] = tags

    return record
