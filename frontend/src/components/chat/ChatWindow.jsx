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
  // Refs track accumulated values so onDone closure always reads the final state
  const streamingTextRef = useRef('')
  const citationsRef = useRef([])

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
    streamingTextRef.current = ''
    citationsRef.current = []

    stream({
      url: chatService.getMessageStreamUrl(session.id),
      body: { content },
      onChunk: (text) => {
        streamingTextRef.current += text
        setStreamingText((prev) => prev + text)
      },
      onCitations: (data) => {
        citationsRef.current = data
        setCitations(data)
      },
      onDone: (doneData) => {
        setMessages((prev) => [
          ...prev,
          {
            id: doneData?.message_id ?? Date.now() + 1,
            role: 'assistant',
            content: streamingTextRef.current,
            created_at: new Date().toISOString(),
            citations: citationsRef.current,
          },
        ])
        setStreamingText('')
        setCitations([])
        queryClient.invalidateQueries({ queryKey: ['chat-session', session.id] })
      },
      onError: () => {
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
        setCitations([])
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
