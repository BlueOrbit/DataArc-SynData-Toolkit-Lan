import { Typography } from 'antd'
import { useEffect, useState } from 'react'
import taskNameIcon from '@/assets/icon/task-name.svg?react'
import totalTimeIcon from '@/assets/icon/total-time.svg?react'
import totalTokenIcon from '@/assets/icon/total-token.svg?react'
import SvgIcon from '@/components/svg-icon'
import { useAntdTheme } from '@/hooks/use-antd-theme'
import { useTaskStore } from '@/store/use-task-store'

const { Title, Text } = Typography

export function TaskInfoBar() {
  const token = useAntdTheme()
  const {
    eventData,
    refineEventData,
    currentPhase,
    accumulatedTokens,
    getCurrentElapsedTime,
    generationSSEConnected,
    refineSSEConnected,
  } = useTaskStore()

  // 前端计时器，每秒更新一次
  const [elapsedTime, setElapsedTime] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedTime(getCurrentElapsedTime())
    }, 1000)

    return () => clearInterval(interval)
  }, [getCurrentElapsedTime])

  // 格式化时间（秒转换为更易读的格式）
  const formatTime = (seconds: number) => {
    const roundedSeconds = Math.floor(seconds)
    if (roundedSeconds < 60) return `${roundedSeconds}s`
    const minutes = Math.floor(roundedSeconds / 60)
    const remainingSeconds = roundedSeconds % 60
    return `${minutes}m ${remainingSeconds}s`
  }

  // 格式化 token 数量（千位分隔符）
  const formatTokens = (tokens: number) => {
    return tokens.toLocaleString()
  }

  // 获取状态文本
  const getStatusText = (status?: string) => {
    if (status === 'generation_complete' || status === 'complete' || status === 'completed') {
      return 'Success'
    }
    if (status === 'running') {
      return 'Running'
    }
    if (status === 'error' || status === 'failed') {
      return 'Error'
    }
    return 'Pending'
  }

  // 获取状态颜色（使用主题变量）
  const getStatusColor = (status?: string) => {
    if (status === 'running') {
      return token.colorSuccess // running 使用 success 颜色（绿色）
    }
    if (status === 'generation_complete' || status === 'complete' || status === 'completed') {
      return token.colorPrimary // success 使用 primary 颜色（蓝色）
    }
    if (status === 'error' || status === 'failed') {
      return token.colorError // error 使用 error 颜色（红色）
    }
    return token.colorTextSecondary // pending 使用次要文本颜色
  }

  // 根据当前阶段确定使用哪个事件数据
  const currentEventData = currentPhase === 'refine' ? refineEventData : eventData

  // 从当前阶段的事件数据中获取任务信息
  const taskName = currentEventData?.task_name || eventData?.task_name || 'DEMO TASK NAME'
  const taskType = currentEventData?.task_type || eventData?.task_type || 'local'
  const status = currentEventData?.status || 'pending'

  // 根据当前阶段确定 SSE 连接状态（未使用，但保留以备将来使用）
  // @ts-expect-error - Variable is intentionally unused but kept for future use
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _isSSEConnected = currentPhase === 'refine' ? refineSSEConnected : generationSSEConnected

  // 根据当前阶段获取估算剩余时间和token
  const estimatedRemainingTokens = currentEventData?.step?.usage?.estimated_remaining_tokens || 0
  const estimatedRemainingTime = currentEventData?.step?.usage?.estimated_remaining_time || 0

  return (
    <div
      className="flex items-center justify-between border-b px-8 py-4"
      style={{ background: token.colorBgContainer, borderColor: token.colorBorderSecondary }}
    >
      <div className="flex flex-col gap-6">
        <section className="flex flex-col gap-2">
          <div className="flex items-center gap-4">
            <SvgIcon icon={taskNameIcon} />
            <Title level={3} style={{ margin: 0 }}>
              {taskName}
            </Title>
          </div>

          <div className="flex items-center gap-3">
            <div
              className="inline-flex w-fit items-center gap-2 rounded border px-3 py-1"
              style={{ borderColor: token.colorBorderSecondary }}
            >
              <span style={{ color: getStatusColor(status), fontSize: '8px', lineHeight: 1 }}>
                ●
              </span>
              <span style={{ color: token.colorTextSecondary, fontSize: token.fontSizeSM }}>
                {taskType === 'local' ? 'Local Task' : taskType}
              </span>
              <span
                style={{
                  color: getStatusColor(status),
                  fontSize: token.fontSizeSM,
                  fontWeight: 500,
                }}
              >
                {getStatusText(status)}
              </span>
            </div>

            {/* SSE 连接状态标签 */}
            {/* <div
              className="inline-flex w-fit items-center gap-2 rounded border px-3 py-1"
              style={{
                borderColor: isSSEConnected ? token.colorSuccessBorder : token.colorBorderSecondary,
                backgroundColor: isSSEConnected
                  ? token.colorSuccessBg
                  : token.colorFillQuaternary,
              }}
            >
              <span
                style={{
                  color: isSSEConnected ? token.colorSuccess : token.colorTextTertiary,
                  fontSize: '8px',
                  lineHeight: 1,
                }}
              >
                ●
              </span>
              <span
                style={{
                  color: isSSEConnected ? token.colorSuccess : token.colorTextTertiary,
                  fontSize: token.fontSizeSM,
                  fontWeight: 500,
                }}
              >
                SSE {isSSEConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div> */}
          </div>
        </section>
        {eventData?.step?.message && (
          <div className="ml-4 flex gap-4">
            <Text type="secondary">{eventData.step.message}</Text>
          </div>
        )}
      </div>

      <div className="flex w-[30%] max-w-[300px] flex-col gap-2">
        <div className="flex items-center justify-between gap-1">
          <div className="flex items-center gap-1">
            <SvgIcon icon={totalTimeIcon} size={18} />
            <span className="font-medium text-sm" style={{ color: token.colorTextSecondary }}>
              Duration
            </span>
          </div>

          <div className="flex items-baseline gap-1">
            <span className="font-bold font-mono text-lg" style={{ color: token.colorPrimary }}>
              {formatTime(elapsedTime)}
            </span>
            {estimatedRemainingTime > 0 && (
              <Text type="secondary" style={{ fontSize: token.fontSize - 2 }}>
                (~ {formatTime(estimatedRemainingTime)} left)
              </Text>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between gap-1">
          <div className="flex items-center gap-1">
            <SvgIcon icon={totalTokenIcon} size={18} />
            <span className="font-medium text-sm" style={{ color: token.colorTextSecondary }}>
              Token
            </span>
          </div>
          <div className="flex items-baseline gap-1">
            <span className="font-bold font-mono text-lg" style={{ color: token.colorPrimary }}>
              {formatTokens(accumulatedTokens)}
            </span>
            {estimatedRemainingTokens > 0 && (
              <Text type="secondary" style={{ fontSize: token.fontSize - 2 }}>
                (~ {formatTokens(estimatedRemainingTokens)} left)
              </Text>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
