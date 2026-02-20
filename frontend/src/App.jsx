import { useState } from 'react'
import SearchBar from './components/SearchBar'
import LoadingSpinner from './components/LoadingSpinner'
import ResultDisplay from './components/ResultDisplay'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSearch = async (appId) => {
    setLoading(true)
    setResult(null)
    setError(null)

    try {
      const response = await fetch(
        `${API_BASE}/summarize?app_id=${encodeURIComponent(appId)}`
      )

      if (!response.ok) {
        throw new Error(
          response.status === 404
            ? 'Game not found. Check the name and try again.'
            : 'Something went wrong. Please try again.'
        )
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app">
      <h1 className="app__title">Steam Review Summarizer</h1>
      <p className="app__subtitle">
        AI-powered analysis of what players are saying
      </p>

      <SearchBar onSearch={handleSearch} loading={loading} />

      {loading && <LoadingSpinner />}

      {error && <p className="app__error">{error}</p>}

      {result && (
        <ResultDisplay
          game={result.game}
          appId={result.app_id}
          summary={result.summary}
        />
      )}

      {!loading && !error && !result && (
        <p className="app__placeholder">
          Search for a Steam game to see what reviewers think
        </p>
      )}
    </main>
  )
}

export default App
