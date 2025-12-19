import { Button, message, Typography } from 'antd'
import { useEffect, useRef, useState } from 'react'
import ProcessChain from '@/components/process-chain'
import type { StepItemData, StepStatus } from '@/components/process-chain/types'
import { useTaskStore } from '@/store/use-task-store'

const { Title, Text } = Typography

export interface ProcessStepsPanelProps {
  onStartRefine: () => Promise<void>
}

export function ProcessStepsPanel({ onStartRefine }: ProcessStepsPanelProps) {
  const { eventData, refineEventData, stepHistory, config, generationCompleted, isRefining } =
    useTaskStore()

  const [refineLoading, setRefineLoading] = useState(false)
  const [generationExpanded, setGenerationExpanded] = useState(true)

  const hasShownGenerationErrorRef = useRef(false)
  const hasShownRefineErrorRef = useRef(false)

  const generationSteps: StepItemData[] = Object.values(stepHistory)
    .filter(step => step.phaseId === 'generation')
    .map(step => ({
      key: step.id,
      title: step.name,
      description: step.status === 'success' ? undefined : step.message || undefined,
      status: step.status,
      stats: step.usage || undefined,
      result: step.result || undefined,
    }))

  const refineSteps: StepItemData[] = Object.values(stepHistory)
    .filter(step => step.phaseId === 'refinement')
    .map(step => ({
      key: step.id,
      title: step.name,
      description: step.status === 'success' ? undefined : step.message || undefined,
      status: step.status,
      stats: step.usage || undefined,
      result: step.result || undefined,
    }))

  const generationPhaseName = eventData?.phase?.name || 'Generating Dataset'
  const generationPhaseStatus = eventData?.phase?.status || 'pending'
  const generationPhaseId = eventData?.phase?.id

  const refinePhaseName = refineEventData?.phase?.name || 'Refining & Evaluating'
  const refinePhaseStatus = refineEventData?.phase?.status || 'pending'
  const refinePhaseId = refineEventData?.phase?.id

  const getPhaseDescription = (phaseId?: string): string | undefined => {
    if (phaseId === 'generation') {
      return 'Execute files needed for creating new component'
    } else if (phaseId === 'refinement') {
      return 'Refine and evaluate generated data'
    }
    return undefined
  }

  const getPhaseStepStatus = (status: string): StepStatus => {
    switch (status) {
      case 'running':
        return 'loading'
      case 'completed':
        return 'success'
      case 'error':
      case 'failed':
        return 'error'
      default:
        return 'pending'
    }
  }

  const hasGenerationError = eventData?.status === 'error' || eventData?.status === 'failed'
  const hasRefineError = refineEventData?.status === 'error' || refineEventData?.status === 'failed'

  useEffect(() => {
    if (hasGenerationError && !hasShownGenerationErrorRef.current) {
      message.error('Please reconfigure and create a new task')
      hasShownGenerationErrorRef.current = true
    }
    if (!hasGenerationError) {
      hasShownGenerationErrorRef.current = false
    }
  }, [hasGenerationError])

  useEffect(() => {
    if (hasRefineError && !hasShownRefineErrorRef.current) {
      message.error('Please reconfigure and create a new task')
      hasShownRefineErrorRef.current = true
    }
    if (!hasRefineError) {
      hasShownRefineErrorRef.current = false
    }
  }, [hasRefineError])

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
  }

  const handleRefineAndEvaluate = async () => {
    if (refineLoading) return

    setGenerationExpanded(false)

    setRefineLoading(true)
    try {
      await onStartRefine()
    } finally {
      setRefineLoading(false)
    }
  }

  const showRefineButton = generationCompleted && !isRefining && refineSteps.length === 0

  return (
    <div className="col-span-4 flex flex-col gap-4">
      {eventData?.phase ? (
        <div className="mb-2">
          <Title level={4} style={{ margin: 0 }}>
            Generating <span className="text-primary">{config.task.num_samples}</span> data samples
            using <span className="text-primary">{config.llm.model}</span> ...
          </Title>
          <Text type="secondary" className="text-xs">
            {eventData?.created_at ? formatTime(eventData.created_at) : '--:--'}
          </Text>
        </div>
      ) : null}

      <div className="flex flex-col gap-4">
        {eventData?.phase ? (
          <ProcessChain
            itemKey="generation-phase"
            title={generationPhaseName}
            description={getPhaseDescription(generationPhaseId)}
            status={getPhaseStepStatus(generationPhaseStatus)}
            steps={generationSteps}
            expanded={generationExpanded}
            onExpandedChange={setGenerationExpanded}
          />
        ) : (
          <Text type="secondary">Waiting for task to start...</Text>
        )}

        {showRefineButton && (
          <Button
            type="primary"
            size="large"
            block
            onClick={handleRefineAndEvaluate}
            loading={refineLoading}
            disabled={refineLoading}
          >
            Execute Rewrite & Evaluate Task
          </Button>
        )}

        {refineEventData?.phase && (
          <ProcessChain
            itemKey="refine-phase"
            title={refinePhaseName}
            description={getPhaseDescription(refinePhaseId)}
            status={getPhaseStepStatus(refinePhaseStatus)}
            steps={refineSteps}
            defaultExpanded={true}
          />
        )}
      </div>
    </div>
  )
}
