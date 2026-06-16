import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import authService from '../services/authService'

export default function VerifyEmail() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { verifyEmail } = useAuth()

  const [status, setStatus] = useState('verifying') // verifying | success | error
  const [errorCode, setErrorCode] = useState(null)
  const [resendEmail, setResendEmail] = useState('')
  const [resendStatus, setResendStatus] = useState(null) // null | sending | sent | error
  const didRun = useRef(false)

  useEffect(() => {
    if (didRun.current) return
    didRun.current = true

    const token = searchParams.get('token')
    if (!token) {
      setStatus('error')
      setErrorCode('TOKEN_INVALID')
      return
    }

    verifyEmail(token)
      .then(() => {
        setStatus('success')
        setTimeout(() => navigate('/dashboard'), 3000)
      })
      .catch((err) => {
        const code = err.response?.data?.error?.code ?? 'TOKEN_INVALID'
        setErrorCode(code)
        setStatus('error')
      })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  async function handleResend(e) {
    e.preventDefault()
    if (!resendEmail) return
    setResendStatus('sending')
    try {
      await authService.resendVerification(resendEmail)
      setResendStatus('sent')
    } catch (err) {
      const code = err.response?.data?.error?.code
      setResendStatus(code === 'RATE_LIMITED' ? 'rate_limited' : 'error')
    }
  }

  if (status === 'verifying') {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
        <div className="text-center">
          <div className="h-10 w-10 rounded-full border-2 border-gray-700 border-t-indigo-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400 text-sm">Verifying your email…</p>
        </div>
      </div>
    )
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
          <h1 className="text-2xl font-bold text-white mb-2">Email verified</h1>
          <p className="text-gray-400 text-sm mb-6">
            Your account is active. Redirecting to your dashboard…
          </p>
          <Link to="/dashboard" className="text-indigo-400 hover:text-indigo-300 text-sm">
            Go to dashboard now →
          </Link>
        </div>
      </div>
    )
  }

  // Error state
  const isExpired = errorCode === 'TOKEN_EXPIRED'

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
            ? 'This verification link has expired. Request a new one below.'
            : 'This verification link is invalid or has already been used.'}
        </p>

        {resendStatus === 'sent' ? (
          <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4 text-green-400 text-sm">
            Verification email sent. Check your inbox.
          </div>
        ) : (
          <form onSubmit={handleResend} className="space-y-3">
            <p className="text-sm font-medium text-gray-300">Request a new verification email</p>
            <input
              type="email"
              value={resendEmail}
              onChange={(e) => setResendEmail(e.target.value)}
              required
              placeholder="your@email.com"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
            />
            {resendStatus === 'rate_limited' && (
              <p className="text-yellow-400 text-xs">Please wait a moment before requesting another email.</p>
            )}
            {resendStatus === 'error' && (
              <p className="text-red-400 text-xs">Something went wrong. Try again.</p>
            )}
            <button
              type="submit"
              disabled={resendStatus === 'sending'}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-lg transition-colors"
            >
              {resendStatus === 'sending' ? 'Sending…' : 'Resend verification email'}
            </button>
          </form>
        )}

        <p className="mt-6 text-center text-gray-500 text-sm">
          Already verified?{' '}
          <Link to="/login" className="text-indigo-400 hover:text-indigo-300">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
