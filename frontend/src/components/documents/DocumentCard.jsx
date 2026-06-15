import Badge from '../shared/Badge'
import ProcessingStatus from './ProcessingStatus'

const STATUS_BADGE = {
  pending: 'default',
  processing: 'info',
  ready: 'success',
  failed: 'error',
}

export default function DocumentCard({ document, onDelete }) {
  const sizeMb = document.file_size_bytes
    ? (document.file_size_bytes / 1024 / 1024).toFixed(1)
    : null

  return (
    <div className="flex items-center gap-4 bg-gray-900 border border-gray-800 rounded-lg px-4 py-3">
      <div className="shrink-0 text-2xl">📄</div>

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white truncate">{document.filename}</p>
        <div className="flex items-center gap-3 mt-1">
          <Badge variant={STATUS_BADGE[document.status] ?? 'default'}>{document.status}</Badge>
          {sizeMb && <span className="text-gray-500 text-xs">{sizeMb} MB</span>}
          {document.page_count && (
            <span className="text-gray-500 text-xs">{document.page_count} pages</span>
          )}
        </div>
        {(document.status === 'processing' || document.status === 'pending') && (
          <ProcessingStatus status={document.status} className="mt-2" />
        )}
        {document.status === 'failed' && document.error_message && (
          <p className="text-red-400 text-xs mt-1 truncate">{document.error_message}</p>
        )}
      </div>

      <button
        onClick={() => {
          if (window.confirm(`Delete "${document.filename}"?`)) onDelete(document.id)
        }}
        className="text-gray-600 hover:text-red-400 text-xs shrink-0 transition-colors"
      >
        Delete
      </button>
    </div>
  )
}
