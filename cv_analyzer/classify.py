"""Style & content-type classifier — gives a first-pass classification purely
from CV measurements, before AI interpretation.

The classifier's output goes into ``cv_data["cv_classification"]`` so the AI
can compare its own judgement against the machine's and calibrate biases.
"""

from typing import Any, Dict, List


def classify(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a first-pass style / content-type guess from CV data only.

    Parameters
    ----------
    cv_data : dict
        The output of ``cv_analyzer.analyze()``.

    Returns
    -------
    dict with keys:
        - ``styles``: list of candidate style tags (may be empty)
        - ``content_types``: list of candidate content-type tags (may be empty)
        - ``confidence``: ``"high"``, ``"medium"``, or ``"low"``
    """
    color = cv_data.get("color", {}) or {}
    composition = cv_data.get("composition", {}) or {}
    lighting = cv_data.get("lighting", {}) or {}
    spacing = cv_data.get("spacing", {}) or {}
    texture = cv_data.get("texture", {}) or {}

    styles: List[str] = []
    content_types: List[str] = []

    # ----- style heuristics -----

    sat = color.get("saturation_stats", {}) or {}
    lit = color.get("lightness_stats", {}) or {}
    mean_sat = sat.get("mean", 128)
    mean_lit = lit.get("mean", 128)
    sym = composition.get("symmetry_score", 0)
    neg = spacing.get("negative_space_ratio", 0)
    cmp = texture.get("texture_complexity", 0)
    contrast = lighting.get("contrast", 0)

    # 极简文艺 — high negative space, low saturation, mid lightness
    if neg > 0.4 and mean_sat < 80 and 80 < mean_lit < 200:
        styles.append("极简文艺")

    # 复古胶片 — low saturation, low contrast; exclude very dark (夜读风/暗黑系)
    if mean_sat < 90 and contrast < 0.3 and mean_lit > 80:
        styles.append("复古胶片")

    # 赛博朋克 — high contrast, high saturation, vibrant
    if contrast > 0.4 and mean_sat > 140:
        styles.append("赛博朋克")

    # 自然森系 — high texture complexity, mid lightness
    if cmp > 0.5 and 100 < mean_lit < 180:
        styles.append("自然森系")

    # 科技极客 — high symmetry, high contrast, low negative space
    if sym > 0.7 and contrast > 0.35 and neg < 0.3:
        styles.append("科技极客")

    # 暗黑系 — very low lightness
    if mean_lit < 60:
        styles.append("暗黑系")

    # 轻奢质感 — mid-high saturation, mid lightness, mid symmetry
    if 100 < mean_sat < 160 and 120 < mean_lit < 200 and sym > 0.5:
        styles.append("轻奢质感")

    # 新中式水墨 — low saturation, mid lightness, high negative space
    if mean_sat < 70 and 100 < mean_lit < 190 and neg > 0.3:
        styles.append("新中式水墨")

    # 治愈系 — mid lightness, mid saturation, high negative space
    if 100 < mean_lit < 200 and 60 < mean_sat < 130 and neg > 0.35:
        styles.append("治愈系")

    # 夜读风 — very low lightness, mid-low saturation
    if mean_lit < 80 and mean_sat < 100:
        styles.append("夜读风")

    # ----- content-type heuristics -----

    # 教程 — high symmetry, content dense
    if sym > 0.6 and neg < 0.35:
        content_types.append("教程")

    # 开箱 / 产品展示 — centered, high symmetry
    if sym > 0.7 and neg < 0.4:
        content_types.append("开箱")

    # Vlog / 生活记录 — varied composition
    if 0.2 < sym < 0.6 and 0.3 < neg < 0.6:
        content_types.append("Vlog")

    # ----- confidence -----
    confidence = "high" if len(styles) >= 2 or (len(styles) == 1 and len(content_types) >= 1) else "medium" if styles else "low"

    return {
        "styles": styles,
        "content_types": content_types,
        "confidence": confidence,
    }
