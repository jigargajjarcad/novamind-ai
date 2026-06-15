import { useCallback, useEffect, useRef, useState } from 'react'
import { useAuthStore } from '../store/authStore'

export function useSSE() {
  const [streaming, setStreaming] = useState(false)
  const eventSourceRef = useRef(null)
  const token = useAuthStore((s) => s.token)

  const close = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
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
            const err = await res.json().catch(() => ({ message: 'Stream error' }))
            onError?.(err)
            setStreaming(false)
            return
          }

          const reader = res.body.getReader()
          const decoder = new TextDecoder()
          let buffer = ''

          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            buffer = lines.pop() ?? ''

            for (const line of lines) {
              if (!line.startsWith('data: ')) continue
              const raw = line.slice(6).trim()
              if (!raw || raw === '[DONE]') continue

              try {
                const parsed = JSON.parse(raw)
                if (parsed.type === 'chunk') onChunk?.(parsed.text)
                if (parsed.type === 'citations') onCitations?.(parsed.data)
                if (parsed.type === 'done') {
                  onDone?.(parsed.data)
                  setStreaming(false)
                }
              } catch {
                // non-JSON SSE line — ignore
              }
            }
          }
          setStreaming(false)
        })
        .catch((err) => {
          onError?.(err)
          setStreaming(false)
        })
    },
    [token, close],
  )

  return { stream, streaming, close }
}
