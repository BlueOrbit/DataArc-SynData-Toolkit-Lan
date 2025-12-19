import type { ThemeConfig } from 'antd'
import { componentConfig } from '../components'
import { lightTokens } from '../tokens'

export const lightTheme: ThemeConfig = {
  token: lightTokens,
  components: componentConfig,

  // v6 新增: CSS Variable 配置
  cssVar: { key: 'app' }, // 启用 CSS Variables

  // v6 新增: Hash 优先级配置
  hashed: true,

  // 算法 (可选)
  algorithm: undefined, // 默认算法
}
