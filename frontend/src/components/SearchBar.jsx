import { useState, useEffect, useRef } from 'react'
import './SearchBar.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function SearchBar({ onSearch, loading }) {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [selectedGame, setSelectedGame] = useState(null)

  const debounceRef = useRef(null)
  const wrapperRef = useRef(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Debounced autocomplete search
  useEffect(() => {
    if (query.length < 2 || selectedGame) {
      setSuggestions([])
      return
    }

    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    debounceRef.current = setTimeout(async () => {
      try {
        const resp = await fetch(
          `${API_BASE}/search?q=${encodeURIComponent(query)}`
        )
        if (resp.ok) {
          const data = await resp.json()
          setSuggestions(data)
          setShowDropdown(data.length > 0)
        }
      } catch {
        setSuggestions([])
      }
    }, 300)

    return () => clearTimeout(debounceRef.current)
  }, [query, selectedGame])

  const handleSelect = (game) => {
    setSelectedGame(game)
    setQuery(game.name)
    setShowDropdown(false)
    setSuggestions([])
  }

  const handleInputChange = (e) => {
    const value = e.target.value
    setQuery(value)
    if (selectedGame) {
      setSelectedGame(null)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setShowDropdown(false)
    if (selectedGame) {
      onSearch(selectedGame.appid, selectedGame.name)
    }
  }

  return (
    <div className="search-bar" ref={wrapperRef}>
      <form className="search-bar__form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="search-bar__input"
          placeholder="Search for a Steam game..."
          value={query}
          onChange={handleInputChange}
          disabled={loading}
        />
        <button
          type="submit"
          className="search-bar__button"
          disabled={loading || !selectedGame}
        >
          {loading ? 'Analyzing...' : 'Summarize'}
        </button>
      </form>

      {showDropdown && suggestions.length > 0 && (
        <ul className="search-bar__dropdown">
          {suggestions.map((game) => (
            <li key={game.appid}>
              <button
                type="button"
                className="search-bar__option"
                onClick={() => handleSelect(game)}
              >
                {game.name}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default SearchBar
