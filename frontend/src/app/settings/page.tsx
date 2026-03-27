'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100'

interface HealthStatus {
  status: string
  qdrant_connected: boolean
  collection_name: string
}

interface SettingsResponse {
  llm_provider: string
  llm_model: string
  embedding_provider: string
  embedding_model: string
}

interface SettingsState {
  llmProvider: string
  llmModel: string
  embeddingProvider: string
  embeddingModel: string
  availableLLMModels?: Record<string, string[]>
  availableEmbeddingModels?: Record<string, string[]>
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
      const data: SettingsResponse = await api.getSettings()
      setSettings({
        llmProvider: data.llm_provider,
        llmModel: data.llm_model,
        embeddingProvider: data.embedding_provider,
        embeddingModel: data.embedding_model,
      })
      // Load models for the selected providers
      loadLLMModels(data.llm_provider)
      loadEmbeddingModels(data.embedding_provider)
    } catch (err) {
      console.error('Failed to load settings:', err)
    }
  }

  const loadLLMModels = async (provider: string) => {
    // Fallback models when API is unavailable or returns Docker-serialized format
    const fallbackModels: Record<string, string[]> = {
      openai: ['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
      deepseek: ['deepseek-chat', 'deepseek-coder'],
      anthropic: ['claude-3-5-haiku-20241022', 'claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
      ollama: [],  // Will be populated from local Ollama if running
      zai: ['glm-4.5', 'glm-4.5-air', 'glm-4.6', 'glm-4.7', 'glm-5', 'glm-5-turbo'],
    }

    try {
      const response = await fetch(`${API_URL}/api/v1/settings/v1/llm-models`)
      if (response.ok) {
        const text = await response.text()
        let data

        try {
          data = JSON.parse(text)
          // Check if models contain actual data or Docker-serialized "[string] (N)" format
          const firstProvider = Object.keys(data.models || {})[0]
          if (firstProvider && typeof data.models[firstProvider]?.[0] === 'string' && data.models[firstProvider][0].includes('[string]')) {
            // Docker serialization detected, use fallback
            console.warn('Docker serialization detected, using fallback models')
            data = { models: fallbackModels }
          }
        } catch {
          // Parse Python repr format like: "['glm-5', 'glm-4']"
          const match = text.match(/\[([^\]]*)\]/)
          if (match && !match[1].includes('[string]')) {
            const models = match[1].split(',').map(m => m.trim().replace(/^'|"|'$|"$/g, ''))
            data = { models: { [provider]: models } }
          } else {
            console.warn('Could not parse models, using fallback')
            data = { models: fallbackModels }
          }
        }
        setSettings(prev => ({
          ...prev,
          availableLLMModels: data.models,
          llmModel: data.models?.[provider]?.[0] || prev.llmModel
        }))
      }
    } catch (err) {
      console.error('Failed to load LLM models:', err)
      // Use fallback on error
      setSettings(prev => ({
        ...prev,
        availableLLMModels: fallbackModels,
        llmModel: fallbackModels[provider]?.[0] || prev.llmModel
      }))
    }
  }

  const loadEmbeddingModels = async (provider: string) => {
    // Fallback embedding models when API is unavailable
    const fallbackModels: Record<string, string[]> = {
      openai: ['text-embedding-3-small', 'text-embedding-3-large', 'text-embedding-ada-002'],
      gemini: ['gemini-embedding-2-preview', 'gemini-embedding-001'],
      ollama: ['nomic-embed-text', 'mxbai-embed-large', 'bge-m3'],
    }

    try {
      const response = await fetch(`${API_URL}/api/v1/settings/v1/embedding-models`)
      if (response.ok) {
        const text = await response.text()
        let data

        try {
          data = JSON.parse(text)
          // Check if models contain actual data or Docker-serialized "[string] (N)" format
          const firstProvider = Object.keys(data.models || {})[0]
          if (firstProvider && typeof data.models[firstProvider]?.[0] === 'string' && data.models[firstProvider][0].includes('[string]')) {
            console.warn('Docker serialization detected in embedding models, using fallback')
            data = { models: fallbackModels }
          }
        } catch {
          const match = text.match(/\[([^\]]*)\]/)
          if (match && !match[1].includes('[string]')) {
            const models = match[1].split(',').map(m => m.trim().replace(/^'|"|'$|"$/g, ''))
            data = { models: { [provider]: models } }
          } else {
            console.warn('Could not parse embedding models, using fallback')
            data = { models: fallbackModels }
          }
        }
        setSettings(prev => ({
          ...prev,
          availableEmbeddingModels: data.models,
          embeddingModel: data.models?.[provider]?.[0] || prev.embeddingModel
        }))
      }
    } catch (err) {
      console.error('Failed to load embedding models:', err)
      setSettings(prev => ({
        ...prev,
        availableEmbeddingModels: fallbackModels,
        embeddingModel: fallbackModels[provider]?.[0] || prev.embeddingModel
      }))
    }
  }

  const handleLLMProviderChange = (value: string) => {
    setSettings(prev => ({ ...prev, llmProvider: value, llmModel: '' }))
    loadLLMModels(value)
  }

  const handleEmbeddingProviderChange = (value: string) => {
    setSettings(prev => ({ ...prev, embeddingProvider: value, embeddingModel: '' }))
    loadEmbeddingModels(value)
  }

  const handleSettingChange = (key: keyof SettingsState, value: string) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  const saveSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      })
      if (response.ok) {
        alert('Settings saved successfully!')
        loadSettings()
      } else {
        alert('Failed to save settings')
      }
    } catch (err) {
      console.error('Failed to save settings:', err)
      alert('Failed to save settings')
    }
  }

  useEffect(() => {
    loadHealth()
    loadSettings()
  }, [])

  useEffect(() => {
    if (settings.llmProvider) {
      loadLLMModels(settings.llmProvider)
    }
    if (settings.embeddingProvider) {
      loadEmbeddingModels(settings.embeddingProvider)
    }
  }, [settings.llmProvider, settings.embeddingProvider])

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
                onChange={(e) => handleLLMProviderChange(e.target.value)}
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
                {settings.availableLLMModels?.[settings.llmProvider]?.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                )) || <option value="">Loading models...</option>}
              </select>
            </div>

            {/* Embedding Configuration */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Embedding Provider
              </label>
              <select
                value={settings.embeddingProvider}
                onChange={(e) => handleEmbeddingProviderChange(e.target.value)}
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
                {settings.availableEmbeddingModels?.[settings.embeddingProvider]?.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                )) || <option value="">Loading models...</option>}
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
