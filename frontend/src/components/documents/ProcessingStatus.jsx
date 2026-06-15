import Spinner from '../shared/Spinner'

export default function ProcessingStatus({ status, className = '' }) {
  const label = status === 'processing' ? 'Processing PDF…' : 'Queued for processing…'

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Spinner size="sm" />
      <span className="text-xs text-gray-400">{label}</span>
    </div>
  )
}
