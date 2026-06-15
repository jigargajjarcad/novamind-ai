import PageWrapper from '../components/layout/PageWrapper'

export default function Admin() {
  return (
    <PageWrapper title="Admin">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Usage & Cost Dashboard</h1>
        <p className="text-gray-400 text-sm mt-1">Token usage, query latency, and cost per user.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center">
        <p className="text-gray-400 text-sm">Admin panel — implemented in Week 4.</p>
        <p className="text-gray-500 text-xs mt-2">
          Will show: total tokens used, cost per user, query log with latency.
        </p>
      </div>
    </PageWrapper>
  )
}
