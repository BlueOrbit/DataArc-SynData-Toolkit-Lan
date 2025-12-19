import { EventStreamContentType, fetchEventSource } from '@microsoft/fetch-event-source'
import { useCallback, useEffect, useRef, useState } from 'react'

export interface SSEOptions {
  method?: 'GET' | 'POST'
  headers?: Record<string, string>
  body?: any
  autoReconnect?: boolean
}

export interface UseSSEReturn<T> {
  data: T | null
  isConnected: boolean
  error: Error | null
  start: () => Promise<void>
  stop: () => void
}

export function useSSE<T = any>(
  url: string,
  options?: SSEOptions,
  onMessageCallback?: (data: T) => void,
): UseSSEReturn<T> {
  const [data, setData] = useState<T | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const abortControllerRef = useRef<AbortController | null>(null)

  const stop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setIsConnected(false)
  }, [])

  const start = useCallback(async () => {
    if (isConnected) return

    setError(null)
    setIsConnected(true)

    const controller = new AbortController()
    abortControllerRef.current = controller

    try {
      await fetchEventSource(url, {
        method: options?.method ?? 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        body: options?.body ? JSON.stringify(options.body) : undefined,
        signal: controller.signal,

        async onopen(response) {
          if (response.ok && response.headers.get('content-type') === EventStreamContentType) {
            return
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
            const parsedData = JSON.parse(msg.data)
            setData(parsedData)
            if (onMessageCallback) {
              onMessageCallback(parsedData)
            }
          } catch (_e) {}
        },

        onclose() {
          setIsConnected(false)
          if (!options?.autoReconnect) {
          }
        },

        onerror(err) {
          setError(err instanceof Error ? err : new Error(String(err)))
          if (!options?.autoReconnect) {
            throw err
          }
        },
      })
    } catch (err) {
      if (controller.signal.aborted) {
      } else {
        setError(err instanceof Error ? err : new Error(String(err)))
      }
      setIsConnected(false)
    }
  }, [url, options, isConnected, onMessageCallback])

  useEffect(() => {
    return () => {
      stop()
    }
  }, [stop])

  return { data, isConnected, error, start, stop }
}
