import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import PageWrapper from '../components/layout/PageWrapper'
import { useAuth } from '../hooks/useAuth'
import { useAuthStore } from '../store/authStore'
import authService from '../services/authService'

function Section({ title, description, children }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="mb-5">
        <h2 className="text-base font-semibold text-white">{title}</h2>
        {description && <p className="text-gray-500 text-sm mt-0.5">{description}</p>}
      </div>
      {children}
    </div>
  )
}

function InlineStatus({ status }) {
  if (!status) return null
  const isSuccess = status.type === 'success'
  return (
    <div className={`mt-4 rounded-lg px-4 py-3 text-sm ${
      isSuccess
        ? 'bg-green-900/20 border border-green-500/30 text-green-400'
        : 'bg-red-900/20 border border-red-500/30 text-red-400'
    }`}>
      {status.message}
    </div>
  )
}

function inputClass() {
  return 'w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors text-sm'
}

function labelClass() {
  return 'block text-sm font-medium text-gray-300 mb-1.5'
}

function fmt(n) {
  if (n == null) return '—'
  return Number(n).toLocaleString()
}

function fmtCost(usd) {
  if (usd == null) return '—'
  return `$${Number(usd).toFixed(4)}`
}

function fmtDateTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' })
}

export default function Profile() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { token } = useAuth()
  const setAuth = useAuthStore((s) => s.setAuth)

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: authService.getProfile,
  })

  const { data: myUsage, isLoading: usageLoading } = useQuery({
    queryKey: ['my-usage'],
    queryFn: authService.getMyUsage,
  })

  // Personal info form
  const [fullName, setFullName] = useState('')
  const [profileSaving, setProfileSaving] = useState(false)
  const [profileStatus, setProfileStatus] = useState(null)

  // Password form
  const [passwords, setPasswords] = useState({ current: '', next: '', confirm: '' })
  const [passwordSaving, setPasswordSaving] = useState(false)
  const [passwordStatus, setPasswordStatus] = useState(null)

  useEffect(() => {
    if (profile?.user?.full_name != null) {
      setFullName(profile.user.full_name)
    }
  }, [profile?.user?.full_name])

  async function handleProfileSave(e) {
    e.preventDefault()
    setProfileSaving(true)
    setProfileStatus(null)
    try {
      const updated = await authService.updateProfile({ full_name: fullName })
      setAuth(token, updated)
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      setProfileStatus({ type: 'success', message: 'Name updated successfully.' })
    } catch (err) {
      setProfileStatus({ type: 'error', message: err.response?.data?.error?.message || 'Update failed.' })
    } finally {
      setProfileSaving(false)
    }
  }

  function handlePasswordChange(field) {
    return (e) => {
      setPasswords((prev) => ({ ...prev, [field]: e.target.value }))
      setPasswordStatus(null)
    }
  }

  async function handlePasswordSave(e) {
    e.preventDefault()
    if (passwords.next !== passwords.confirm) {
      setPasswordStatus({ type: 'error', message: 'New passwords do not match.' })
      return
    }
    setPasswordSaving(true)
    setPasswordStatus(null)
    try {
      await authService.changePassword({ current_password: passwords.current, new_password: passwords.next })
      setPasswords({ current: '', next: '', confirm: '' })
      setPasswordStatus({ type: 'success', message: 'Password changed successfully.' })
    } catch (err) {
      setPasswordStatus({ type: 'error', message: err.response?.data?.error?.message || 'Password change failed.' })
    } finally {
      setPasswordSaving(false)
    }
  }

  function fmtDate(iso) {
    if (!iso) return '—'
    return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
  }

  const recentQueries = myUsage?.recent_queries ?? []

  return (
    <PageWrapper title="Profile">
      <div className="max-w-2xl">
        <div className="mb-6">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-gray-400 hover:text-white text-sm mb-2 inline-flex items-center gap-1 transition-colors"
          >
            ← Collections
          </button>
          <h1 className="text-2xl font-bold text-white">Profile</h1>
        </div>

        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((n) => (
              <div key={n} className="bg-gray-900 border border-gray-800 rounded-xl p-6 h-40 animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-4">

            {/* Personal Info */}
            <Section title="Personal info" description="Update your display name.">
              <form onSubmit={handleProfileSave} className="space-y-4">
                <div>
                  <label className={labelClass()}>Full name</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => { setFullName(e.target.value); setProfileStatus(null) }}
                    placeholder="Your name"
                    className={inputClass()}
                  />
                </div>
                <div>
                  <label className={labelClass()}>Email</label>
                  <input
                    type="email"
                    value={profile?.user?.email ?? ''}
                    readOnly
                    className={`${inputClass()} opacity-50 cursor-not-allowed`}
                  />
                  <p className="text-gray-600 text-xs mt-1">Email changes require re-verification and are not supported yet.</p>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    type="submit"
                    disabled={profileSaving}
                    className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
                  >
                    {profileSaving ? 'Saving…' : 'Save name'}
                  </button>
                </div>
                <InlineStatus status={profileStatus} />
              </form>
            </Section>

            {/* Change Password */}
            <Section title="Change password" description="Must be at least 8 characters.">
              <form onSubmit={handlePasswordSave} className="space-y-4">
                <div>
                  <label className={labelClass()}>Current password</label>
                  <input
                    type="password"
                    value={passwords.current}
                    onChange={handlePasswordChange('current')}
                    required
                    autoComplete="current-password"
                    placeholder="••••••••"
                    className={inputClass()}
                  />
                </div>
                <div>
                  <label className={labelClass()}>New password</label>
                  <input
                    type="password"
                    value={passwords.next}
                    onChange={handlePasswordChange('next')}
                    required
                    minLength={8}
                    autoComplete="new-password"
                    placeholder="Min 8 characters"
                    className={inputClass()}
                  />
                </div>
                <div>
                  <label className={labelClass()}>Confirm new password</label>
                  <input
                    type="password"
                    value={passwords.confirm}
                    onChange={handlePasswordChange('confirm')}
                    required
                    autoComplete="new-password"
                    placeholder="Repeat new password"
                    className={inputClass()}
                  />
                </div>
                <button
                  type="submit"
                  disabled={passwordSaving}
                  className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
                >
                  {passwordSaving ? 'Updating…' : 'Update password'}
                </button>
                <InlineStatus status={passwordStatus} />
              </form>
            </Section>

            {/* Account */}
            <Section title="Account">
              <dl className="space-y-3">
                <div className="flex items-center justify-between py-2">
                  <dt className="text-sm text-gray-400">Member since</dt>
                  <dd className="text-sm text-white">{fmtDate(profile?.stats?.member_since)}</dd>
                </div>
              </dl>
            </Section>

            {/* My Usage */}
            <Section title="My usage" description="Your personal token and cost summary.">
              {usageLoading ? (
                <div className="h-16 animate-pulse bg-gray-800 rounded-lg" />
              ) : (
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { label: 'Queries', value: fmt(myUsage?.total_queries ?? 0) },
                    {
                      label: 'Tokens',
                      value: fmt((myUsage?.total_input_tokens ?? 0) + (myUsage?.total_output_tokens ?? 0)),
                      sub: `${fmt(myUsage?.total_input_tokens ?? 0)} in · ${fmt(myUsage?.total_output_tokens ?? 0)} out`,
                    },
                    { label: 'Cost', value: fmtCost(myUsage?.total_cost_usd ?? 0) },
                  ].map(({ label, value, sub }) => (
                    <div key={label} className="bg-gray-800 rounded-lg p-4">
                      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
                      <p className="text-xl font-bold text-white">{value}</p>
                      {sub && <p className="text-xs text-gray-600 mt-0.5">{sub}</p>}
                    </div>
                  ))}
                </div>
              )}
            </Section>

            {/* Recent Queries */}
            <Section title="Recent queries" description="Your last 10 queries across all collections.">
              {usageLoading ? (
                <div className="h-24 animate-pulse bg-gray-800 rounded-lg" />
              ) : recentQueries.length === 0 ? (
                <p className="text-gray-500 text-sm">No queries yet. Start a chat to see your activity here.</p>
              ) : (
                <div className="overflow-x-auto -mx-2">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-800 text-gray-500 text-xs uppercase tracking-wide">
                        <th className="text-left px-2 py-2 font-medium">Query</th>
                        <th className="text-right px-2 py-2 font-medium">Tokens</th>
                        <th className="text-right px-2 py-2 font-medium">Cost</th>
                        <th className="text-right px-2 py-2 font-medium">Latency</th>
                        <th className="text-right px-2 py-2 font-medium">Time</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                      {recentQueries.map((q) => (
                        <tr key={q.id} className="hover:bg-gray-800/50 transition-colors">
                          <td className="px-2 py-2.5 text-gray-300 max-w-[14rem] truncate" title={q.query}>{q.query}</td>
                          <td className="px-2 py-2.5 text-right text-gray-400 tabular-nums">
                            {q.input_tokens != null ? fmt((q.input_tokens ?? 0) + (q.output_tokens ?? 0)) : '—'}
                          </td>
                          <td className="px-2 py-2.5 text-right text-indigo-400 tabular-nums">{fmtCost(q.cost_usd)}</td>
                          <td className="px-2 py-2.5 text-right text-gray-400 tabular-nums">
                            {q.latency_ms != null ? `${fmt(q.latency_ms)}ms` : '—'}
                          </td>
                          <td className="px-2 py-2.5 text-right text-gray-500 text-xs whitespace-nowrap">{fmtDateTime(q.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Section>

          </div>
        )}
      </div>
    </PageWrapper>
  )
}
