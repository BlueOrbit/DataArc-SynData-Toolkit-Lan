import { CheckCircleOutlined, CloseOutlined, LoadingOutlined } from '@ant-design/icons'
import { useAntdTheme } from '@/hooks/use-antd-theme'
import type { StepStatus } from './types'

export interface StatusIconProps {
  /** 状态 */
  status: StepStatus
  /** 图标大小，默认使用 fontSizeSM (12px) */
  size?: number
}

/**
 * 状态图标组件
 */
export function StatusIcon({ status, size }: StatusIconProps) {
  const token = useAntdTheme()
  const iconSize = size ?? token.fontSizeSM

  switch (status) {
    case 'loading':
      return <LoadingOutlined style={{ color: token.colorPrimary, fontSize: iconSize }} spin />
    case 'success':
      return <CheckCircleOutlined style={{ color: token.colorSuccess, fontSize: iconSize }} />
    case 'error':
      return <CloseOutlined style={{ color: token.colorError, fontSize: iconSize }} />
    default:
      return null
  }
}
