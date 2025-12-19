import { type ThemeConfig, theme } from 'antd'
import { componentConfig } from '../components'
import { darkTokens } from '../tokens'

export const darkTheme: ThemeConfig = {
  token: darkTokens,
  components: componentConfig,
  cssVar: { key: 'app' },
  hashed: true,

  // 使用暗色算法
  algorithm: theme.darkAlgorithm,
}
