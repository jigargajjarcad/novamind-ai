const VARIANTS = {
  default: 'bg-gray-700 text-gray-300',
  info: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
  success: 'bg-green-500/20 text-green-400 border border-green-500/30',
  error: 'bg-red-500/20 text-red-400 border border-red-500/30',
  warning: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
}

export default function Badge({ children, variant = 'default' }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${VARIANTS[variant]}`}>
      {children}
    </span>
  )
}
