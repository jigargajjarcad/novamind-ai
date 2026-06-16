import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import authService from '../services/authService'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [unverified, setUnverified] = useState(false)
  const [resendStatus, setResendStatus] = useState(null) // null | sending | sent | error
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setUnverified(false)
    setResendStatus(null)
    setLoading(true)
    try {
      await login({ email, password })
      navigate('/dashboard')
    } catch (err) {
      const code = err.response?.data?.error?.code
      if (code === 'EMAIL_NOT_VERIFIED') {
        setUnverified(true)
      } else {
        setError(err.response?.data?.error?.message || 'Login failed. Check your credentials.')
      }
    } finally {
      setLoading(false)
    }
  }

  async function handleResend() {
    setResendStatus('sending')
    try {
      await authService.resendVerification(email)
      setResendStatus('sent')
    } catch (err) {
      const code = err.response?.data?.error?.code
      setResendStatus(code === 'RATE_LIMITED' ? 'rate_limited' : 'error')
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <Link
          to="/"
          className="text-indigo-400 text-sm hover:text-indigo-300 mb-8 inline-block"
        >
          ← NovaMind AI
        </Link>
        <h1 className="text-3xl font-bold text-white mb-1">Sign in</h1>
        <p className="text-gray-400 mb-8 text-sm">Welcome back</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
              {error}
            </div>
          )}

          {unverified && (
            <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4 text-sm">
              <p className="text-yellow-300 font-medium mb-1">Email not verified</p>
              <p className="text-yellow-400/80 mb-3">
                Please verify your email address before signing in. Check your inbox for the verification link.
              </p>
              {resendStatus === 'sent' ? (
                <p className="text-green-400 text-xs">Verification email sent. Check your inbox.</p>
              ) : resendStatus === 'rate_limited' ? (
                <p className="text-yellow-400 text-xs">Please wait a moment before requesting another email.</p>
              ) : (
                <button
                  type="button"
                  onClick={handleResend}
                  disabled={resendStatus === 'sending'}
                  className="text-indigo-400 hover:text-indigo-300 text-xs underline disabled:opacity-50"
                >
                  {resendStatus === 'sending' ? 'Sending…' : 'Resend verification email'}
                </button>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="mt-6 text-center text-gray-400 text-sm">
          Don&apos;t have an account?{' '}
          <Link to="/register" className="text-indigo-400 hover:text-indigo-300 font-medium">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}
