# 📦 安装指南（中文版）

本文档描述运行 **DataArc SynData Toolkit** 所需的全部依赖，并提供详细的安装步骤。

## 1. 硬件要求

本项目需要 GPU 环境，推荐配置如下：

- Linux（Ubuntu 20.04+）
- CUDA 12.4+
- GPU 显存 ≥ 24 GB（适用于 7B–13B 模型）

## 2. 核心 Python 依赖

| 分类 | 库 | 版本 | 说明 |
|------|------|--------|------|
| **核心** | Python | 3.10+ | 运行环境 |
| **LLM 引擎** | vLLM | 0.8.5.post1 | 需配合 torch 2.6.0 + cu124 |
| **深度学习** | PyTorch | >=2.6.0 | 建议使用 2.6.0 以上版本 |
| **模型加载** | sentence-transformers | ≥5.1.2 |  |
| **分词器** | tiktoken | ≥0.12.0 |  |
| **文档处理** | mineru[core] | ≥2.6.4 | PDF → JSONL 处理流程 |
|  | pymupdf | ≥1.26.5 | PDF 解析 |
|  | rank-bm25 | ≥0.2.2 | 文本检索 |
| **工具** | pyyaml | ≥6.0.3 | 配置文件 |
|  | python-dotenv | ≥1.1.1 | 环境变量加载 |
|  | tqdm | ≥4.67.1 | 进度条 |
| **API** | openai | ≥2.6.0 | LLM API 支持 |

## 3. 安装指南

如果在使用 `uv sync` 安装依赖时遇到构建问题，请按照以下步骤进行。

首先，确认你要使用的 Python 版本，并删除 [pyproject.toml](./pyproject.toml) 中所有与 CUDA 相关的依赖。

```toml
requires-python = "==3.11.13"  ## 在此指定 Python 版本
dependencies = [
    "fastapi>=0.122.0",
    "mineru[core]>=2.6.4",  ## 删除这一行
    "openai>=2.6.0",
    "pymupdf>=1.26.5",
    "python-dotenv>=1.1.1",
    "pyyaml>=6.0.3",
    "rank-bm25>=0.2.2",
    "sentence-transformers>=5.1.2",
    "tiktoken>=0.12.0",
    "torch==2.6.0",
    "torchaudio==2.6.0",
    "torchvision==0.21.0",
    "tqdm>=4.67.1",
    "vllm>=0.8.5.post1",   ## 删除这一行
]
```

### 第一步 — 检查 CUDA 版本

使用下面命令查看 CUDA 版本：

```bash
nvidia-smi
```

然后在 pyproject.toml 中调整与你 CUDA 对应的 PyTorch 索引：

```toml
[[tool.uv.index]]
name = "pytorch-cu124"  ## 例如你的环境为CUDA 12.6，则将下方所有 cu124 都改为 cu126
url = "https://download.pytorch.org/whl/cu124"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cu124" }
torchvision = { index = "pytorch-cu124" }
torchaudio = { index = "pytorch-cu124" }
```

### 第二步 — 安装对应 CUDA 的 PyTorch 版本

安装与你 CUDA 匹配的正确版本 PyTorch，可参考[PyTorch官方文档](https://pytorch.org/get-started/previous-versions/)

示例（CUDA 12.6）：

```bash
uv add torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0
```

### 第三步 — 安装 CUDA 依赖库（必须在 PyTorch 之后安装）

vLLM 与 mineru 依赖已安装的 PyTorch与 CUDA 环境，使用 mineru 需要 torch >= 2.6.0

```bash
uv add vllm mineru[core]
```

### 第四步 — 安装通用依赖（与 CUDA 无关）

```bash
uv sync
```

完成以上步骤后，如果还是没法运行，请在 issues 中提出。

