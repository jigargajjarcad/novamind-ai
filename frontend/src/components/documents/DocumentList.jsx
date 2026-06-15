import DocumentCard from './DocumentCard'
import Spinner from '../shared/Spinner'
import { useDocuments, useDeleteDocument } from '../../hooks/useDocuments'

export default function DocumentList({ collectionId }) {
  const { data: documents = [], isLoading, error } = useDocuments(collectionId)
  const deleteMutation = useDeleteDocument(collectionId)

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <Spinner />
      </div>
    )
  }

  if (error) {
    return <p className="text-red-400 text-sm text-center py-8">Failed to load documents.</p>
  }

  if (documents.length === 0) {
    return (
      <p className="text-gray-500 text-sm text-center py-8">
        No documents yet. Upload a PDF above to get started.
      </p>
    )
  }

  return (
    <div className="space-y-2">
      <h2 className="text-sm font-medium text-gray-400 mb-3">
        {documents.length} document{documents.length !== 1 ? 's' : ''}
      </h2>
      {documents.map((doc) => (
        <DocumentCard
          key={doc.id}
          document={doc}
          onDelete={(id) => deleteMutation.mutate(id)}
        />
      ))}
    </div>
  )
}
