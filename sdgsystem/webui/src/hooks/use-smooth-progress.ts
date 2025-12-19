import { useEffect, useRef, useState } from 'react'

/**
 * 平滑进度条 hook
 * 实现从当前值平滑过渡到目标值的动画效果
 *
 * @param targetProgress 目标进度（0-100）
 * @param options 配置选项
 * @returns 当前显示的进度值
 */
export function useSmoothProgress(
  targetProgress: number,
  options: {
    /** 初始进度值 */
    initialProgress?: number
    /** 基础递增速率（每帧增加的百分比），默认 0.5 */
    baseSpeed?: number
    /** 最小速率，防止进度增长太慢，默认 0.1 */
    minSpeed?: number
    /** 最大速率，防止进度增长太快，默认 2 */
    maxSpeed?: number
  } = {},
) {
  const { initialProgress = 0, baseSpeed = 0.5, minSpeed = 0.1, maxSpeed = 2 } = options

  const [displayProgress, setDisplayProgress] = useState(initialProgress)
  const rafRef = useRef<number | undefined>(undefined)
  const lastUpdateTimeRef = useRef<number>(Date.now())

  useEffect(() => {
    // 如果目标进度大幅下降（从高到低，比如从 99 到 0），立即重置
    if (targetProgress < displayProgress - 50) {
      setDisplayProgress(targetProgress)
      lastUpdateTimeRef.current = Date.now()
      return
    }

    if (Math.abs(targetProgress - displayProgress) < 0.1) {
      setDisplayProgress(targetProgress)
      return
    }

    // 开始动画
    const animate = (_timestamp: number) => {
      setDisplayProgress(current => {
        const diff = targetProgress - current

        if (Math.abs(diff) < 0.1) {
          return targetProgress
        }

        const now = Date.now()
        const timeDelta = now - lastUpdateTimeRef.current
        lastUpdateTimeRef.current = now

        const frameRateAdjustment = timeDelta / 16

        let speed = baseSpeed * frameRateAdjustment

        if (Math.abs(diff) > 10) {
          speed = Math.min(maxSpeed * frameRateAdjustment, Math.abs(diff) * 0.1)
        } else if (Math.abs(diff) < 5) {
          speed = Math.max(minSpeed * frameRateAdjustment, Math.abs(diff) * 0.05)
        }

        const increment = diff > 0 ? Math.min(speed, diff) : Math.max(-speed, diff)

        return current + increment
      })

      rafRef.current = requestAnimationFrame(animate)
    }

    rafRef.current = requestAnimationFrame(animate)

    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
      }
    }
  }, [targetProgress, baseSpeed, minSpeed, maxSpeed, displayProgress])

  return Math.min(100, Math.max(0, displayProgress))
}
