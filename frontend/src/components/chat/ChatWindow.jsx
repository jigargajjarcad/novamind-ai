import { useEffect, useRef, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import MessageBubble from './MessageBubble'
import MessageInput from './MessageInput'
import { useSSE } from '../../hooks/useSSE'
import chatService from '../../services/chatService'

export default function ChatWindow({ session }) {
  const queryClient = useQueryClient()
  const { stream, streaming } = useSSE()
  const [messages, setMessages] = useState(session?.messages ?? [])
  const [streamingText, setStreamingText] = useState('')
  const [citations, setCitations] = useState([])
  const bottomRef = useRef(null)

  useEffect(() => {
    setMessages(session?.messages ?? [])
  }, [session?.id])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingText])

  function sendMessage(content) {
    const userMsg = { id: Date.now(), role: 'user', content, created_at: new Date().toISOString() }
    setMessages((prev) => [...prev, userMsg])
    setStreamingText('')
    setCitations([])

    stream({
      url: chatService.getMessageStreamUrl(session.id),
      body: { content },
      onChunk: (text) => setStreamingText((prev) => prev + text),
      onCitations: (data) => setCitations(data),
      onDone: () => {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            role: 'assistant',
            content: streamingText,
            created_at: new Date().toISOString(),
            citations,
          },
        ])
        setStreamingText('')
        queryClient.invalidateQueries({ queryKey: ['chat-session', session.id] })
      },
      onError: (err) => {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            role: 'assistant',
            content: 'Sorry, something went wrong. Please try again.',
            created_at: new Date().toISOString(),
            isError: true,
          },
        ])
        setStreamingText('')
      },
    })
  }

  return (
    <div className="flex flex-col flex-1 min-h-0">
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6 scrollbar-thin">
        {messages.length === 0 && !streaming && (
          <div className="text-center py-16">
            <p className="text-gray-400 text-sm">Ask a question about the documents in this collection.</p>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {streaming && streamingText && (
          <MessageBubble
            message={{ role: 'assistant', content: streamingText, isStreaming: true }}
          />
        )}

        <div ref={bottomRef} />
      </div>

      <MessageInput onSend={sendMessage} disabled={streaming} />
    </div>
  )
}
