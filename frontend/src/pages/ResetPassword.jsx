import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import authService from '../services/authService'

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [status, setStatus] = useState('idle') // idle | loading | success | token_invalid | token_expired | error
  const [errorMsg, setErrorMsg] = useState(null)
  const didMount = useRef(false)

  useEffect(() => {
    if (didMount.current) return
    didMount.current = true
    if (!token) setStatus('token_invalid')
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  async function handleSubmit(e) {
    e.preventDefault()
    if (newPassword !== confirmPassword) {
      setErrorMsg('Passwords do not match.')
      return
    }
    setErrorMsg(null)
    setStatus('loading')
    try {
      await authService.resetPassword(token, newPassword)
      setStatus('success')
      setTimeout(() => navigate('/login'), 3000)
    } catch (err) {
      const code = err.response?.data?.error?.code
      if (code === 'TOKEN_EXPIRED') {
        setStatus('token_expired')
      } else if (code === 'TOKEN_INVALID') {
        setStatus('token_invalid')
      } else {
        setStatus('error')
        setErrorMsg(err.response?.data?.error?.message || 'Something went wrong. Please try again.')
      }
    }
  }

  if (status === 'success') {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
        <div className="w-full max-w-md text-center">
          <div className="w-14 h-14 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-6">
            <svg className="w-7 h-7 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Password reset</h1>
          <p className="text-gray-400 text-sm mb-6">
            Your password has been updated. Redirecting to sign in…
          </p>
          <Link to="/login" className="text-indigo-400 hover:text-indigo-300 text-sm">
            Sign in now →
          </Link>
        </div>
      </div>
    )
  }

  if (status === 'token_invalid' || status === 'token_expired') {
    const isExpired = status === 'token_expired'
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <Link to="/" className="text-indigo-400 text-sm hover:text-indigo-300 mb-8 inline-block">
            ← NovaMind AI
          </Link>
          <div className="w-14 h-14 rounded-full bg-red-500/20 flex items-center justify-center mb-6">
            <svg className="w-7 h-7 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">
            {isExpired ? 'Link expired' : 'Invalid link'}
          </h1>
          <p className="text-gray-400 text-sm mb-8">
            {isExpired
              ? 'This password reset link has expired. Request a new one.'
              : 'This password reset link is invalid or has already been used.'}
          </p>
          <Link
            to="/forgot-password"
            className="inline-block w-full text-center bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            Request a new reset link
          </Link>
          <p className="mt-6 text-center text-gray-500 text-sm">
            <Link to="/login" className="text-indigo-400 hover:text-indigo-300">Back to sign in</Link>
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <Link
          to="/login"
          className="text-indigo-400 text-sm hover:text-indigo-300 mb-8 inline-block"
        >
          ← Back to sign in
        </Link>
        <h1 className="text-3xl font-bold text-white mb-1">Reset password</h1>
        <p className="text-gray-400 mb-8 text-sm">Choose a new password for your account.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {(status === 'error' || errorMsg) && (
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
              {errorMsg}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">New password</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              minLength={8}
              autoComplete="new-password"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
              placeholder="Minimum 8 characters"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Confirm password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              autoComplete="new-password"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={status === 'loading'}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            {status === 'loading' ? 'Resetting…' : 'Reset password'}
          </button>
        </form>
      </div>
    </div>
  )
}
