import { useCallback, useEffect, useRef, useState } from 'react'
import { useAuthStore } from '../store/authStore'

export function useSSE() {
  const [streaming, setStreaming] = useState(false)
  const readerRef = useRef(null)
  const token = useAuthStore((s) => s.token)

  const close = useCallback(() => {
    readerRef.current?.cancel()
    readerRef.current = null
    setStreaming(false)
  }, [])

  useEffect(() => () => close(), [close])

  const stream = useCallback(
    ({ url, body, onChunk, onCitations, onDone, onError }) => {
      close()
      setStreaming(true)

      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      })
        .then(async (res) => {
          if (!res.ok) {
            const err = await res.json().catch(() => ({ message: 'Stream request failed' }))
            onError?.(err)
            setStreaming(false)
            return
          }

          const reader = res.body.getReader()
          readerRef.current = reader
          const decoder = new TextDecoder()
          let buffer = ''

          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            buffer += decoder.decode(value, { stream: true })

            // SSE blocks are delimited by double newline
            const blocks = buffer.split('\n\n')
            buffer = blocks.pop() ?? ''

            for (const block of blocks) {
              if (!block.trim()) continue

              let eventName = ''
              let dataStr = ''

              for (const line of block.split('\n')) {
                if (line.startsWith('event: ')) {
                  eventName = line.slice(7).trim()
                } else if (line.startsWith('data: ')) {
                  dataStr = line.slice(6).trim()
                }
              }

              if (!dataStr) continue

              try {
                const parsed = JSON.parse(dataStr)

                if (eventName === 'chunk') {
                  onChunk?.(parsed.text ?? '')
                } else if (eventName === 'citations') {
                  // parsed is the citations array directly
                  onCitations?.(Array.isArray(parsed) ? parsed : [])
                } else if (eventName === 'done') {
                  onDone?.(parsed)
                  setStreaming(false)
                } else if (eventName === 'error') {
                  onError?.(parsed)
                  setStreaming(false)
                }
              } catch {
                // non-JSON SSE data — ignore
              }
            }
          }

          setStreaming(false)
        })
        .catch((err) => {
          if (err.name !== 'AbortError') {
            onError?.({ message: err.message ?? 'Connection failed' })
          }
          setStreaming(false)
        })
    },
    [token, close],
  )

  return { stream, streaming, close }
}
