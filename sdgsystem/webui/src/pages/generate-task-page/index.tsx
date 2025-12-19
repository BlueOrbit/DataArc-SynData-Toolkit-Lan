import { EventStreamContentType, fetchEventSource } from '@microsoft/fetch-event-source'
import { message } from 'antd'
import { useEffect, useRef } from 'react'
import { useSmoothProgress } from '@/hooks/use-smooth-progress'
import { type SSEEventData, useTaskStore } from '@/store/use-task-store'
import { CustomProgressBar } from './components/custom-progress-bar'
import { OutputPanel } from './components/output-panel'
import { ProcessStepsPanel } from './components/process-steps-panel'
import { TaskInfoBar } from './components/task-info-bar'

export default function GenerateTaskPage() {
  const {
    taskId,
    eventData,
    getTargetProgress,
    setEventData,
    setIsGenerating,
    isGenerating,
    setIsRefining,
    setRefineEventData,
    isRefining,
    refineEventData,
    pauseTimer,
    resumeTimer,
    startTimer,
    setGenerationSSEConnected,
    setRefineSSEConnected,
    hasConnectedGeneration,
    setHasConnectedGeneration,
  } = useTaskStore()

  const generationAbortControllerRef = useRef<AbortController | null>(null)
  const generationShouldStopRef = useRef(false)
  const generationConnectionCountRef = useRef(0)

  const refineAbortControllerRef = useRef<AbortController | null>(null)
  const refineShouldStopRef = useRef(false)
  const refineConnectionCountRef = useRef(0)

  const targetProgress = getTargetProgress(isRefining ? refineEventData : eventData)

  const displayProgress = useSmoothProgress(targetProgress, {
    initialProgress: 0,
    baseSpeed: 0.5,
    minSpeed: 0.1,
    maxSpeed: 2,
  })

  interface SSEConnectionConfig {
    jobId: string
    endpoint: 'generate' | 'refine'
    onComplete: () => void
    onEventData: (data: SSEEventData) => void
    shouldStopRef: React.MutableRefObject<boolean>
    connectionCountRef: React.MutableRefObject<number>
    abortControllerRef: React.MutableRefObject<AbortController | null>
    setIsConnected: (connected: boolean) => void
    completeEventType: string
  }

  const connectSSE = async (config: SSEConnectionConfig) => {
    const {
      jobId,
      endpoint,
      onComplete,
      onEventData,
      shouldStopRef,
      connectionCountRef,
      abortControllerRef,
      setIsConnected,
      completeEventType,
    } = config

    const controller = new AbortController()
    abortControllerRef.current = controller
    setIsConnected(true)

    await fetchEventSource(`/api/sdg/${jobId}/${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
      openWhenHidden: true,

      async onopen(response) {
        if (shouldStopRef.current) {
          throw new Error('Connection stopped by user')
        }

        if (connectionCountRef.current > 0) {
          throw new Error('Duplicate connection not allowed')
        }

        if (response.ok) {
          const contentType = response.headers.get('content-type')
          if (
            contentType === EventStreamContentType ||
            contentType?.includes('text/event-stream')
          ) {
            connectionCountRef.current += 1
            return
          } else {
            connectionCountRef.current += 1
            return
          }
        } else if (response.status >= 400 && response.status < 500 && response.status !== 429) {
          throw new Error(`Client error: ${response.status}`)
        } else {
          throw new Error(`Unexpected response: ${response.status}`)
        }
      },

      onmessage(msg) {
        if (msg.event === 'FatalError') {
          throw new Error(msg.data)
        }

        if (!msg.data) return

        try {
          const parsedData = JSON.parse(msg.data) as SSEEventData
          onEventData(parsedData)

          const isComplete =
            msg.event === 'complete' ||
            msg.event === 'generation_complete' ||
            parsedData.status === completeEventType

          if (isComplete) {
            shouldStopRef.current = true
            onComplete()
            controller.abort()
            setIsConnected(false)
          }
        } catch (_e) {
          // Silently handle parse errors
        }
      },

      onclose() {
        setIsConnected(false)
        if (shouldStopRef.current) {
          throw new Error('Connection closed - stop requested')
        }
        throw new Error('Connection closed')
      },

      onerror(err) {
        setIsConnected(false)
        if (shouldStopRef.current) {
          throw new Error('Connection error - stop requested')
        }
        throw err
      },
    })
  }

  const handleStartRefine = async () => {
    const currentTaskId = useTaskStore.getState().taskId

    if (!currentTaskId) {
      message.error('Task ID not found, cannot start Refine')
      return
    }

    try {
      refineShouldStopRef.current = false
      refineConnectionCountRef.current = 0
      setIsRefining(true)

      resumeTimer()

      await connectSSE({
        jobId: currentTaskId,
        endpoint: 'refine',
        completeEventType: 'completed',
        onComplete: async () => {
          message.success('Rewrite and evaluation completed')
          setIsRefining(false)
          pauseTimer()
        },
        onEventData: setRefineEventData,
        shouldStopRef: refineShouldStopRef,
        connectionCountRef: refineConnectionCountRef,
        abortControllerRef: refineAbortControllerRef,
        setIsConnected: setRefineSSEConnected,
      })
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      if (refineAbortControllerRef.current?.signal.aborted) {
        // User aborted the refine request
      } else {
        message.error(`Failed to start Refine: ${error.message}`)
      }
      setIsRefining(false)
    }
  }

  // biome-ignore lint/correctness/useExhaustiveDependencies: connectSSE and store methods are stable across renders
  useEffect(() => {
    if (taskId && isGenerating && !hasConnectedGeneration) {
      setHasConnectedGeneration(true)

      const startGeneration = async () => {
        try {
          generationShouldStopRef.current = false
          generationConnectionCountRef.current = 0

          startTimer()

          await connectSSE({
            jobId: taskId,
            endpoint: 'generate',
            completeEventType: 'generation_complete',
            onComplete: async () => {
              message.success('Data generation completed')
              setIsGenerating(false)
              pauseTimer()
            },
            onEventData: setEventData,
            shouldStopRef: generationShouldStopRef,
            connectionCountRef: generationConnectionCountRef,
            abortControllerRef: generationAbortControllerRef,
            setIsConnected: setGenerationSSEConnected,
          })
        } catch (err) {
          const error = err instanceof Error ? err : new Error(String(err))
          message.error(`Failed to connect to generation task: ${error.message}`)
          setIsGenerating(false)
          setHasConnectedGeneration(false)
        }
      }

      startGeneration()
    }

    return () => {
      if (generationAbortControllerRef.current) {
        generationShouldStopRef.current = true
        generationAbortControllerRef.current.abort()
      }
    }
    // biome-ignore lint/correctness/useExhaustiveDependencies: hasConnectedGeneration should not trigger re-run
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId, isGenerating])

  const getProgressStatus = () => {
    if (refineEventData?.status === 'completed') {
      return 'success'
    }
    if (refineEventData?.status === 'error' || refineEventData?.status === 'failed') {
      return 'exception'
    }
    if (
      eventData?.status === 'generation_complete' ||
      eventData?.status === 'complete' ||
      eventData?.status === 'completed'
    ) {
      return 'success'
    }
    if (eventData?.status === 'error' || eventData?.status === 'failed') {
      return 'exception'
    }
    return 'active'
  }

  return (
    <>
      <TaskInfoBar />
      <CustomProgressBar percent={displayProgress} status={getProgressStatus()} />

      <div className="p-6">
        <div className="grid h-full grid-cols-12 gap-6">
          <ProcessStepsPanel onStartRefine={handleStartRefine} />
          <OutputPanel />
        </div>
      </div>
    </>
  )
}
