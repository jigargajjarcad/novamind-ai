import { useState } from 'react'
import { Link } from 'react-router-dom'
import authService from '../services/authService'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState('idle') // idle | loading | sent | error
  const [errorMsg, setErrorMsg] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setStatus('loading')
    setErrorMsg(null)
    try {
      await authService.forgotPassword(email)
      setStatus('sent')
    } catch {
      setStatus('error')
      setErrorMsg('Something went wrong. Please try again.')
    }
  }

  if (status === 'sent') {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
        <div className="w-full max-w-md text-center">
          <div className="w-14 h-14 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-6">
            <svg className="w-7 h-7 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Check your email</h1>
          <p className="text-gray-400 text-sm mb-8">
            If <span className="text-gray-200">{email}</span> is registered, we&apos;ve sent a
            password reset link. Check your inbox and follow the instructions.
          </p>
          <p className="text-gray-500 text-sm">
            Didn&apos;t receive it?{' '}
            <button
              onClick={() => setStatus('idle')}
              className="text-indigo-400 hover:text-indigo-300"
            >
              Try again
            </button>
          </p>
          <p className="mt-4 text-gray-500 text-sm">
            <Link to="/login" className="text-indigo-400 hover:text-indigo-300">
              Back to sign in
            </Link>
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
        <h1 className="text-3xl font-bold text-white mb-1">Forgot password?</h1>
        <p className="text-gray-400 mb-8 text-sm">
          Enter your email and we&apos;ll send you a reset link.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {status === 'error' && (
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
              {errorMsg}
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

          <button
            type="submit"
            disabled={status === 'loading'}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            {status === 'loading' ? 'Sending…' : 'Send reset link'}
          </button>
        </form>
      </div>
    </div>
  )
}
