import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import documentService from '../services/documentService'

export function useDocuments(collectionId) {
  return useQuery({
    queryKey: ['documents', collectionId],
    queryFn: () => documentService.listByCollection(collectionId),
    enabled: !!collectionId,
    refetchInterval: (query) => {
      const data = query.state.data
      const hasPending = Array.isArray(data) && data.some((d) => d.status === 'pending' || d.status === 'processing')
      return hasPending ? 3000 : false
    },
  })
}

export function useDocument(documentId) {
  return useQuery({
    queryKey: ['document', documentId],
    queryFn: () => documentService.getById(documentId),
    enabled: !!documentId,
  })
}

export function useUploadDocument(collectionId) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ file, onUploadProgress }) =>
      documentService.upload(collectionId, file, onUploadProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', collectionId] })
    },
  })
}

export function useDeleteDocument(collectionId) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (documentId) => documentService.delete(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', collectionId] })
    },
  })
}
