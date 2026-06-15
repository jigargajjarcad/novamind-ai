import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import PageWrapper from '../components/layout/PageWrapper'
import CollectionList from '../components/collections/CollectionList'
import CreateCollectionModal from '../components/collections/CreateCollectionModal'
import Button from '../components/shared/Button'
import collectionService from '../services/collectionService'

export default function Dashboard() {
  const [showCreate, setShowCreate] = useState(false)
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const { data: collections = [], isLoading, error } = useQuery({
    queryKey: ['collections'],
    queryFn: collectionService.list,
  })

  const createMutation = useMutation({
    mutationFn: collectionService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collections'] })
      setShowCreate(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: collectionService.delete,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['collections'] }),
  })

  return (
    <PageWrapper title="My Collections">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">My Collections</h1>
          <p className="text-gray-400 text-sm mt-1">
            Organize your documents into collections and start asking questions.
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)}>+ New Collection</Button>
      </div>

      <CollectionList
        collections={collections}
        isLoading={isLoading}
        error={error}
        onSelect={(id) => navigate(`/collections/${id}`)}
        onDelete={(id) => deleteMutation.mutate(id)}
      />

      {showCreate && (
        <CreateCollectionModal
          onClose={() => setShowCreate(false)}
          onSubmit={(data) => createMutation.mutate(data)}
          isLoading={createMutation.isPending}
          error={createMutation.error?.response?.data?.error?.message}
        />
      )}
    </PageWrapper>
  )
}
