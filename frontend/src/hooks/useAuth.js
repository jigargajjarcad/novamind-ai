import { useAuthStore } from '../store/authStore'
import authService from '../services/authService'

export function useAuth() {
  const { user, token, setAuth, clearAuth } = useAuthStore()

  async function login(credentials) {
    const { token } = await authService.login(credentials)
    setAuth(token, null)
    const user = await authService.getMe()
    setAuth(token, user)
    return user
  }

  async function register(data) {
    // Registration no longer auto-logs in — user must verify email first
    const { user } = await authService.register(data)
    return user
  }

  async function verifyEmail(token) {
    const { token: jwt } = await authService.verifyEmail(token)
    setAuth(jwt, null)
    const user = await authService.getMe()
    setAuth(jwt, user)
    return user
  }

  function logout() {
    clearAuth()
  }

  return {
    user,
    token,
    isAuthenticated: !!token,
    login,
    register,
    verifyEmail,
    logout,
  }
}
