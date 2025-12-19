# Synth-Data Web

> Frontend visualization interface for [DataArc-SynData-Toolkit](https://github.com/DataArcTech/DataArc-SynData-Toolkit) - providing interactive operations for synthetic data generation workflow.

[![React](https://img.shields.io/badge/React-19.2-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue.svg)](https://www.typescriptlang.org/)
[![Ant Design](https://img.shields.io/badge/Ant%20Design-6.0-1890ff.svg)](https://ant.design/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg)](https://vitejs.dev/)

English | [简体中文](./README_zh.md)

## 📖 Overview

Synth-Data Web is the **frontend demonstration interface for DataArc-SynData-Toolkit**, providing intuitive visual operations for configuring and monitoring synthetic data generation tasks. Core algorithms and functionality are implemented in the backend.

### Key Features

- 🎯 **Multi-Source Generation**: Local PDFs, HuggingFace datasets, knowledge distillation
- 🤖 **Multiple LLM Providers**: OpenAI, Anthropic, Google, and custom providers
- 📊 **Real-time Monitoring**: SSE-based live task progress updates
- 🔄 **Two-Stage Workflow**: Data generation → Refinement & evaluation
- 💾 **Result Download**: Download by quality category (Raw/Solved/Learnable/Unsolved)
- 🧪 **Training Configuration**: SFT/GRPO fine-tuning config and log monitoring
- 🎨 **Modern UI**: Responsive design with dark/light theme support

## 🚀 Quick Start

### Prerequisites

- Node.js >= 18.0.0
- pnpm >= 8.0.0
- Backend server running on `http://localhost:8000`

### Installation

```bash
cd sdgsystem/webui

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

The application will be available at `http://localhost:5173`

### Build for Production

```bash
# Build the project
pnpm build

# Preview production build
pnpm preview
```

## 📁 Project Structure

```
webui/
├── src/
│   ├── api/                    # API service layer
│   ├── assets/                 # Static assets (icons, images)
│   ├── components/            # Reusable components
│   │   ├── custom-upload/     # File upload component
│   │   ├── generation-core-modal/  # Core configuration modal
│   │   ├── process-chain/     # Process visualization
│   │   └── svg-icon/          # SVG icon wrapper
│   ├── config/                # Configuration files
│   │   └── theme/             # Theme system (tokens, light/dark)
│   ├── contexts/              # React Context providers
│   ├── hooks/                 # Custom React hooks
│   ├── layout/                # Layout components
│   ├── pages/                 # Page components
│   │   ├── home-page/         # Landing page
│   │   ├── configuration-page/  # Task configuration
│   │   ├── generate-task-page/  # Task execution monitoring
│   │   └── training-page/       # Training config, logs, and export
│   ├── store/                 # State management (Zustand)
│   ├── styles/                # Global styles
│   ├── types/                 # TypeScript type definitions
│   └── utils/                 # Utility functions
├── public/                    # Public assets
├── docs/                      # Documentation
└── package.json               # Project dependencies
```

## 🛠️ Tech Stack

- **React 19** + **TypeScript 5.9** - Type-safe modern frontend development
- **Vite 6** - Lightning-fast build tool
- **Ant Design 6** + **TailwindCSS 3.4** - UI components and styling
- **Zustand 5** - Lightweight state management
- **Axios** + **SSE** - API communication and real-time updates
- **Biome** - Code formatting and linting

## 🎯 Workflow

```
Home → Configuration (LLM + Task Parameters) → Generation (Real-time Monitoring) → Download Results
                                                        ↓
                                      Optional: Training Page (SFT/GRPO Training)
```

## 📊 Available Scripts

| Script | Description |
|--------|-------------|
| `pnpm dev` | Start development server with hot reload |
| `pnpm build` | Build for production |
| `pnpm preview` | Preview production build |
| `pnpm check` | Run linter and formatter |

## 🔧 Backend Configuration

Ensure backend service is running on `http://localhost:8000`. The frontend automatically proxies API requests.

To modify backend URL: Edit `server.proxy` configuration in `vite.config.ts`.

## 📝 Development Notes

- Import aliases: Use `@/` for cross-directory imports, relative paths for local imports
- Code style: Use Biome for formatting and linting
- Theme system: Supports design tokens and dark/light theme switching
- Detailed docs: Check `/docs` directory

## 🔗 Related Projects

- [DataArc-SynData-Toolkit](https://github.com/DataArcTech/DataArc-SynData-Toolkit) - Backend core algorithm engine

> **Note**: This is a frontend visualization interface. Full functionality requires running the backend service.
