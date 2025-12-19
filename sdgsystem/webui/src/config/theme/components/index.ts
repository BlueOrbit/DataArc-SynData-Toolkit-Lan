import type { ThemeConfig } from 'antd'

/**
 * 组件级主题配置
 */
export const componentConfig: ThemeConfig['components'] = {
  // Button 组件
  Button: {
    controlHeight: 32,
    controlHeightLG: 40,
    controlHeightSM: 24,
    borderRadius: 6,
    borderRadiusLG: 8,
    borderRadiusSM: 4,
    fontWeight: 500,
    defaultShadow: 'none',
    primaryShadow: 'none',
    dangerShadow: 'none',
  },

  // Input 组件
  Input: {
    controlHeight: 32,
    borderRadius: 6,
    paddingInline: 12,
  },

  // Select 组件
  Select: {
    controlHeight: 32,
    borderRadius: 6,
  },

  // Card 组件
  Card: {
    borderRadius: 8,
  },

  // Table 组件
  Table: {
    borderRadius: 8,
  },

  // Modal 组件
  Modal: {
    borderRadius: 8,
  },

  // Tooltip 组件 - 深色主题
  Tooltip: {
    colorBgSpotlight: 'rgba(0, 0, 0, 0.85)', // 黑色背景，85% 不透明度
    colorTextLightSolid: '#ffffff', // 白色文字
  },
}
