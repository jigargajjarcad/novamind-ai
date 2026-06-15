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
}

export default authService
