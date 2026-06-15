import { Link } from 'react-router-dom'

const features = [
  {
    title: 'Upload any PDF',
    description: 'Drag and drop your documents. We handle contracts, reports, manuals, and more.',
  },
  {
    title: 'Ask natural language questions',
    description: 'No query syntax or search terms. Just ask in plain English.',
  },
  {
    title: 'Get cited answers',
    description: 'Every answer links back to the exact page and paragraph in your document.',
  },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="px-6 py-4 flex items-center justify-between border-b border-gray-800 max-w-7xl mx-auto">
        <span className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          NovaMind AI
        </span>
        <div className="flex items-center gap-4">
          <Link to="/login" className="text-gray-300 hover:text-white text-sm transition-colors">
            Sign in
          </Link>
          <Link
            to="/register"
            className="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Get started
          </Link>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-6 py-28 text-center">
        <div className="inline-block bg-indigo-500/10 border border-indigo-500/20 rounded-full px-4 py-1 text-indigo-400 text-sm font-medium mb-8">
          RAG-powered document intelligence
        </div>
        <h1 className="text-6xl font-bold mb-6 bg-gradient-to-br from-white via-gray-200 to-gray-400 bg-clip-text text-transparent leading-tight">
          Talk to your documents
        </h1>
        <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto leading-relaxed">
          Upload any PDF and ask natural language questions. NovaMind retrieves the exact relevant
          content and returns accurate, cited answers — no hallucinations.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link
            to="/register"
            className="bg-indigo-600 hover:bg-indigo-500 px-8 py-4 rounded-xl text-lg font-medium transition-colors inline-block"
          >
            Start for free →
          </Link>
          <Link to="/login" className="text-gray-400 hover:text-white px-8 py-4 transition-colors">
            Sign in
          </Link>
        </div>
      </main>

      <section className="max-w-5xl mx-auto px-6 pb-28 grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((f) => (
          <div key={f.title} className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h3 className="font-semibold text-white mb-2">{f.title}</h3>
            <p className="text-gray-400 text-sm leading-relaxed">{f.description}</p>
          </div>
        ))}
      </section>
    </div>
  )
}
