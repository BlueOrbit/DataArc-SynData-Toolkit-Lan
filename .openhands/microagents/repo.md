# DataArc SynData Toolkit

## Project Description

DataArc SynData Toolkit is a modular synthetic data generation toolkit for training Large Language Models (LLMs). Developed by DataArcTech and IDEA, it enables users to generate customized training data through simple configuration files. The toolkit supports multi-source data synthesis (local corpora, HuggingFace datasets, model distillation), multilingual output, and integrates end-to-end model training via the verl framework (SFT and GRPO).

## File Structure

- **`configs/`** - YAML configuration files for SDG pipeline, SFT, and GRPO training
- **`sdgsystem/`** - Core system containing:
  - `app/` - FastAPI backend with REST APIs and SSE streaming
  - `generation/` - Data generation and rewriting modules
  - `documents/` - PDF parsing, chunking, and retrieval
  - `distillation/` - Model distillation synthesis (self-instruct, evol-instruct)
  - `tasks/` - SDG task executors (local, web, distill)
  - `models/` - Unified LLM interface and postprocessing
  - `trainer/` - Post-training launcher (SFT + GRPO via verl)
  - `webui/` - React frontend for GUI
- **`verl/`** - Integrated verl framework for distributed training
- **`docs/`** - Documentation (dependencies, use cases)
- **`examples/`** - Domain-specific examples (finance, mathematics, medicine)

## Getting Started

**Requirements**: Python 3.11.13, CUDA 12.8+, GPU ≥ 24GB VRAM

```bash
# Install
pip install uv && uv sync

# Create .env file with API credentials
echo "API_KEY=sk-xxx" > .env

# Generate synthetic data
uv run sdg generate configs/sdg.yaml

# Train models
uv run sdg train configs/sft.yaml   # SFT
uv run sdg train configs/grpo.yaml  # GRPO

# Run GUI (two terminals)
uv run fastapi dev sdgsystem/app/main.py  # Backend
cd sdgsystem/webui && pnpm install && pnpm dev  # Frontend
```

## Developer Notes

- Extend data generation by inheriting `BaseTaskConfig` and `BaseTaskExecutor` in `sdgsystem/tasks/`
- Customize rewriting by inheriting `BaseRewriteConfig` and `BaseRewriter` in `sdgsystem/generation/`
- Configuration examples are in `configs/` directory
- See `docs/DEPENDENCIES.md` for detailed installation troubleshooting
