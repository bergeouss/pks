import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-slate-900 dark:text-slate-100 mb-4">
            PKS
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400">
            Personal Knowledge Synthesizer
          </p>
          <p className="text-sm text-slate-500 dark:text-slate-500 mt-2">
            Self-hosted knowledge management with AI-powered search
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <Link
            href="/chat"
            className="group p-8 bg-white dark:bg-slate-800 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 border border-slate-200 dark:border-slate-700"
          >
            <div className="text-4xl mb-4">💬</div>
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100 mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400">
              Chat
            </h2>
            <p className="text-slate-600 dark:text-slate-400">
              Ask questions and get AI-powered answers from your knowledge base
            </p>
          </Link>

          <Link
            href="/documents"
            className="group p-8 bg-white dark:bg-slate-800 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 border border-slate-200 dark:border-slate-700"
          >
            <div className="text-4xl mb-4">📄</div>
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100 mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400">
              Documents
            </h2>
            <p className="text-slate-600 dark:text-slate-400">
              Browse and manage your ingested documents and sources
            </p>
          </Link>

          <Link
            href="/settings"
            className="group p-8 bg-white dark:bg-slate-800 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 border border-slate-200 dark:border-slate-700"
          >
            <div className="text-4xl mb-4">⚙️</div>
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100 mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400">
              Settings
            </h2>
            <p className="text-slate-600 dark:text-slate-400">
              Configure API keys and system preferences
            </p>
          </Link>
        </div>

        <div className="mt-16 text-center text-sm text-slate-500 dark:text-slate-500">
          <p>Backend API: <span className="font-mono">{process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100'}</span></p>
        </div>
      </div>
    </div>
  )
}
