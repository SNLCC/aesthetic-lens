# Aesthetic Lens — Contributing Guide

## 项目简介

Aesthetic Lens（审美棱镜）是一个从图片中提炼审美原则与设计理论的工具。它通过计算机视觉（CV）客观测量和 AI 审美解读，构建可复用的审美规范库。

## 环境准备

```bash
# 克隆后进入项目
cd aesthetic-lens

# 安装依赖（创建 venv + pip install）
source scripts/install_deps.sh

# 验证安装
python -m pytest cv_analyzer/test_*.py -v
```

## 开发工作流

### 代码结构

```
aesthetic-lens/
├── cv_analyzer/         # CV 分析引擎
│   ├── analyze.py       # 统一入口
│   ├── color.py         # 色彩分析
│   ├── composition.py   # 构图分析
│   ├── texture.py       # 纹理分析
│   ├── lighting.py      # 光影分析
│   ├── spacing.py       # 留白分析
│   ├── components.py    # 组件结构
│   ├── classify.py      # 启发式分类
│   ├── write_raw.py     # L1 写入
│   ├── build_library.py # 库构建
│   ├── _utils.py        # Unicode-safe I/O
│   └── cli.py           # 命令行入口
├── scripts/             # 安装脚本
├── library/             # 审美库（用户数据）
├── skill.md             # Reasonix Skill 定义
└── README.md
```

### 测试

```bash
# 运行全部测试
python -m pytest cv_analyzer/test_*.py -v

# 运行单个测试文件
python -m pytest cv_analyzer/test_color.py -v

# 运行单个测试
python -m pytest cv_analyzer/test_analyze.py::TestAnalyze::test_color_section_structure -v
```

## 编码规范

- **Python 3.10+** — 使用类型注解
- **PEP 8** — 两个空行分隔顶级定义，一个空行分隔方法
- **Docstring** — 所有公共函数需要 docstring
- **AI_FILLS** — AI 填充的字段用 `# AI_FILLS:` 注释，并附示例值
- **测试** — 新功能需要对应测试

## 提交 PR

1. Fork 项目
2. 创建特性分支：`git checkout -b feat/my-feature`
3. 提交改动
4. 确保所有测试通过
5. 发起 Pull Request

## 许可证

MIT License — 详见 LICENSE 文件。所有依赖均为 BSD/MIT/PSF 许可。
