import CollectionCard from './CollectionCard'
import Spinner from '../shared/Spinner'

export default function CollectionList({ collections, isLoading, error, onSelect, onDelete }) {
  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-16 text-red-400 text-sm">
        Failed to load collections. Please refresh.
      </div>
    )
  }

  if (collections.length === 0) {
    return (
      <div className="text-center py-16 border border-dashed border-gray-700 rounded-xl">
        <p className="text-gray-400 mb-2">No collections yet</p>
        <p className="text-gray-500 text-sm">Create a collection to start uploading documents.</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {collections.map((c) => (
        <CollectionCard key={c.id} collection={c} onSelect={onSelect} onDelete={onDelete} />
      ))}
    </div>
  )
}
