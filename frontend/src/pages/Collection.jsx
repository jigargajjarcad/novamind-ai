import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import PageWrapper from '../components/layout/PageWrapper'
import DocumentList from '../components/documents/DocumentList'
import UploadDropzone from '../components/documents/UploadDropzone'
import Button from '../components/shared/Button'
import collectionService from '../services/collectionService'
import chatService from '../services/chatService'
import { useDocuments, useUploadDocument } from '../hooks/useDocuments'

export default function Collection() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const uploadMutation = useUploadDocument(id)

  const { data: collection, isLoading } = useQuery({
    queryKey: ['collection', id],
    queryFn: () => collectionService.getById(id),
  })

  const { data: documents = [] } = useDocuments(id)

  const readyCount = documents.filter((d) => d.status === 'ready').length
  const processingCount = documents.filter((d) => d.status === 'pending' || d.status === 'processing').length
  const canChat = readyCount > 0

  const createSessionMutation = useMutation({
    mutationFn: () => chatService.createSession({ collection_id: id, name: `Session ${new Date().toLocaleDateString()}` }),
    onSuccess: (session) => navigate(`/chat/${session.id}`),
  })

  return (
    <PageWrapper title={collection?.name ?? 'Collection'}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <button
            onClick={() => navigate('/dashboard')}
            className="text-gray-400 hover:text-white text-sm mb-2 inline-flex items-center gap-1 transition-colors"
          >
            ← Collections
          </button>
          <h1 className="text-2xl font-bold text-white">{collection?.name ?? '…'}</h1>
          {collection?.description && (
            <p className="text-gray-400 text-sm mt-1">{collection.description}</p>
          )}
        </div>

        <div className="flex flex-col items-end gap-1">
          <Button
            onClick={() => createSessionMutation.mutate()}
            disabled={createSessionMutation.isPending || !canChat}
            title={!canChat ? 'Upload and process at least one document before chatting' : undefined}
          >
            {createSessionMutation.isPending ? 'Starting…' : 'Start Chat →'}
          </Button>
          {!canChat && documents.length > 0 && processingCount > 0 && (
            <p className="text-xs text-yellow-500">
              {processingCount} document{processingCount !== 1 ? 's' : ''} still processing…
            </p>
          )}
          {!canChat && documents.length === 0 && (
            <p className="text-xs text-gray-500">Upload a document to get started</p>
          )}
        </div>
      </div>

      <UploadDropzone
        collectionId={id}
        onUpload={(file, onProgress) => uploadMutation.mutate({ file, onUploadProgress: onProgress })}
        isUploading={uploadMutation.isPending}
      />

      <div className="mt-6">
        <DocumentList collectionId={id} />
      </div>
    </PageWrapper>
  )
}
