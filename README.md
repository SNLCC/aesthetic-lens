# Aesthetic Lens — 审美棱镜 🔍🎨

从参考图片中提炼结构化的审美原则与设计理论，构建可复用的审美规范库。

## 快速开始

### 依赖安装

```bash
cd aesthetic-lens
chmod +x scripts/install_deps.sh
./scripts/install_deps.sh
```

### 使用

在 Reasonix 中通过 `/aesthetic-lens` skill 使用：

```
/esthetic-lens 分析这张图 [图片文件]
```

或直接通过 CLI 测试 CV 分析：

```bash
source .venv/bin/activate
python -m cv_analyzer.cli path/to/image.jpg --pretty
```

### 查看审美库

所有提炼结果存储在 `aesthetic-lens/library/` 目录。

## 项目结构

```
aesthetic-lens/
├── cv_analyzer/        # Python CV 分析包
│   ├── analyze.py      # 统一入口
│   ├── color.py        # 色彩分析
│   ├── composition.py  # 构图分析
│   ├── texture.py      # 纹理分析
│   ├── lighting.py     # 光影分析
│   ├── spacing.py      # 留白分析
│   ├── components.py   # 组件结构分析
│   └── cli.py          # CLI 入口
├── library/            # 审美规范库
│   ├── raw/            # L1 单图分析
│   ├── styles/         # L2 风格层
│   ├── content_types/  # L3 类型层
│   ├── cross/          # L4 交叉层
│   └── universal.json  # L5 统摄层
├── scripts/            # 安装脚本
├── skill.md            # Reasonix Skill 定义
└── requirements.txt    # Python 依赖
```

## 设计原则

1. **脱敏优先** — 输出的审美原则不保留源图片痕迹，100% 可开源
2. **CV + AI 融合** — 客观测量 + 高阶审美解读，互相印证
3. **多层抽象** — 从单图到风格到统摄哲学，层层提炼
4. **零外部 API 费用** — 审美分析由 agent 内置能力完成

## 开源合规

本项目使用 MIT 许可证。所有依赖均为 BSD/MIT/PSF 许可，可商用。

## 下游集成

小红书排版工具可通过直接读取 `library/` 中的 JSON 文件获取审美约束：

```python
import json
with open("aesthetic-lens/library/styles/极简.json") as f:
    rules = json.load(f)
    # rules["color"]["rules"] → 色彩约束
    # rules["composition"]["rules"] → 构图约束
```

## 审美维度

| 维度 | CV 测量项 | AI 解读 |
|------|-----------|---------|
| 色彩 | K-Means 主色提取, HSL 统计, ColorThief | 配色法则, 色彩情绪, 色彩节奏 |
| 构图 | 对称性评分, 边缘密度, 3×3 三分网格, Saliency | 布局类型, 视觉重量, 引导线 |
| 纹理 | LBP 复杂度, GLCM 对比度 | 表面类型, 材质感 |
| 光影 | 亮度直方图, RMS 对比度, 象限光源估计 | 光影质量, 氛围风格 |
| 留白 | 负空间比, 4×4 内容分布网格 | 呼吸感, 间距系统 |
| 组件 | 轮廓检测, 水平切片分析 | 组件角色, 跨组件协调 |
