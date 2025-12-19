import { ThoughtChain, type ThoughtChainItemType } from '@ant-design/x'
import { Flex } from 'antd'
import thoughtChainIcon from '@/assets/icon/thought-chain.svg?react'
import { useAntdTheme } from '@/hooks/use-antd-theme'
import SvgIcon from '../svg-icon'
import { StepItem } from './step-item'
import type { StepItemData, StepStatus } from './types'

export interface ProcessChainProps {
  /** 阶段唯一标识 */
  itemKey: string
  /** 阶段标题 */
  title: string
  /** 阶段描述 */
  description?: string
  /** 阶段整体状态 */
  status?: StepStatus
  /** 步骤列表 */
  steps: StepItemData[]
  /** 是否默认展开 */
  defaultExpanded?: boolean
  /** 受控：是否展开 */
  expanded?: boolean
  /** 受控：展开状态变化回调 */
  onExpandedChange?: (expanded: boolean) => void
}

export default function ProcessChain({
  itemKey,
  title,
  description,
  status: _status = 'pending',
  steps,
  defaultExpanded = true,
  expanded,
  onExpandedChange,
}: ProcessChainProps) {
  const token = useAntdTheme()

  const stageIcon = <SvgIcon icon={thoughtChainIcon} size={token.fontSizeLG} />

  const chainItems: ThoughtChainItemType[] = [
    {
      key: itemKey,
      title,
      description,
      collapsible: true,
      icon: stageIcon,
      content: (
        <Flex gap="middle" vertical>
          {steps.map(step => (
            <StepItem
              key={step.key}
              title={step.title}
              description={step.description}
              status={step.status}
              stats={step.stats}
              result={step.result}
            />
          ))}
        </Flex>
      ),
    },
  ]

  const isControlled = expanded !== undefined

  const handleExpand = (keys: string[]) => {
    if (isControlled && onExpandedChange) {
      onExpandedChange(keys.includes(itemKey))
    }
  }

  return (
    <div style={{ width: '80%' }}>
      {isControlled ? (
        <ThoughtChain
          items={chainItems}
          expandedKeys={expanded ? [itemKey] : []}
          onExpand={handleExpand}
        />
      ) : (
        <ThoughtChain items={chainItems} defaultExpandedKeys={defaultExpanded ? [itemKey] : []} />
      )}
    </div>
  )
}
