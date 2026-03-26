'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import Link from 'next/link'

interface HealthStatus {
  status: string
  qdrant_connected: boolean
  collection_name: string
}

interface SettingsState {
  llmProvider: string
  llmModel: string
  embeddingProvider: string
  embeddingModel: string
}

const LLM_MODELS: Record<string, string[]> = {
  openai: ['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
  deepseek: ['deepseek-chat'],
  anthropic: ['claude-3-haiku-20240307', 'claude-3-sonnet-20240229', 'claude-3-opus-20240229'],
  ollama: ['llama3', 'mistral', 'gemma2'],
  zai: ['glm-5', 'glm-4', 'glm-4-plus', 'glm-4-air'],
}

const EMBEDDING_MODELS: Record<string, string[]> = {
  openai: ['text-embedding-3-small', 'text-embedding-3-large', 'text-embedding-ada-002'],
  gemini: ['gemini-embedding-2-preview', 'gemini-embedding-001'],
}

export default function SettingsPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [settings, setSettings] = useState<SettingsState>({
    llmProvider: 'zai',
    llmModel: 'glm-5',
    embeddingProvider: 'gemini',
    embeddingModel: 'gemini-embedding-2-preview',
  })

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

  const loadSettings = async () => {
    try {
      const response = await fetch('/api/settings')
      if (response.ok) {
        const data = await response.json()
        setSettings(data)
      }
    } catch (err) {
      console.error('Failed to load settings:', err)
    }
  }

  const handleSettingChange = (key: keyof SettingsState, value: string) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  const saveSettings = async () => {
    try {
      await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      })
      alert('Settings saved successfully!')
      loadSettings()
    } catch (err) {
      console.error('Failed to save settings:', err)
      alert('Failed to save settings')
    }
  }

  useEffect(() => {
    loadHealth()
    loadSettings()
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
            <Link href="/ingest" className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100">
              Ingest
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
            Model Selection
          </h2>
          <p className="text-slate-600 dark:text-slate-400 mb-6">
            Select your preferred LLM and embedding models for RAG.
          </p>

          <div className="space-y-6">
            {/* LLM Configuration */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                LLM Provider
              </label>
              <select
                value={settings.llmProvider}
                onChange={(e) => handleSettingChange('llmProvider', e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="openai">OpenAI</option>
                <option value="deepseek">DeepSeek</option>
                <option value="anthropic">Anthropic (Claude)</option>
                <option value="ollama">Ollama (Local)</option>
                <option value="zai">Z.ai (GLM)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                LLM Model
              </label>
              <select
                value={settings.llmModel}
                onChange={(e) => handleSettingChange('llmModel', e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {LLM_MODELS[settings.llmProvider]?.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </div>

            {/* Embedding Configuration */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Embedding Provider
              </label>
              <select
                value={settings.embeddingProvider}
                onChange={(e) => handleSettingChange('embeddingProvider', e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="openai">OpenAI</option>
                <option value="gemini">Google Gemini</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Embedding Model
              </label>
              <select
                value={settings.embeddingModel}
                onChange={(e) => handleSettingChange('embeddingModel', e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {EMBEDDING_MODELS[settings.embeddingProvider]?.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Save Button */}
          <div className="mt-6">
            <button
              onClick={saveSettings}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Save Settings
            </button>
            <p className="text-xs text-slate-500 dark:text-slate-500 mt-2 text-center">
              Note: Changes require backend restart to take effect
            </p>
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
