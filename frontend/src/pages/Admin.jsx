import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import PageWrapper from '../components/layout/PageWrapper'
import { useAuthStore } from '../store/authStore'
import adminService from '../services/adminService'

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  )
}

function fmt(n, decimals = 0) {
  if (n == null) return '—'
  return Number(n).toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

function fmtCost(usd) {
  if (usd == null) return '—'
  return `$${Number(usd).toFixed(4)}`
}

function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' })
}

export default function Admin() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)

  useEffect(() => {
    if (user && !user.is_admin) {
      navigate('/dashboard', { replace: true })
    }
  }, [user, navigate])
  const { data: usage, isLoading: usageLoading } = useQuery({
    queryKey: ['admin-usage'],
    queryFn: adminService.getUsage,
    refetchInterval: 30_000,
  })

  const { data: logData, isLoading: logLoading } = useQuery({
    queryKey: ['admin-queries'],
    queryFn: adminService.getQueryLog,
    refetchInterval: 30_000,
  })

  const summary = usage?.summary ?? {}
  const byUser = usage?.by_user ?? []
  const queries = logData?.queries ?? []
  const currentUserId = usage?.current_user_id ?? null
  const myUsage = usage?.my_usage ?? null

  return (
    <PageWrapper title="Admin">
      <div className="mb-6">
        <button
          onClick={() => navigate('/dashboard')}
          className="text-gray-400 hover:text-white text-sm mb-2 inline-flex items-center gap-1 transition-colors"
        >
          ← Back to Collections
        </button>
        <h1 className="text-2xl font-bold text-white">Usage &amp; Cost Dashboard</h1>
        <p className="text-gray-400 text-sm mt-1">Token usage, query latency, and cost per user.</p>
      </div>

      {/* My Usage */}
      {(myUsage || usageLoading) && (
        <div className="mb-6">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide mb-3">My Usage</h2>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            <StatCard
              label="My Queries"
              value={usageLoading ? '…' : fmt(myUsage?.query_count ?? 0)}
            />
            <StatCard
              label="My Tokens"
              value={usageLoading ? '…' : fmt((myUsage?.total_input_tokens ?? 0) + (myUsage?.total_output_tokens ?? 0))}
              sub={myUsage ? `${fmt(myUsage.total_input_tokens)} in · ${fmt(myUsage.total_output_tokens)} out` : undefined}
            />
            <StatCard
              label="My Cost"
              value={usageLoading ? '…' : fmtCost(myUsage?.total_cost_usd ?? 0)}
            />
          </div>
        </div>
      )}

      {/* Platform summary stats */}
      <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide mb-3">Platform Totals</h2>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Total Queries"
          value={usageLoading ? '…' : fmt(summary.total_queries)}
        />
        <StatCard
          label="Total Tokens"
          value={usageLoading ? '…' : fmt((summary.total_input_tokens ?? 0) + (summary.total_output_tokens ?? 0))}
          sub={`${fmt(summary.total_input_tokens)} in · ${fmt(summary.total_output_tokens)} out`}
        />
        <StatCard
          label="Total Cost"
          value={usageLoading ? '…' : fmtCost(summary.total_cost_usd)}
        />
        <StatCard
          label="Avg Latency"
          value={usageLoading ? '…' : summary.avg_latency_ms ? `${fmt(summary.avg_latency_ms)}ms` : '—'}
        />
      </div>

      {/* Per-user breakdown */}
      <section className="mb-8">
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide mb-3">Usage by User</h2>
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          {usageLoading ? (
            <p className="p-6 text-gray-500 text-sm">Loading…</p>
          ) : byUser.length === 0 ? (
            <p className="p-6 text-gray-500 text-sm">No query data yet.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-gray-500 text-xs uppercase tracking-wide">
                  <th className="text-left px-4 py-3 font-medium">User</th>
                  <th className="text-right px-4 py-3 font-medium">Queries</th>
                  <th className="text-right px-4 py-3 font-medium">Input Tokens</th>
                  <th className="text-right px-4 py-3 font-medium">Output Tokens</th>
                  <th className="text-right px-4 py-3 font-medium">Cost</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {byUser.map((row) => {
                  const isMe = row.user_id === currentUserId
                  return (
                    <tr
                      key={row.email}
                      className={`transition-colors ${isMe ? 'bg-indigo-950/40 hover:bg-indigo-950/60' : 'hover:bg-gray-800/50'}`}
                    >
                      <td className="px-4 py-3 text-gray-300">
                        <span>{row.email}</span>
                        {isMe && (
                          <span className="ml-2 inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                            You
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right text-gray-300">{fmt(row.query_count)}</td>
                      <td className="px-4 py-3 text-right text-gray-400">{fmt(row.total_input_tokens)}</td>
                      <td className="px-4 py-3 text-right text-gray-400">{fmt(row.total_output_tokens)}</td>
                      <td className="px-4 py-3 text-right text-indigo-400 font-medium">{fmtCost(row.total_cost_usd)}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>
      </section>

      {/* Recent query log */}
      <section>
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide mb-3">Recent Queries</h2>
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          {logLoading ? (
            <p className="p-6 text-gray-500 text-sm">Loading…</p>
          ) : queries.length === 0 ? (
            <p className="p-6 text-gray-500 text-sm">No queries logged yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-800 text-gray-500 text-xs uppercase tracking-wide">
                    <th className="text-left px-4 py-3 font-medium">Query</th>
                    <th className="text-left px-4 py-3 font-medium">User</th>
                    <th className="text-right px-4 py-3 font-medium">Chunks</th>
                    <th className="text-right px-4 py-3 font-medium">Tokens</th>
                    <th className="text-right px-4 py-3 font-medium">Cost</th>
                    <th className="text-right px-4 py-3 font-medium">Latency</th>
                    <th className="text-right px-4 py-3 font-medium">Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {queries.map((q) => (
                    <tr key={q.id} className="hover:bg-gray-800/50 transition-colors">
                      <td className="px-4 py-3 text-gray-300 max-w-xs truncate" title={q.query}>{q.query}</td>
                      <td className="px-4 py-3 text-gray-500 text-xs">{q.user_email ?? '—'}</td>
                      <td className="px-4 py-3 text-right text-gray-400">{q.chunks_retrieved ?? '—'}</td>
                      <td className="px-4 py-3 text-right text-gray-400">
                        {q.input_tokens != null ? fmt(q.input_tokens + (q.output_tokens ?? 0)) : '—'}
                      </td>
                      <td className="px-4 py-3 text-right text-indigo-400">{fmtCost(q.cost_usd)}</td>
                      <td className="px-4 py-3 text-right text-gray-400">
                        {q.latency_ms != null ? `${fmt(q.latency_ms)}ms` : '—'}
                      </td>
                      <td className="px-4 py-3 text-right text-gray-500 text-xs whitespace-nowrap">{fmtDate(q.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>
    </PageWrapper>
  )
}
