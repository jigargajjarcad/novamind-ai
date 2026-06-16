import api from './api'

const adminService = {
  async getUsage() {
    const res = await api.get('/admin/usage')
    return res.data
  },

  async getQueryLog() {
    const res = await api.get('/admin/queries')
    return res.data
  },
}

export default adminService
