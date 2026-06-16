import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <nav className="h-14 border-b border-gray-800 flex items-center justify-between px-6 bg-gray-950 shrink-0">
      <Link
        to="/dashboard"
        className="font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent"
      >
        NovaMind AI
      </Link>

      <div className="flex items-center gap-4">
        {user?.full_name && (
          <Link to="/profile" className="text-gray-400 hover:text-white text-sm transition-colors">
            {user.full_name}
          </Link>
        )}
        {user?.is_admin && (
          <Link to="/admin" className="text-gray-400 hover:text-white text-sm transition-colors">
            Admin
          </Link>
        )}
        <button
          onClick={handleLogout}
          className="text-gray-400 hover:text-white text-sm transition-colors"
        >
          Sign out
        </button>
      </div>
    </nav>
  )
}
