import { useNavigate } from 'react-router-dom'
import { useChatSessions, useCreateSession, useDeleteSession } from '../../hooks/useChat'
import Spinner from '../shared/Spinner'

export default function SessionList({ activeSessionId, collectionId }) {
  const navigate = useNavigate()
  const { data: sessions = [], isLoading } = useChatSessions()
  const deleteMutation = useDeleteSession()
  const createMutation = useCreateSession()

  const filtered = collectionId
    ? sessions.filter((s) => s.collection_id === collectionId)
    : sessions

  function handleDelete(e, session) {
    e.stopPropagation()
    const isActive = session.id === activeSessionId

    deleteMutation.mutate(session.id, {
      onSuccess: () => {
        if (!isActive) return
        // Find another session to land on after deleting the active one
        const remaining = filtered.filter((s) => s.id !== session.id)
        if (remaining.length > 0) {
          navigate(`/chat/${remaining[0].id}`)
        } else {
          navigate(collectionId ? `/collections/${collectionId}` : '/dashboard')
        }
      },
    })
  }

  function handleNewSession() {
    if (!collectionId) return
    createMutation.mutate(
      { collection_id: collectionId, name: `Session ${new Date().toLocaleDateString()}` },
      { onSuccess: (session) => navigate(`/chat/${session.id}`) },
    )
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-6">
        <Spinner size="sm" />
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto flex flex-col py-2 scrollbar-thin">
      <div className="flex items-center justify-between px-4 mb-2">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Sessions</p>
        {collectionId && (
          <button
            onClick={handleNewSession}
            disabled={createMutation.isPending}
            className="text-xs text-gray-500 hover:text-indigo-400 transition-colors disabled:opacity-50"
            title="New session"
          >
            {createMutation.isPending ? '…' : '+ New'}
          </button>
        )}
      </div>

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
            onClick={(e) => handleDelete(e, session)}
            disabled={deleteMutation.isPending && deleteMutation.variables === session.id}
            className="text-gray-600 hover:text-red-400 text-xs opacity-0 group-hover:opacity-100 transition-opacity shrink-0 ml-2 disabled:opacity-30"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  )
}
