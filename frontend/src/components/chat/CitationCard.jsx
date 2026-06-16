export default function CitationCard({ citation, index }) {
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 text-xs">
      <div className="flex items-center justify-between mb-1.5">
        <span className="font-medium text-indigo-400">[{index}] {citation.filename ?? 'Document'}</span>
        {citation.page_number && (
          <span className="text-gray-500">Page {citation.page_number}</span>
        )}
      </div>
      {citation.content && (
        <p className="text-gray-400 line-clamp-3 leading-relaxed">&ldquo;{citation.content}&rdquo;</p>
      )}
    </div>
  )
}
