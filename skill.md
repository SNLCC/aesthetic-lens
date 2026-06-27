---
name: aesthetic-lens
description: 从图片中提炼审美原则与设计理论，构建多层审美规范库
---

# Aesthetic Lens — 审美棱镜

> **项目级 Skill** — 更多见 README。
>
> ⚠️ **图片必须直接贴到对话中**（拖放/粘贴），不能只给文件路径。
>
> ⚠️ 需要 LLM 视觉能力。CV 测量可独立运行，但完整审美分析需要 AI 填充 12 个 ``AI_FILLS`` 字段。如果当前 LLM 无法查看图片，写出的 L1 会标记 ``incomplete: true``。

从参考图片中提炼结构化的审美原则与设计理论。分析结果直接写入本地审美库，可被下游工具（如小红书排版工具）消费。

## 使用方式

### 分析单张图片

```
/esthetic-lens 分析这张图 [图片]
```

1. 运行 `python -m cv_analyzer.cli <图片路径> --pretty --with-image` 获取 CV 测量 + base64 图片（LLM 可从中读取图片进行视觉解读）
2. **⛔ 必须执行 AI 视觉解读**（不可跳过！）：
   **你必须使用视觉能力实际查看图片本身。**
   - 不要只依赖 CV 数据填空——CV 提供的是数字，不是审美判断
   - 看完图片后，严格复制以下 JSON 模板，用自己的视觉判断填入每个字段的值

   直接输出以下 dict（每个字段必填，缺一不可）：
   ```json
   {
       "color_scheme": "互补色|类比色|单色|三色",
       "composition_layout_type": "居中|三分法|对角线|不对称",
       "texture_surface_type": "光滑|粗糙|图案|颗粒",
       "lighting_light_quality": "柔和|硬朗|黄金时段|平淡|戏剧性",
       "spacing_spacing_principle": "透气|紧密|平衡|留白",
       "components_component_roles": ["主图", "背景", "装饰"],
       "typography_hierarchy": "3级|2级|均匀",
       "typography_line_spacing": "紧密|中等|宽松",
       "typography_text_density": "稀疏|中等|密集",
       "typography_alignment": "左对齐|居中|两端对齐|混合",
       "typography_font_style": "衬线|无衬线|手写|混合",
       "style_influence": "自由描述风格流派"
   }
   ```
   ⚠️ 如果图中确实没有某个元素（如纯图片无文字），对应字段填 `"none"`。
   - `color.scheme` — 配色方案：complementary / analogous / monochrome / triadic
   - `composition.layout_type` — 布局：centered / rule-of-thirds / diagonal / asymmetric
   - `texture.surface_type` — 表面：smooth / rough / patterned / grainy
   - `lighting.light_quality` — 光影：soft / harsh / golden-hour / flat / dramatic
   - `spacing.spacing_principle` — 留白：breathing / dense / balanced / spacious
   - `components.component_roles` — 组件角色：["hero", "background", "decor"]
   - `typography.hierarchy` — 字号层次：3-level / 2-level / uniform
   - `typography.line_spacing` — 行距：tight / medium / loose
   - `typography.text_density` — 文字密度：sparse / medium / dense
   - `typography.alignment` — 对齐：left / center / justified / mixed
**  - `typography.font_style` — 字体风格：serif / sans-serif / hand-drawn / mixed
   - `style_influence` — 模仿/借鉴的设计风格流派（如 Swiss Design、日式侘寂、包豪斯），自由文本
3. 立即将 AI 视觉解读结果 + CV 数据写入 L1（不可只跑 CV 就停）：
   
   调用 `write_raw(image_path, cv_data, ai_interpretation={上述JSON}, tags={你的标签}, mode="upsert")`
   或使用一键入口 `assemble_l1(image_path, ai_interpretation={上述JSON}, tags={你的标签})`
   
   ⛔ 如果只跑了步骤 1 没有写 L1，产出不完整。
4. （可选）定期运行 `python -m cv_analyzer.build_library` 聚合库

### 批量分析归纳风格

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

