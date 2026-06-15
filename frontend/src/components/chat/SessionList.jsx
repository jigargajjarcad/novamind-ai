import { useNavigate } from 'react-router-dom'
import { useChatSessions, useDeleteSession } from '../../hooks/useChat'
import Spinner from '../shared/Spinner'

export default function SessionList({ activeSessionId, collectionId }) {
  const navigate = useNavigate()
  const { data: sessions = [], isLoading } = useChatSessions()
  const deleteMutation = useDeleteSession()

  const filtered = collectionId
    ? sessions.filter((s) => s.collection_id === collectionId)
    : sessions

  if (isLoading) {
    return (
      <div className="flex justify-center py-6">
        <Spinner size="sm" />
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto py-2 scrollbar-thin">
      <p className="px-4 text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
        Sessions
      </p>
      {filtered.length === 0 && (
        <p className="px-4 text-gray-500 text-xs">No sessions yet.</p>
      )}
      {filtered.map((session) => (
        <div
          key={session.id}
          className={`group flex items-center justify-between px-4 py-2 cursor-pointer transition-colors ${
            session.id === activeSessionId
              ? 'bg-indigo-600/20 text-indigo-300'
              : 'text-gray-400 hover:bg-gray-800 hover:text-white'
          }`}
          onClick={() => navigate(`/chat/${session.id}`)}
        >
          <span className="text-sm truncate">{session.name ?? 'Untitled session'}</span>
          <button
            onClick={(e) => {
              e.stopPropagation()
              deleteMutation.mutate(session.id)
              if (session.id === activeSessionId) navigate('/dashboard')
            }}
            className="text-gray-600 hover:text-red-400 text-xs opacity-0 group-hover:opacity-100 transition-opacity shrink-0 ml-2"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  )
}
