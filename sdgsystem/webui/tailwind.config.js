/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      // 与 Ant Design 协调的断点
      screens: {
        xs: '480px',
        sm: '576px',
        md: '768px',
        lg: '992px',
        xl: '1200px',
        '2xl': '1600px',
      },

      // 使用 Ant Design CSS 变量
      colors: {
        // 主色
        primary: 'var(--ant-color-primary)',
        secondary: 'var(--ant-color-text-secondary)', // 次要颜色（灰色调）
        success: 'var(--ant-color-success)',
        warning: 'var(--ant-color-warning)',
        error: 'var(--ant-color-error)',
        info: 'var(--ant-color-info)',

        // 文本色
        text: {
          DEFAULT: 'var(--ant-color-text)',
          secondary: 'var(--ant-color-text-secondary)',
          tertiary: 'var(--ant-color-text-tertiary)',
          quaternary: 'var(--ant-color-text-quaternary)',
        },

        // 背景色
        bg: {
          DEFAULT: 'var(--ant-color-bg-container)',
          layout: 'var(--ant-color-bg-layout)',
          elevated: 'var(--ant-color-bg-elevated)',
          spotlight: 'var(--ant-color-bg-spotlight)',
        },

        // 填充色
        fill: {
          alter: 'var(--ant-color-fill-alter)',
          secondary: 'var(--ant-color-fill-secondary)',
          tertiary: 'var(--ant-color-fill-tertiary)',
          quaternary: 'var(--ant-color-fill-quaternary)',
        },

        // 边框色
        border: {
          DEFAULT: 'var(--ant-color-border)',
          secondary: 'var(--ant-color-border-secondary)',
        },
      },
    },
  },
  plugins: [],
  // 避免与 Ant Design 的样式冲突
  corePlugins: {
    preflight: true,
  },
}
