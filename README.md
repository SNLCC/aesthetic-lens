# Aesthetic Lens — 审美棱镜 🔍🎨

从图片中提炼审美规则与设计原则，构建可演化的多层审美库。

[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-32%20passed-brightgreen)](.)

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/你的用户名/aesthetic-lens.git
cd aesthetic-lens

# 安装依赖（创建 venv + pip install）
source scripts/install_deps.sh

# CV 分析一张图片
source .venv/bin/activate  # 或 .venv/Scripts/activate (Windows)
python -m cv_analyzer.cli path/to/image.jpg --pretty

# 运行测试
python -m pytest cv_analyzer/test_*.py -v
```

## 工作流

```
图片 → CV 分析(6维) → classify(初判) → AI 审美解读 → write_raw(L1) → build_library(L2→L5)
```

| 命令 | 作用 |
|------|------|
| `python -m cv_analyzer.cli <img> --pretty` | CV 测量 + 分类 |
| `/aesthetic-lens 分析这张图 [图片]` | 完整分析（需 LLM 视觉） |
| `python -m cv_analyzer.build_library` | 聚合审美库（自进化） |

## 11 个分析维度（6 个 CV + 5 个 LLM 视觉）

| 维度 | 来源 | 示例 |
|------|------|------|
| 色彩 palette_bgr / palette_hex_rgb | CV | K-Means + ColorThief |
| 构图 symmetry / edge / thirds / saliency | CV | centered / diagonal |
| 纹理 complexity / glcm_contrast | CV | smooth / grainy |
| 光影 brightness / contrast / histogram | CV | soft / harsh |
| 留白 negative_space / distribution | CV | breathing / dense |
| 组件 roi_segments / slices | CV | hero / background |
| 排版 hierarchy / spacing / density | LLM 视觉 | 3-level / loose |
| 对齐 alignment | LLM 视觉 | left / center / mixed |
| 字体 font_style | LLM 视觉 | serif / sans-serif |

## 五层模型（L1→L5，自演化）

| 层 | 内容 | 触发 |
|----|------|------|
| L1 Raw | 单图全量分析 | 每次分析 |
| L2 风格卡 | 按视觉风格聚合 | `build_library` |
| L3 类型卡 | 按内容类型聚合 | `build_library` |
| L4 交叉层 | 风格×类型最佳实践 | 待建 |
| L5 统摄层 | "什么是好设计"的核心公理 | ≥10 张 L1 自动 |

标签不预置——AI 自由命名，`build_library` 自动注册到 `tag_alias_map`。

## 开源合规

本项目使用 MIT 许可证。所有依赖均为开源宽松许可证（Apache 2.0 / BSD-3 / HPND），可商用。
