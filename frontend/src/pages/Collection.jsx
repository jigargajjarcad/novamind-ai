import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import PageWrapper from '../components/layout/PageWrapper'
import DocumentList from '../components/documents/DocumentList'
import UploadDropzone from '../components/documents/UploadDropzone'
import Button from '../components/shared/Button'
import collectionService from '../services/collectionService'
import chatService from '../services/chatService'
import { useUploadDocument } from '../hooks/useDocuments'

export default function Collection() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const uploadMutation = useUploadDocument(id)

  const { data: collection, isLoading } = useQuery({
    queryKey: ['collection', id],
    queryFn: () => collectionService.getById(id),
  })

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
        <Button
          onClick={() => createSessionMutation.mutate()}
          disabled={createSessionMutation.isPending}
        >
          {createSessionMutation.isPending ? 'Starting…' : 'Start Chat →'}
        </Button>
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
