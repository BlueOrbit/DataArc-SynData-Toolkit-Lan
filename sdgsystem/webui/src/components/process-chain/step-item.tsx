import { Flex, Typography } from 'antd'
import { useAntdTheme } from '@/hooks/use-antd-theme'
import type { SSEUsage } from '@/store/use-task-store'
import { StatusIcon } from './status-icon'
import type { StepStatus } from './types'

const { Text } = Typography

export interface StepItemProps {
  /** 步骤标题 */
  title: string
  /** 步骤描述 */
  description?: string
  /** 步骤状态 */
  status: StepStatus
  /** 统计信息（包含已使用和预计消耗） */
  stats?: SSEUsage
  /** 步骤结果（包含 datasets_to_use 等） */
  result?: any
}

/**
 * 步骤项组件
 */
export function StepItem({ title, description, status, stats, result }: StepItemProps) {
  const token = useAntdTheme()

  // 格式化时间（秒转为友好格式）
  const formatTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${seconds.toFixed(1)}s`
    }
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.floor(seconds % 60)
    return `${minutes}m ${remainingSeconds}s`
  }

  // 格式化 token 数量（添加千分位分隔符）
  const formatTokens = (tokens: number): string => {
    return tokens.toLocaleString()
  }

  const getTitleColor = () => {
    switch (status) {
      case 'error':
        return token.colorError
      case 'pending':
        return token.colorTextSecondary
      default:
        return token.colorText
    }
  }

  const getTopSectionStyle = () => {
    const baseStyle = {
      borderRadius: token.borderRadius,
    }

    switch (status) {
      case 'loading':
        return {
          ...baseStyle,
          border: `1px solid ${token.colorPrimary}`,
          padding: `${token.paddingXS}px ${token.paddingSM}px`,
          // 添加渐变背景和 blink 动画
          background: `linear-gradient(90deg, ${token.colorPrimaryBg} 0%, ${token.colorPrimaryBgHover} 50%, ${token.colorPrimaryBg} 100%)`,
          backgroundSize: '200% 100%',
          animation: 'blink 2s linear infinite',
        }
      case 'error':
        return {
          ...baseStyle,
          border: `1px solid ${token.colorError}`,
          backgroundColor: token.colorErrorBg,
          padding: `${token.paddingXS}px ${token.paddingSM}px`,
        }
      case 'success':
        return {
          ...baseStyle,
          border: `1px solid #E7E9E9`,
          backgroundColor: '#F3F4F4',
          padding: `${token.paddingXS}px ${token.paddingSM}px`,
        }
      default:
        return {
          padding: `${token.paddingXS}px 0`,
        }
    }
  }

  return (
    <Flex vertical gap={token.marginXS}>
      <Flex gap={token.marginXS} align="center" style={getTopSectionStyle()}>
        <StatusIcon status={status} />

        <Text style={{ color: getTitleColor(), fontWeight: 500 }}>{title}</Text>
      </Flex>

      <Flex vertical gap={token.marginXXS} style={{ paddingLeft: token.paddingMD }}>
        {description && (
          <Text type="secondary" style={{ fontSize: token.fontSize }}>
            {description}
          </Text>
        )}

        {status === 'success' &&
          result?.datasets_to_use &&
          Array.isArray(result.datasets_to_use) && (
            <Text
              type="secondary"
              style={{
                fontSize: token.fontSizeSM,
                wordBreak: 'break-word',
                whiteSpace: 'normal',
              }}
            >
              Datasets used: {result.datasets_to_use.join(', ')}
            </Text>
          )}

        {stats && (
          <Flex vertical gap={2}>
            <Text type="secondary" style={{ fontSize: token.fontSizeSM }}>
              Used: {formatTokens(stats.tokens)} tokens | {formatTime(stats.time)}
            </Text>
            {status !== 'success' && (
              <Text type="secondary" style={{ fontSize: token.fontSizeSM }}>
                Estimated remaining: {formatTokens(stats.estimated_remaining_tokens)} tokens |{' '}
                {formatTime(stats.estimated_remaining_time)}
              </Text>
            )}
          </Flex>
        )}
      </Flex>
    </Flex>
  )
}
