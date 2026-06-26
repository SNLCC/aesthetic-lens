"""build_library — scan accumulated L1 raw profiles and evolve the aesthetic
rule library (L2 style cards, L3 content-type cards, index).

Run periodically (e.g. after every 5 new L1s) to keep the library fresh::

    python -m cv_analyzer.build_library
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple

from .write_raw import get_library_dir


def _slug(tag: str) -> str:
    """Turn a Chinese tag into a stable English ID slug.

    Known terms use the mapping table below.  Unknown tags fall back to
    a short hash of the UTF-8 bytes, guaranteeing a unique forever-stable ID.
    """
    s = tag.strip().lower()
    # known term → english
    table = {
        "极简": "minimalist", "文艺": "literati",
        "新中式": "neo-chinese", "水墨": "ink",
        "夜读": "night-reading", "复古": "vintage",
        "胶片": "film", "科技": "tech", "极客": "geek",
        "自然": "natural", "森系": "forest",
        "轻奢": "light-luxury", "质感": "texture",
        "治愈": "healing", "暗黑": "dark",
        "赛博": "cyber", "朋克": "punk",
        "教程": "tutorial", "种草": "recommend",
        "开箱": "unboxing", "测评": "review",
        "vlog": "vlog", "生活": "lifestyle",
    }
    for zh, en in table.items():
        s = s.replace(zh, en)
    # if any chinese chars remain after mapping, generate a stable hash
    remaining = re.sub(r"[a-z0-9-]", "", s)
    if remaining:
        import hashlib
        h = hashlib.sha256(tag.encode("utf-8")).hexdigest()[:8]
        base = re.sub(r"[^a-z0-9-]", "-", s).strip("-")
        base = re.sub(r"-+", "-", base)
        base = base if base else "tag"
        return f"{base}-{h}"
    s = re.sub(r"[^a-z0-9-]", "-", s).strip("-")
    s = re.sub(r"-+", "-", s)
    return s if s else "tag"


def _load_index() -> Dict[str, Any]:
    path = os.path.join(get_library_dir(), "index.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.1.0", "tag_alias_map": {}, "styles": [], "content_types": [], "raw_images": [], "cross_profiles": [], "has_universal": False}


def _save_index(idx: Dict[str, Any]) -> None:
    idx["updated_at"] = datetime.now(timezone.utc).isoformat()
    path = os.path.join(get_library_dir(), "index.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2, ensure_ascii=False)


def _l1_files() -> List[Tuple[str, Dict]]:
    raw_dir = os.path.join(get_library_dir(), "raw")
    if not os.path.isdir(raw_dir):
        return []
    results = []
    for fn in sorted(os.listdir(raw_dir)):
        if not fn.endswith(".json"):
            continue
        fp = os.path.join(raw_dir, fn)
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            results.append((fp, data))
        except (json.JSONDecodeError, OSError):
            continue
    return results


def _discover_tags(l1s: List[Tuple[str, Dict]], alias_map: Dict[str, str]) -> Dict[str, str]:
    seen: Set[str] = set(alias_map.keys())
    for _fp, data in l1s:
        tags = data.get("tags", {}) or {}
        for tag_list in tags.values():
            if isinstance(tag_list, list):
                for tag in tag_list:
                    if tag and tag not in seen:
                        base = _slug(tag)
                        candidate = base
                        used = set(alias_map.values())
                        i = 1
                        while candidate in used:
                            candidate = f"{base}-{i}"
                            i += 1
                        alias_map[tag] = candidate
                        seen.add(tag)
    return alias_map


def _aggregate_l1s(l1s: List[Tuple[str, Dict]], tag_key: str, target_tag: str,
                     min_confidence: str = "low") -> List[Dict]:
    """Return L1s with target_tag. Skips incomplete L1s when min_confidence="high"."""
    matched = []
    for _fp, data in l1s:
        tags = data.get("tags", {}) or {}
        vals = tags.get(tag_key, []) or []
        if target_tag in vals:
            matched.append(data)
    return matched


def _build_style_card(style_tag: str, l1s: List[Dict], alias_map: Dict[str, str]) -> Dict:
    card: Dict[str, Any] = {
        "id": alias_map.get(style_tag, _slug(style_tag)),
        "label": style_tag,
        "source_count": len(l1s),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    sats, lits, syms, negs, cmps, contrs = [], [], [], [], [], []
    ais: Dict[str, list] = defaultdict(list)
    for d in l1s:
        cv = d.get("cv_data", {}) or {}
        color = cv.get("color", {}) or {}
        comp = cv.get("composition", {}) or {}
        tex = cv.get("texture", {}) or {}
        light = cv.get("lighting", {}) or {}
        space = cv.get("spacing", {}) or {}
        sats.append((color.get("saturation_stats", {}) or {}).get("mean", 128))
        lits.append((color.get("lightness_stats", {}) or {}).get("mean", 128))
        syms.append(comp.get("symmetry_score", 0))
        negs.append(space.get("negative_space_ratio", 0))
        cmps.append(tex.get("texture_complexity", 0))
        contrs.append(light.get("contrast", 0))
        ai = d.get("ai_interpretation", {}) or {}
        for k, v in ai.items():
            if v:
                ais[k].append(v)

    def _rng(vals): return [min(vals), max(vals)] if vals else []
    def _avg(vals): return sum(vals) / len(vals) if vals else 0.0

    card["cv_profile"] = {
        "saturation_mean": _avg(sats), "saturation_range": _rng(sats),
        "lightness_mean": _avg(lits), "lightness_range": _rng(lits),
        "symmetry_mean": _avg(syms), "symmetry_range": _rng(syms),
        "negative_space_mean": _avg(negs), "negative_space_range": _rng(negs),
        "texture_complexity_mean": _avg(cmps), "contrast_mean": _avg(contrs),
    }
    ai_summary = {}
    for k, vals in ais.items():
        freq = defaultdict(int)
        for v in vals:
            key = json.dumps(v, ensure_ascii=False, sort_keys=True) if not isinstance(v, (str, int, float, bool, type(None))) else v
            freq[key] += 1
        ai_summary[k] = sorted(freq.items(), key=lambda x: -x[1])[:3]
    if ai_summary:
        card["ai_patterns"] = ai_summary
    return card


def _write_card(card: Dict, sub_dir: str) -> str:
    target = os.path.join(get_library_dir(), sub_dir, f"{card['id']}.json")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2, ensure_ascii=False)
    return target

# ---------------------------------------------------------------------------
# main build
# ---------------------------------------------------------------------------

def build() -> Dict[str, Any]:
    """Run the full library build and return a summary dict."""
    idx = _load_index()
    alias_map: Dict[str, str] = idx.get("tag_alias_map", {})
    l1s = _l1_files()
    summary = {"l1_count": len(l1s), "tags_discovered": 0, "styles_written": [], "content_types_written": [], "cross_written": []}
    if not l1s:
        return summary

    old_len = len(alias_map)
    alias_map = _discover_tags(l1s, alias_map)
    summary["tags_discovered"] = len(alias_map) - old_len

    style_tags: Set[str] = set()
    ct_tags: Set[str] = set()
    for _fp, data in l1s:
        tags = data.get("tags", {}) or {}
        for s in (tags.get("styles", []) or []):
            if s:
                style_tags.add(s)
        for ct in (tags.get("content_types", []) or []):
            if ct:
                ct_tags.add(ct)

    for tag in sorted(style_tags):
        matched = _aggregate_l1s(l1s, "styles", tag)
        if matched:
            card = _build_style_card(tag, matched, alias_map)
            _write_card(card, "styles")
            summary["styles_written"].append(tag)

    for tag in sorted(ct_tags):
        matched = _aggregate_l1s(l1s, "content_types", tag)
        if matched:
            card = _build_style_card(tag, matched, alias_map)
            _write_card(card, "content_types")
            summary["content_types_written"].append(tag)

    idx["tag_alias_map"] = alias_map
    idx["styles"] = sorted(style_tags)
    idx["content_types"] = sorted(ct_tags)
    idx["raw_images"] = sorted(set(d.get("source_image", "") for _, d in l1s))

    # L4 cross-profiles: style × content-type intersections
    for s_tag in style_tags:
        for ct_tag in ct_tags:
            matched = [d for d in l1s
                       if s_tag in (d.get("tags", {}).get("styles", []) or [])
                       and ct_tag in (d.get("tags", {}).get("content_types", []) or [])]
            if len(matched) >= 2:
                cid = f"{alias_map.get(s_tag, _slug(s_tag))}-{alias_map.get(ct_tag, _slug(ct_tag))}"
                _write_card({
                    "id": cid, "style": s_tag, "content_type": ct_tag,
                    "source_count": len(matched), "updated_at": datetime.now(timezone.utc).isoformat(),
                }, "cross")
                summary.setdefault("cross_written", []).append(cid)

    _save_index(idx)

    # Trigger universal model if enough data
    if len(l1s) >= 10:
        build_universal(l1s)

    return summary


# ---------------------------------------------------------------------------
# L5 universal model
# ---------------------------------------------------------------------------

def build_universal(l1s: List[Tuple[str, Dict]]) -> Dict:
    """Aggregate cross-style principles from all L1s into a universal card.

    Called automatically by ``build()`` when >=10 L1s are available.
    """
    card: Dict[str, Any] = {
        "version": "1.0.0",
        "l1_count": len(l1s),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "core_principles": [],
        "layout_laws": [],
        "color_axioms": [],
        "evolution_temperature": min(len(l1s) / 50, 1.0),
    }

    # Collect all AI interpretation values across all L1s
    schemes, layouts, surfaces, lights, spacings, roles = [], [], [], [], [], []
    for _, d in l1s:
        ai = d.get("ai_interpretation", {}) or {}
        if ai.get("color_scheme"):
            schemes.append(ai["color_scheme"])
        if ai.get("layout_type"):
            layouts.append(ai["layout_type"])
        if ai.get("surface_type"):
            surfaces.append(ai["surface_type"])
        if ai.get("light_quality"):
            lights.append(ai["light_quality"])
        if ai.get("spacing_principle"):
            spacings.append(ai["spacing_principle"])

    # Frequency distribution
    def _freq(vals):
        c = defaultdict(int)
        for v in vals:
            c[v] += 1
        return sorted(c.items(), key=lambda x: -x[1])

    card["observed_patterns"] = {
        "color_schemes": _freq(schemes),
        "layout_types": _freq(layouts),
        "surface_types": _freq(surfaces),
        "light_qualities": _freq(lights),
        "spacing_principles": _freq(spacings),
    }

    target = os.path.join(get_library_dir(), "universal.json")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2, ensure_ascii=False)

    return card


# ---------------------------------------------------------------------------
# reclassify mode
# ---------------------------------------------------------------------------

def reclassify_l1s() -> Dict[str, Any]:
    """Mark all L1 files as candidates for re-classification.

    This does NOT run the AI itself (that's the calling agent's job).
    It prepares the metadata so the agent knows which files to re-examine.

    Returns a summary of files flagged for reclassification.
    """
    l1s = _l1_files()
    flagged = []
    for fp, data in l1s:
        # Only flag files that have AI interpretation
        if data.get("ai_interpretation"):
            data["_reclassify_flagged"] = True
            data["_revision_count"] = data.get("_revision_count", 0) + 1
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            flagged.append(os.path.basename(fp))

    return {
        "total_l1s": len(l1s),
        "flagged_for_reclassify": len(flagged),
        "files": flagged,
    }


# ---------------------------------------------------------------------------
# main entry
# ---------------------------------------------------------------------------

def main():
    """CLI entry for library management."""
    import sys
    args = sys.argv[1:]

    if "--reclassify" in args:
        r = reclassify_l1s()
        print(f"Flagged {r['flagged_for_reclassify']}/{r['total_l1s']} L1s for re-interpretation")
    elif "--universal-only" in args:
        l1s = _l1_files()
        if l1s:
            u = build_universal(l1s)
            print(f"Universal model updated (temp={u['evolution_temperature']:.2f})")
        else:
            print("No L1 files found")
    else:
        s = build()
        print(f"L1 files: {s['l1_count']}, new tags: {s['tags_discovered']}")
        print(f"Styles: {len(s['styles_written'])}, Content types: {len(s['content_types_written'])}")


if __name__ == "__main__":
    main()
