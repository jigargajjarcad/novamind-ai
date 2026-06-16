import api from './api'

const authService = {
  async register(data) {
    const res = await api.post('/auth/register', data)
    return res.data
  },

  async login(data) {
    const res = await api.post('/auth/login', data)
    return res.data
  },

  async getMe() {
    const res = await api.get('/auth/me')
    return res.data
  },

  async verifyEmail(token) {
    const res = await api.post('/auth/verify-email', { token })
    return res.data
  },

  async resendVerification(email) {
    await api.post('/auth/resend-verification', { email })
  },
}

export default authService
