---
name: aesthetic-lens
description: 从图片中提炼审美原则与设计理论，构建多层审美规范库
---

# Aesthetic Lens — 审美棱镜

> **项目级 Skill** — 更多见 README。
>
> ⚠️ 需要 LLM 视觉能力。CV 测量可独立运行，但完整审美分析需要 AI 填充 12 个 ``AI_FILLS`` 字段。如果当前 LLM 无法查看图片，写出的 L1 会标记 ``incomplete: true``。

从参考图片中提炼结构化的审美原则与设计理论。分析结果直接写入本地审美库，可被下游工具（如小红书排版工具）消费。

## 使用方式

### 分析单张图片

```
/esthetic-lens 分析这张图 [图片路径]
```

**Agent 执行指令（三步，缺一不可）：**

① CLI（CV only）：
   `cd aesthetic-lens && python -m cv_analyzer.cli <图片路径> --pretty`
   → 得 JSON：`{"status":"ok", "cv_data":{...}, "known_tags":{...}, "cv_classification":{...}}`

② AI 解读（需视觉能力）：
   **用你的文件工具读取 <图片路径>，将图片内容传递给视觉 API 查看。**
   不是从 CLI 输出找图片——CLI 只有 CV 数字。你必须自己读文件、看图。
   ```python
   ai = {
     "color_scheme": "complementary|analogous|monochrome|triadic",
     "composition_layout_type": "centered|rule-of-thirds|diagonal|asymmetric",
     "texture_surface_type": "smooth|rough|patterned|grainy",
     "lighting_light_quality": "soft|harsh|golden-hour|flat|dramatic",
     "spacing_spacing_principle": "breathing|dense|balanced|spacious",
     "components_component_roles": ["hero", "background", "decor"],
     "typography_hierarchy": "3-level|2-level|uniform",
     "typography_line_spacing": "tight|medium|loose",
     "typography_text_density": "sparse|medium|dense",
     "typography_alignment": "left|center|right|justified|mixed",
     "typography_font_style": "serif|sans-serif|hand-drawn|mixed",
     "style_influence": "any text"
   }
   ```
   图中无对应元素填 `"none"`。

③ 写库：
   ```python
   from cv_analyzer import assemble_l1
   assemble_l1(
       "<图片路径>",
       ai_interpretation=ai,
       tags={"styles": ["风格"], "content_types": ["类型"]},
   )
   ```
   L1 ≥10 张时追加 `python -m cv_analyzer.build_library`。

```
/esthetic-lens 提炼这组图的共同风格 [图片1][图片2][图片3]...
```

逐张分析后交叉对比，提炼共性后写入/更新风格层。

### 查询审美库

```
/esthetic-lens 查看所有审美规范
/esthetic-lens 教程类有哪些规律
/esthetic-lens 极简风格有什么原则
```

### 查看分析结果

```
/esthetic-lens 这是什么风格
/esthetic-lens 对比这两张图的风格差异 [图1][图2]
```

## 处理流程

```
接收图片 → 校验格式
  → python -m cv_analyzer.cli     (CV 测量 + classify 初判)
  → AI 审美解读 (6 个 AI_FILLS 字段)
  → write_raw() → library/raw/   (L1: 含 incomplete 标记)
  → [定期] build_library()  →    (L2 风格卡 + L3 类型卡)
```

## 五层建模说明

### L1 — Raw（单图分析）
每张图的全维度分析，保留源信息。仅供自己追溯。

### L2 — 风格层
按视觉风格聚类（极简/复古/科技/自然/轻奢等），提炼共同原则。

### L3 — 类型层
按内容类型聚类（教程/种草/开箱/测评/Vlog 等）。

### L4 — 交叉层
特定风格×类型的最优实践（极简×教程、复古×种草等）。

### L5 — 统摄层
跨越所有风格类型的底层设计哲学。

## 脱敏规则

所有 L2-L5 输出遵循：
- ❌ 不包含源文件名、品牌名
- ❌ 不包含具体色值（用区间/关系替代）
- ❌ 不包含具体字体名（用层级关系替代）
- ✅ 只输出可迁移的设计原则和约束区间

## 依赖安装

```bash
cd aesthetic-lens
source scripts/install_deps.sh
```

## 输出文件结构

数据直接存在 skill 目录下，跟随安装位置：

- **开发期**: ``aesthetic-lens/library/``
- **项目安装**: ``.reasonix/skills/aesthetic-lens/library/``
- **全局安装**: ``.../reasonix/skills/aesthetic-lens/library/``
- **自定义**: ``export AESTHETIC_LENS_DATA_DIR=/your/path``

```
library/
├── index.json         # 索引 + tag_alias_map
├── raw/          L1
├── styles/       L2
├── content_types/ L3
├── cross/        L4
└── universal.json L5
```

