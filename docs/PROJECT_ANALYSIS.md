# DataArc SynData Toolkit: Deep Study Report

## 🏗️ Architecture Overview

The **DataArc SynData Toolkit** is a modular framework designed for high-quality synthetic data generation (SDG) and subsequent model fine-tuning. Its architecture follows a decoupled design, allowing for flexible customization of each stage in the data lifecycle.

---

## 🧩 Core Components

### 1. Pipeline Orchestrator (`sdgsystem/pipeline.py`)
The heart of the system. it manages the end-to-end flow:
- **Execution**: Triggers the generation task.
- **Evaluation**: Performs binary (solved/unsolved) and scoring-based quality checks.
- **Refinement**: Uses a rewriter to adjust samples that are too hard or too easy.
- **Categorization**: Splits results into three distinct datasets for targeted training.

### 2. Task Executors (`sdgsystem/tasks/`)
- **Local (`local.py`)**: Implements a RAG (Retrieval-Augmented Generation) pipeline. It parses local PDFs/documents, chunks them, extracts domain keywords, and uses BM25 retrieval to provide context for generation.
- **Web (`web.py`)**: Automates the discovery and filtering of high-quality datasets from Huggingface.
- **Distill (`distill.py`)**: Facilitates generating training data from teacher models.

### 3. Model Management (`sdgsystem/models/`)
- **Unified Client**: Wraps various backends (vLLM for local, OpenAI/DeepSeek/Ollama for APIs).
- **Lazy Loading**: Local models are loaded into VRAM only when needed.
- **Post-Processing**: Includes mechanisms like **Majority Voting** (Exact Match, Semantic Clustering, or LLM-based) to ensure high-quality answers.

### 4. Parallel Execution & Buffering (`sdgsystem/parallel.py`, `sdgsystem/buffer.py`)
- **Acceleration**: Uses `ThreadPoolExecutor` to parallelize prompt generation and evaluation.
- **Resilience**: A task buffer saves progress to disk, allowing the pipeline to resume from the last successful stage if interrupted—saving both time and API tokens.

### 5. Post-Training (`verl/`)
The toolkit integrates the `verl` framework, enabling users to immediately transition from data generation to model training:
- **SFT**: Supervised Fine-Tuning.
- **GRPO**: Group Relative Policy Optimization, specialized for RLHF and reasoning tasks.

---

## 🔄 Execution Workflow

1.  **Configuration**: User defines the task type and model providers in a YAML file.
2.  **Generation**: The system extracts domain keywords and generates initial samples (with RAG support for local tasks).
3.  **Initial Quality Gate**: The student model attempts to "solve" the generated samples.
4.  **Rewrite Cycle**: Unsolved or overly simple samples are rewritten by a teacher model to hit the "sweet spot" of training difficulty (the **learnable** set).
5.  **Final Quality Gate**: Samples are re-evaluated and categorized.
6.  **Export/Training**: Categorized data is exported, and `verl` is invoked for SFT or GRPO training.

## 🛠️ Customization Potential

The project is designed for extensions:
- **Custom Tasks**: Inherit from `BaseTaskConfig` and `BaseTaskExecutor`.
- **Custom Rewriting**: Inherit from `BaseRewriteConfig` and `BaseRewriter`.
- **New Models**: Easily add any OpenAI-compatible provider via configuration.
