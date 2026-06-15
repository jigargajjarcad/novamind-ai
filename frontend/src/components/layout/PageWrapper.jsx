import Navbar from './Navbar'

export default function PageWrapper({ children, title }) {
  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-8">
        {title && <title>{title} — NovaMind AI</title>}
        {children}
      </main>
    </div>
  )
}
