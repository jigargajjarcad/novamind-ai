import api from './api'

const documentService = {
  async listByCollection(collectionId) {
    const res = await api.get(`/collections/${collectionId}/documents`)
    return res.data
  },

  async getById(documentId) {
    const res = await api.get(`/documents/${documentId}`)
    return res.data
  },

  async upload(collectionId, file, onUploadProgress) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post(`/collections/${collectionId}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress,
    })
    return res.data
  },

  async delete(documentId) {
    await api.delete(`/documents/${documentId}`)
  },
}

export default documentService
