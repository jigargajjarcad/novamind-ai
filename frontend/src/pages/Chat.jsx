import { useParams, useNavigate } from 'react-router-dom'
import { useChatSession } from '../hooks/useChat'
import ChatWindow from '../components/chat/ChatWindow'
import SessionList from '../components/chat/SessionList'
import Spinner from '../components/shared/Spinner'

export default function Chat() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const { data: session, isLoading, error } = useChatSession(sessionId)

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <Spinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">Session not found or access denied.</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="text-indigo-400 hover:text-indigo-300 text-sm"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-950 flex">
      <aside className="w-64 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-gray-400 hover:text-white text-sm transition-colors"
          >
            ← Dashboard
          </button>
        </div>
        <SessionList activeSessionId={sessionId} collectionId={session?.collection_id} />
      </aside>

      <main className="flex-1 flex flex-col min-h-0">
        <header className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
          <h1 className="font-semibold text-white">{session?.name ?? 'Chat'}</h1>
        </header>
        <ChatWindow session={session} />
      </main>
    </div>
  )
}
