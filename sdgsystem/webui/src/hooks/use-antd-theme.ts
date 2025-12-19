import { theme } from 'antd'

export function useAntdTheme() {
  const { token } = theme.useToken()
  return token
}
