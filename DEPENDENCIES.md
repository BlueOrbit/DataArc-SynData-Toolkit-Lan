# 📦 Installation

This document describes all dependencies required to run **DataArc SynData Toolkit** and provides detail installation guide.

## 1. Hardware Requirements

This project requires GPU environment. We recommend following settings:
  - Linux (Ubuntu 20.04+)
  - CUDA 12.4+
  - GPU memory ≥ 24 GB (for 7B–13B models)

## 2. Core Python Dependencies

| Category | Library | Version | Notes |
|---------|----------|---------|--------|
| **Core** | Python | 3.10+ | Runtime |
| **LLM Engine** | vLLM | 0.8.5post1 | Work with torch 2.6.0 + cu124 |
| **Deep Learning** | PyTorch | >=2.6.0 | We recommend torch version > 2.6.0 |
| **Model loading** | sentence-transformers | ≥5.1.2 |  |
| **Tokenizer** | tiktoken | ≥0.12.0 |  |
| **Document processing** | mineru[core] | ≥2.6.4 | PDF → JSONL pipeline |
|  | pymupdf | ≥1.26.5 | PDF parsing |
|  | rank-bm25 | ≥0.2.2 | passage retrieval |
| **Utils** | pyyaml | ≥6.0.3 | Config |
|  | python-dotenv | ≥1.1.1 | Env loading |
|  | tqdm | ≥4.67.1 | Progress |
| **API** | openai | ≥2.6.0 | LLM API support |

## 3. Installation guide

If you encounter problem building dependencies with ``uv sync``, please follow this installation guide.

Firstly, specified the python version that you want and delete the cuda dependent package in [pyproject.toml](./pyproject.toml)

```shell
requires-python = "==3.11.13"  ## specified python version here
dependencies = [
    "gradio>=5.49.1",
    "mineru[core]>=2.6.4",  ## delete this line since it's cuda dependent
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
    "vllm>=0.8.5.post1",   ## delete this line since it's cuda dependent
]
```

#### Step 1 — Check Your CUDA Version

Before installing PyTorch or vLLM, confirm your CUDA verison, run command ``nvidia-smi``.

Change the cuda version specified in [pyproject.toml](./pyproject.toml) to your cuda version.

``` shell
[[tool.uv.index]]
name = "pytorch-cu124"  ## e.g. if you have cuda 12.6, change cud124 -> cu126, all of them below as well
url = "https://download.pytorch.org/whl/cu124" 
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cu124" }
torchvision = { index = "pytorch-cu124" }
torchaudio = { index = "pytorch-cu124" }
```

#### Step 2 — Install Matching PyTorch Version

Install the correct pytorch version that match your cuda version. See details in [Pytorch Previous Versions](https://pytorch.org/get-started/previous-versions/).

``` shell
# for example, if you are using cuda12.6, you can install torch 2.7.0 using this uv command
uv add torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0
```

#### Step 3 — Install CUDA Dpendent Dependencies (Must Be After PyTorch)

vLLM depends on your existing PyTorch installation and CUDA runtime. Use this command to install the correct version of vLLM.

```shell
uv add vllm mineru[core]
```

#### Step 4 - Install General Dependencies (CUDA-Independent)

```shell
uv sync
```