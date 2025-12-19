# Synth-Data Web

> Frontend visualization interface for [DataArc-SynData-Toolkit](https://github.com/DataArcTech/DataArc-SynData-Toolkit), for demonstrating and interactively operating the synthetic data generation workflow.

[![React](https://img.shields.io/badge/React-19.2-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue.svg)](https://www.typescriptlang.org/)
[![Ant Design](https://img.shields.io/badge/Ant%20Design-6.0-1890ff.svg)](https://ant.design/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg)](https://vitejs.dev/)

English | [简体中文](./WEBUI_zh.md)

## 📖 Overview

Synth-Data Web is the **frontend demonstration interface for DataArc-SynData-Toolkit**, providing intuitive visual operations that allow users to easily configure and monitor synthetic data generation tasks. Core algorithms and functionality are implemented by the backend.

### Key Features

- 🎯 **Multi-Source Data Generation**: Support for local PDF, HuggingFace datasets, and knowledge distillation
- 🤖 **Multi-Model Support**: OpenAI, Anthropic, Google, and custom providers
- 📊 **Real-Time Monitoring**: SSE-based real-time task progress updates
- 🔄 **Two-Phase Workflow**: Data Generation → Refinement & Evaluation
- 💾 **Result Download**: Support for downloading by quality classification (Raw/Solved/Learnable/Unsolved)
- 🧪 **Training Configuration**: SFT/GRPO fine-tuning configuration and log monitoring
- 🎨 **Modern Interface**: Responsive design with dark/light theme toggle

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
│   ├── api/                        # API service layer
│   ├── assets/                     # Static assets (icons, images)
│   ├── components/                 # Reusable components
│   │   ├── custom-upload/          # File upload component
│   │   ├── generation-core-modal/  # Core configuration modal
│   │   ├── process-chain/          # Process visualization component
│   │   └── svg-icon/               # SVG icon wrapper
│   ├── config/                     # Configuration files
│   │   └── theme/                  # Theme system (tokens, light/dark themes)
│   ├── contexts/                   # React Context providers
│   ├── hooks/                      # Custom React hooks
│   ├── layout/                     # Layout components
│   ├── pages/                      # Page components
│   │   ├── home-page/              # Home page
│   │   ├── configuration-page/     # Task configuration page
│   │   ├── generate-task-page/     # Task execution monitoring page
│   │   └── training-page/          # Training configuration, logs, and export
│   ├── store/                      # State management (Zustand)
│   ├── styles/                     # Global styles
│   ├── types/                      # TypeScript type definitions
│   └── utils/                      # Utility functions
├── public/                         # Public assets
├── docs/                           # Documentation
└── package.json                    # Project dependencies
```

## 🛠️ Tech Stack

- **React 19** + **TypeScript 5.9** - Type-safe modern frontend development
- **Vite 6** - Fast build tool
- **Ant Design 6** + **TailwindCSS 3.4** - UI components and styling
- **Zustand 5** - Lightweight state management
- **Axios** + **SSE** - API communication and real-time updates
- **Biome** - Code formatting and linting

## 🎯 User Workflow

```
Home Page → Configuration Page (LLM + Task Parameters) → Generation Page (Real-time Monitoring) → Download Results
                                            ↓
                              Optional: Training Page (SFT/GRPO Training)
```

## 📊 Available Commands

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start development server (with hot reload) |
| `pnpm build` | Production build |
| `pnpm preview` | Preview production build |
| `pnpm check` | Run code linting and formatting |

## 🔧 Backend Configuration

Ensure the backend server is running on `http://localhost:8000`, and the frontend will automatically proxy API requests.

To modify the backend address: Edit the `server.proxy` configuration in `vite.config.ts`.

## 📝 Development Notes

- Import aliases: Use `@/` for cross-directory imports, use relative paths for same-level imports
- Code style: Use Biome for formatting and linting
- Theme system: Supports design tokens and dark/light theme toggle
- Detailed documentation: See the `/docs` directory

> **Note**: This project is the frontend visualization interface. Full functionality requires running the backend service.
