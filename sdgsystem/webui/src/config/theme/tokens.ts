import type { ThemeConfig } from 'antd'

/**
 * 基础 Design Tokens
 * 遵循 Ant Design v6 Design Token 系统
 */
export const baseTokens = {
  // 主色
  colorPrimary: '#524AC9',
  colorSuccess: '#057C4A',
  colorWarning: '#faad14',
  colorError: '#D40F02',
  colorInfo: '#1677ff',
  colorLink: '#1677ff', // 链接色

  // 文本色
  colorTextBase: '#000000',
  colorTextSecondary: 'rgba(0, 0, 0, 0.65)',
  colorTextTertiary: 'rgba(0, 0, 0, 0.45)',
  colorTextQuaternary: 'rgba(0, 0, 0, 0.25)',

  // 圆角系统
  borderRadiusSM: 4, // 小圆角
  borderRadius: 6, // 基础圆角
  borderRadiusLG: 8, // 大圆角
  borderRadiusXS: 2, // 超小圆角
  borderRadiusOuter: 4, // 外层圆角
  borderRadiusCircle: 9999, // 圆形圆角

  // 字体系统
  fontSizeSM: 12, // 小号文字
  fontSize: 14, // 基础文字
  fontSizeLG: 16, // 大号文字
  fontSizeXL: 20, // 特大文字
  fontSizeHeading1: 38, // 标题1
  fontSizeHeading2: 30, // 标题2
  fontSizeHeading3: 24, // 标题3
  fontSizeHeading4: 20, // 标题4
  fontSizeHeading5: 16, // 标题5
  fontFamily:
    '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',

  // 行高系统
  lineHeight: 1.5715, // 基础行高
  lineHeightLG: 1.5, // 大号行高
  lineHeightSM: 1.66, // 小号行高
  lineHeightHeading1: 1.2105, // 标题1行高
  lineHeightHeading2: 1.2666, // 标题2行高
  lineHeightHeading3: 1.3333, // 标题3行高
  lineHeightHeading4: 1.4, // 标题4行高
  lineHeightHeading5: 1.5, // 标题5行高

  // 间距系统
  marginXXS: 4, // 超超小间距
  marginXS: 8, // 超小间距
  marginSM: 12, // 小间距
  margin: 16, // 基础间距
  marginMD: 20, // 中等间距
  marginLG: 24, // 大间距
  marginXL: 32, // 超大间距
  marginXXL: 48, // 超超大间距

  paddingXXS: 4, // 超超小内边距
  paddingXS: 8, // 超小内边距
  paddingSM: 12, // 小内边距
  padding: 16, // 基础内边距
  paddingMD: 20, // 中等内边距
  paddingLG: 24, // 大内边距
  paddingXL: 32, // 超大内边距

  // 特性
  wireframe: false, // v6 新增: 启用/禁用线框模式
}

/**
 * 浅色主题 Tokens
 */
export const lightTokens: ThemeConfig['token'] = {
  ...baseTokens,

  // 链接色
  colorLink: '#1677ff',
  colorLinkHover: '#4096ff',
  colorLinkActive: '#0958d9',

  // 背景色
  colorBgBase: '#ffffff',
  colorBgContainer: '#ffffff',
  colorBgElevated: '#ffffff',
  colorBgLayout: '#FAFAFA',
  colorBgSpotlight: '#fafafa', // 高亮背景（如表格头部）

  // 填充色（用于悬停、禁用等状态）
  colorFillAlter: '#fafafa', // 替代填充色
  colorFillSecondary: '#f5f5f5', // 次要填充色
  colorFillTertiary: '#f0f0f0', // 三级填充色
  colorFillQuaternary: '#e6e6e6', // 四级填充色

  // 边框色
  colorBorder: '#d9d9d9',
  colorBorderSecondary: '#f0f0f0',

  // 分割线色
  colorSplit: 'rgba(5, 5, 5, 0.06)',

  // 文本色（继承 baseTokens，但可以在这里覆盖）
  colorTextBase: '#000000',
  colorTextSecondary: 'rgba(0, 0, 0, 0.65)',
  colorTextTertiary: 'rgba(0, 0, 0, 0.45)',
  colorTextQuaternary: 'rgba(0, 0, 0, 0.25)',

  // 自定义主色浅色变体（用于背景等）
  colorPrimaryBg: 'rgba(82, 74, 201, 0.05)', // primary/5 - 5% 透明度的主色背景
  colorPrimaryBgHover: 'rgba(82, 74, 201, 0.08)', // primary/8 - 悬停态
}

/**
 * 暗色主题 Tokens
 */
export const darkTokens: ThemeConfig['token'] = {
  ...baseTokens,

  // 主色调整（暗色模式下稍微调暗）
  colorPrimary: '#1668dc',

  // 链接色
  colorLink: '#1668dc',
  colorLinkHover: '#3c89e8',
  colorLinkActive: '#0f5fd1',

  // 背景色
  colorBgBase: '#141414',
  colorBgContainer: '#1f1f1f',
  colorBgElevated: '#262626',
  colorBgLayout: '#000000',
  colorBgSpotlight: '#262626', // 高亮背景

  // 填充色
  colorFillAlter: '#1f1f1f',
  colorFillSecondary: '#262626',
  colorFillTertiary: '#2c2c2c',
  colorFillQuaternary: '#333333',

  // 边框色
  colorBorder: '#424242',
  colorBorderSecondary: '#303030',

  // 分割线色
  colorSplit: 'rgba(253, 253, 253, 0.12)',

  // 文本色
  colorTextBase: '#ffffff',
  colorTextSecondary: 'rgba(255, 255, 255, 0.65)',
  colorTextTertiary: 'rgba(255, 255, 255, 0.45)',
  colorTextQuaternary: 'rgba(255, 255, 255, 0.25)',

  // 自定义主色浅色变体（用于背景等）
  colorPrimaryBg: 'rgba(22, 104, 220, 0.05)', // primary/5 - 5% 透明度的主色背景（暗色主题用暗色主色）
  colorPrimaryBgHover: 'rgba(22, 104, 220, 0.08)', // primary/8 - 悬停态
}
