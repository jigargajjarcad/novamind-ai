export default function CollectionCard({ collection, onSelect, onDelete }) {
  const updatedAt = new Date(collection.updated_at).toLocaleDateString()

  return (
    <div
      className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-gray-600 transition-colors cursor-pointer group"
      onClick={() => onSelect(collection.id)}
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="font-semibold text-white group-hover:text-indigo-300 transition-colors truncate pr-2">
          {collection.name}
        </h3>
        <button
          onClick={(e) => {
            e.stopPropagation()
            if (window.confirm(`Delete "${collection.name}" and all its documents?`)) {
              onDelete(collection.id)
            }
          }}
          className="text-gray-600 hover:text-red-400 text-xs shrink-0 transition-colors"
        >
          Delete
        </button>
      </div>

      {collection.description && (
        <p className="text-gray-400 text-sm mb-3 line-clamp-2">{collection.description}</p>
      )}

      <p className="text-gray-500 text-xs">Updated {updatedAt}</p>
    </div>
  )
}
