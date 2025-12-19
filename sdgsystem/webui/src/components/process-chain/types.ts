import type { SSEUsage } from '@/store/use-task-store'

export type StepStatus = 'pending' | 'loading' | 'success' | 'error'

export interface StepItemData {
  key: string
  title: string
  description?: string
  status: StepStatus
  stats?: SSEUsage
  result?: any
  subSteps?: StepItemData[]
}
