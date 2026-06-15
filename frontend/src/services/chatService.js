import api from './api'

const chatService = {
  async createSession(data) {
    const res = await api.post('/chat/sessions', data)
    return res.data
  },

  async listSessions() {
    const res = await api.get('/chat/sessions')
    return res.data
  },

  async getSession(sessionId) {
    const res = await api.get(`/chat/sessions/${sessionId}`)
    return res.data
  },

  async deleteSession(sessionId) {
    await api.delete(`/chat/sessions/${sessionId}`)
  },

  getMessageStreamUrl(sessionId) {
    const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
    return `${base}/chat/sessions/${sessionId}/messages`
  },
}

export default chatService
