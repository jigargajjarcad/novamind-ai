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
    const { user, token } = await authService.register(data)
    setAuth(token, user)
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
    logout,
  }
}
