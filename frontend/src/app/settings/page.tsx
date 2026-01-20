'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import Link from 'next/link'

interface HealthStatus {
  status: string
  qdrant_connected: boolean
  collection_name: string
}

export default function SettingsPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const loadHealth = async () => {
    try {
      const status = await api.health()
      setHealth(status)
    } catch (err) {
      console.error('Failed to load health status:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadHealth()
  }, [])

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            PKS
          </Link>
          <nav className="flex gap-4">
            <Link href="/chat" className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100">
              Chat
            </Link>
            <Link href="/documents" className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100">
              Documents
            </Link>
            <Link href="/settings" className="text-blue-600 dark:text-blue-400 font-medium">
              Settings
            </Link>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          Settings
        </h1>

        {/* System Status */}
        <div className="mb-8 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
            System Status
          </h2>
          {isLoading ? (
            <p className="text-slate-600 dark:text-slate-400">Loading...</p>
          ) : health ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">API Status</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  health.status === 'healthy'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                    : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                }`}>
                  {health.status}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">Qdrant Connection</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  health.qdrant_connected
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                    : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                }`}>
                  {health.qdrant_connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">Collection</span>
                <span className="text-slate-900 dark:text-slate-100 font-mono text-sm">
                  {health.collection_name}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-600 dark:text-slate-400">Backend API</span>
                <span className="text-slate-900 dark:text-slate-100 font-mono text-sm">
                  {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100'}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-red-600 dark:text-red-400">Failed to load system status</p>
          )}
        </div>

        {/* Configuration */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
            Configuration
          </h2>
          <p className="text-slate-600 dark:text-slate-400 mb-4">
            API keys and provider settings are configured via environment variables on the backend server.
          </p>

          <div className="space-y-4">
            <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg">
              <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2">LLM Provider</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Configure via <code className="px-2 py-1 bg-slate-200 dark:bg-slate-800 rounded">DEFAULT_LLM_PROVIDER</code> environment variable
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">
                Options: openai, deepseek, anthropic, ollama, zai
              </p>
            </div>

            <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg">
              <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2">Embedding Provider</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Configure via <code className="px-2 py-1 bg-slate-200 dark:bg-slate-800 rounded">DEFAULT_EMBEDDING_PROVIDER</code> environment variable
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">
                Options: openai, gemini
              </p>
            </div>

            <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg">
              <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2">API Keys</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Configure provider API keys via environment variables on the backend server:
              </p>
              <ul className="text-xs text-slate-500 dark:text-slate-500 mt-2 space-y-1 ml-4">
                <li><code>OPENAI_API_KEY</code></li>
                <li><code>DEEPSEEK_API_KEY</code></li>
                <li><code>ANTHROPIC_API_KEY</code></li>
                <li><code>ZAI_API_KEY</code></li>
                <li><code>GEMINI_API_KEY</code></li>
              </ul>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 flex gap-4">
          <button
            onClick={loadHealth}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Refresh Status
          </button>
          <Link
            href="/"
            className="px-6 py-3 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors font-medium text-center"
          >
            Back to Home
          </Link>
        </div>
      </main>
    </div>
  )
}
