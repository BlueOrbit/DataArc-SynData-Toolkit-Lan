import { useAntdTheme } from '@/hooks/use-antd-theme'

interface CustomProgressBarProps {
  percent: number // 0-100，可以是小数
  status?: 'active' | 'success' | 'exception'
}

export function CustomProgressBar({ percent }: CustomProgressBarProps) {
  const token = useAntdTheme()

  const clampedPercent = Math.min(Math.max(percent, 0), 100)
  // 显示时保留一位小数
  const displayPercent = clampedPercent.toFixed(1)

  return (
    <div
      className="relative w-full overflow-hidden"
      style={{
        height: '14px',
        background: token.colorFillSecondary,
        borderRadius: 0,
      }}
    >
      <div
        className="absolute top-0 left-0 h-full"
        style={{
          width: `${clampedPercent}%`,
          background: token.colorPrimary,
          borderTopRightRadius: clampedPercent >= 100 ? 0 : '100px',
          borderBottomRightRadius: clampedPercent >= 100 ? 0 : '100px',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* 条纹动画 */}
        <div
          className="absolute inset-0 animate-progress-stripes"
          style={{
            backgroundImage: `linear-gradient(
              45deg,
              rgba(255, 255, 255, 0.15) 25%,
              transparent 25%,
              transparent 50%,
              rgba(255, 255, 255, 0.15) 50%,
              rgba(255, 255, 255, 0.15) 75%,
              transparent 75%,
              transparent
            )`,
            backgroundSize: '40px 40px',
          }}
        />

        {clampedPercent > 0 && (
          <span
            className="-translate-y-1/2 absolute top-1/2 whitespace-nowrap font-medium text-xs"
            style={{
              right: '8px',
              color: 'white',
              textShadow: '0 0 2px rgba(0, 0, 0, 0.3)',
              zIndex: 10,
            }}
          >
            {displayPercent}%
          </span>
        )}
      </div>
    </div>
  )
}
