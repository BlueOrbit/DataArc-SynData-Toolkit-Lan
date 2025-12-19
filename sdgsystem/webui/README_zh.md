# Synth-Data Web

> [DataArc-SynData-Toolkit](https://github.com/DataArcTech/DataArc-SynData-Toolkit) 的前端可视化界面，用于演示和交互式操作合成数据生成流程。

[![React](https://img.shields.io/badge/React-19.2-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue.svg)](https://www.typescriptlang.org/)
[![Ant Design](https://img.shields.io/badge/Ant%20Design-6.0-1890ff.svg)](https://ant.design/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg)](https://vitejs.dev/)

[English](./README.md) | 简体中文

## 📖 项目简介

Synth-Data Web 是 **DataArc-SynData-Toolkit 的前端演示界面**，提供直观的可视化操作，让用户能够轻松配置和监控合成数据生成任务。核心算法和功能由后端实现。

### 主要特性

- 🎯 **多源数据生成**：支持本地 PDF、HuggingFace 数据集、知识蒸馏
- 🤖 **多模型支持**：OpenAI、Anthropic、Google 及自定义提供商
- 📊 **实时监控**：基于 SSE 的任务进度实时更新
- 🔄 **两阶段流程**：数据生成 → 精炼评估
- 💾 **结果下载**：支持按质量分类下载（Raw/Solved/Learnable/Unsolved）
- 🧪 **训练配置**：SFT/GRPO 微调配置与日志监控
- 🎨 **现代界面**：响应式设计，支持暗黑/明亮主题切换

## 🚀 快速开始

### 前置要求

- Node.js >= 18.0.0
- pnpm >= 8.0.0
- 后端服务运行在 `http://localhost:8000`

### 安装

```bash
cd sdgsystem/webui

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

应用将在 `http://localhost:5173` 上运行

### 生产构建

```bash
# 构建项目
pnpm build

# 预览生产构建
pnpm preview
```

## 📁 项目结构

```
webui/
├── src/
│   ├── api/                    # API 服务层
│   ├── assets/                 # 静态资源（图标、图片）
│   ├── components/            # 可复用组件
│   │   ├── custom-upload/     # 文件上传组件
│   │   ├── generation-core-modal/  # 核心配置模态框
│   │   ├── process-chain/     # 流程可视化组件
│   │   └── svg-icon/          # SVG 图标封装
│   ├── config/                # 配置文件
│   │   └── theme/             # 主题系统（Token、明暗主题）
│   ├── contexts/              # React Context 提供者
│   ├── hooks/                 # 自定义 React Hooks
│   ├── layout/                # 布局组件
│   ├── pages/                 # 页面组件
│   │   ├── home-page/         # 首页
│   │   ├── configuration-page/  # 任务配置页
│   │   ├── generate-task-page/  # 任务执行监控页
│   │   └── training-page/       # 训练配置、日志与导出
│   ├── store/                 # 状态管理（Zustand）
│   ├── styles/                # 全局样式
│   ├── types/                 # TypeScript 类型定义
│   └── utils/                 # 工具函数
├── public/                    # 公共资源
├── docs/                      # 文档
└── package.json               # 项目依赖
```

## 🛠️ 技术栈

- **React 19** + **TypeScript 5.9** - 类型安全的现代前端开发
- **Vite 6** - 快速构建工具
- **Ant Design 6** + **TailwindCSS 3.4** - UI 组件与样式
- **Zustand 5** - 轻量级状态管理
- **Axios** + **SSE** - API 通信与实时更新
- **Biome** - 代码格式化与检查

## 🎯 使用流程

```
首页 → 配置页面（LLM + 任务参数）→ 生成页面（实时监控）→ 下载结果
                                            ↓
                              可选：Training 页面（SFT/GRPO 训练）
```

## 📊 可用命令

| 命令 | 说明 |
|------|------|
| `pnpm dev` | 启动开发服务器（支持热重载） |
| `pnpm build` | 生产环境构建 |
| `pnpm preview` | 预览生产构建 |
| `pnpm check` | 运行代码检查和格式化 |

## 🔧 后端配置

确保后端服务运行在 `http://localhost:8000`，前端会自动代理 API 请求。

修改后端地址：编辑 `vite.config.ts` 中的 `server.proxy` 配置。

## 📝 开发说明

- 导入别名：跨目录使用 `@/`，同级使用相对路径
- 代码风格：使用 Biome 进行格式化和 Linting
- 主题系统：支持设计 Token、明暗主题切换
- 详细文档：查看 `/docs` 目录

## 🔗 相关项目

- [DataArc-SynData-Toolkit](https://github.com/DataArcTech/DataArc-SynData-Toolkit) - 后端核心算法引擎

> **注意**：本项目为前端可视化界面，完整功能需要运行后端服务。
