import { useState } from 'react'
import CitationCard from './CitationCard'

export default function MessageBubble({ message }) {
  const [showCitations, setShowCitations] = useState(false)
  const isUser = message.role === 'user'
  const hasCitations = message.citations?.length > 0

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
            isUser
              ? 'bg-indigo-600 text-white rounded-br-sm'
              : message.isError
              ? 'bg-red-900/30 border border-red-500/30 text-red-300 rounded-bl-sm'
              : 'bg-gray-800 text-gray-100 rounded-bl-sm'
          }`}
        >
          {message.content}
          {message.isStreaming && (
            <span className="inline-block w-1 h-4 bg-indigo-400 ml-1 animate-pulse align-middle" />
          )}
        </div>

        {hasCitations && (
          <div className="mt-2">
            <button
              onClick={() => setShowCitations((v) => !v)}
              className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              {showCitations ? '▾ Hide sources' : `▸ ${message.citations.length} source${message.citations.length !== 1 ? 's' : ''}`}
            </button>
            {showCitations && (
              <div className="mt-2 space-y-2">
                {message.citations.map((c, i) => (
                  <CitationCard key={c.id ?? i} citation={c} index={i + 1} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
