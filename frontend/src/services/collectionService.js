import api from './api'

const collectionService = {
  async list() {
    const res = await api.get('/collections')
    return res.data
  },

  async getById(id) {
    const res = await api.get(`/collections/${id}`)
    return res.data
  },

  async create(data) {
    const res = await api.post('/collections', data)
    return res.data
  },

  async update(id, data) {
    const res = await api.put(`/collections/${id}`, data)
    return res.data
  },

  async delete(id) {
    await api.delete(`/collections/${id}`)
  },
}

export default collectionService
