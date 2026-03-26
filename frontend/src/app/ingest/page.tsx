'use client'

import { useState, useCallback } from 'react'
import { api } from '@/lib/api'
import Link from 'next/link'

type IngestMethod = 'url' | 'text' | 'file'
type IngestResult = { success: boolean; document_id: string; chunks_count: number } | null

const SUPPORTED_FILE_TYPES = [
  { ext: '.pdf', label: 'PDF' },
  { ext: '.docx', label: 'Word' },
  { ext: '.txt', label: 'Text' },
  { ext: '.md', label: 'Markdown' },
  { ext: '.png', label: 'PNG' },
  { ext: '.jpg', label: 'JPG' },
  { ext: '.jpeg', label: 'JPEG' },
  { ext: '.webp', label: 'WebP' },
  { ext: '.gif', label: 'GIF' },
]

export default function IngestPage() {
  const [method, setMethod] = useState<IngestMethod>('file')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<IngestResult>(null)

  // URL state
  const [url, setUrl] = useState('')

  // Text state
  const [text, setText] = useState('')
  const [textTitle, setTextTitle] = useState('')

  // File state
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
      setResult(null)
    }
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
      setResult(null)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      let response

      if (method === 'url') {
        if (!url.trim()) {
          throw new Error('Please enter a URL')
        }
        response = await api.ingest({ url: url.trim() })
      } else if (method === 'text') {
        if (!text.trim()) {
          throw new Error('Please enter some text')
        }
        response = await api.ingest({
          text: text.trim(),
          metadata: textTitle.trim() ? { title: textTitle.trim() } : undefined
        })
      } else if (method === 'file') {
        if (!selectedFile) {
          throw new Error('Please select a file')
        }
        response = await api.uploadFile(selectedFile)
      } else {
        throw new Error('Invalid method')
      }

      setResult({
        success: true,
        document_id: response.document_id,
        chunks_count: response.chunks_count
      })

      // Reset form on success
      setUrl('')
      setText('')
      setTextTitle('')
      setSelectedFile(null)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to ingest content'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const getFileExtension = (filename: string) => {
    return filename.substring(filename.lastIndexOf('.')).toLowerCase()
  }

  const isValidFileType = (filename: string) => {
    const ext = getFileExtension(filename)
    return SUPPORTED_FILE_TYPES.some(t => t.ext === ext)
  }

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
            <Link href="/ingest" className="text-blue-600 dark:text-blue-400 font-medium">
              Ingest
            </Link>
            <Link href="/documents" className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100">
              Documents
            </Link>
            <Link href="/settings" className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100">
              Settings
            </Link>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-3xl">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-6">
          Add to Knowledge Base
        </h1>

        {/* Method Tabs */}
        <div className="flex border-b border-slate-200 dark:border-slate-700 mb-6">
          {[
            { key: 'file' as const, label: 'Upload File' },
            { key: 'url' as const, label: 'URL' },
            { key: 'text' as const, label: 'Paste Text' },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => {
                setMethod(tab.key)
                setError(null)
                setResult(null)
              }}
              className={`px-6 py-3 font-medium transition-colors ${
                method === tab.key
                  ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-800 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Success Message */}
        {result && (
          <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <p className="text-green-800 dark:text-green-400 font-medium">
              Successfully added to knowledge base!
            </p>
            <p className="text-green-700 dark:text-green-500 text-sm mt-1">
              Document ID: {result.document_id} ({result.chunks_count} chunks)
            </p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          {/* File Upload */}
          {method === 'file' && (
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Select a file to upload
              </label>
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  isDragging
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-slate-300 dark:border-slate-600 hover:border-blue-400 dark:hover:border-blue-500'
                }`}
              >
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.docx,.txt,.md,.png,.jpg,.jpeg,.webp,.gif"
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  {selectedFile ? (
                    <div>
                      <p className="text-lg font-medium text-slate-900 dark:text-slate-100">
                        {selectedFile.name}
                      </p>
                      <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                        {(selectedFile.size / 1024).toFixed(1)} KB
                      </p>
                      {!isValidFileType(selectedFile.name) && (
                        <p className="text-sm text-red-600 dark:text-red-400 mt-2">
                          Warning: This file type may not be supported
                        </p>
                      )}
                    </div>
                  ) : (
                    <div>
                      <p className="text-lg font-medium text-slate-900 dark:text-slate-100">
                        Drop a file here or click to browse
                      </p>
                      <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                        Supported: {SUPPORTED_FILE_TYPES.map(t => t.label).join(', ')}
                      </p>
                    </div>
                  )}
                </label>
              </div>
            </div>
          )}

          {/* URL Input */}
          {method === 'url' && (
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Enter a URL to ingest
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/article or https://youtube.com/watch?v=..."
                className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                Supports web pages and YouTube videos
              </p>
            </div>
          )}

          {/* Text Input */}
          {method === 'text' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Title (optional)
                </label>
                <input
                  type="text"
                  value={textTitle}
                  onChange={(e) => setTextTitle(e.target.value)}
                  placeholder="My notes..."
                  className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Content
                </label>
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Paste your text here..."
                  rows={10}
                  className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
                />
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="mt-6 flex justify-end">
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-slate-300 dark:disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <span className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                  Processing...
                </span>
              ) : (
                'Add to Knowledge Base'
              )}
            </button>
          </div>
        </form>

        {/* Help Section */}
        <div className="mt-8 p-6 bg-slate-100 dark:bg-slate-800/50 rounded-xl">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
            Tips
          </h2>
          <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
            <li>• <strong>Files:</strong> Upload PDFs, Word docs, text files, or images with text</li>
            <li>• <strong>URLs:</strong> Paste any web page or YouTube video link</li>
            <li>• <strong>Text:</strong> Paste notes, articles, or any text content</li>
            <li>• After ingesting, you can chat with your documents on the <Link href="/chat" className="text-blue-600 dark:text-blue-400 hover:underline">Chat page</Link></li>
          </ul>
        </div>
      </main>
    </div>
  )
}
