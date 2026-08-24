'use client'

import { useState, useRef } from 'react'
import { Search, Loader2 } from 'lucide-react'

interface SatelliteSearchProps {
  onSearch: (query: string) => void
  loading?: boolean
  placeholder?: string
}

const QUICK_CHIPS = ['STARLINK', 'ISS', '25544', 'NOAA', 'COSMOS 2251']

export default function SatelliteSearch({
  onSearch,
  loading = false,
  placeholder = 'Search by satellite name or NORAD ID (e.g. STARLINK, 25544, ISS)...',
}: SatelliteSearchProps) {
  const [query, setQuery] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
    }
  }

  const handleChipClick = (chip: string) => {
    setQuery(chip)
    onSearch(chip)
  }

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-3">
      <div className="relative flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
        {/* Search Input Container */}
        <div className="relative flex-1">
          <div className="absolute left-3.5 top-1/2 -translate-y-1/2 text-text-tertiary pointer-events-none">
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin text-accent-primary" />
            ) : (
              <Search className="w-4 h-4" />
            )}
          </div>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            className="w-full pl-10 pr-4 py-3 bg-bg-surface border border-border-subtle hover:border-border-hover focus:border-accent-primary rounded-xl text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none transition-all duration-200"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="btn-primary text-xs py-3 px-6 rounded-xl font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition-all shrink-0"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Querying...</span>
            </span>
          ) : (
            'Check Compliance'
          )}
        </button>
      </div>

      {/* Quick Access Chips */}
      <div className="flex items-center gap-2 flex-wrap pt-1">
        <span className="text-[11px] font-mono text-text-tertiary tracking-wide uppercase">
          Quick Access:
        </span>
        {QUICK_CHIPS.map((chip) => (
          <button
            key={chip}
            type="button"
            onClick={() => handleChipClick(chip)}
            className="px-2.5 py-1 rounded-full text-xs font-mono bg-bg-elevated/80 border border-border-subtle hover:border-accent-primary text-text-secondary hover:text-text-primary transition-all duration-150"
          >
            {chip}
          </button>
        ))}
      </div>
    </form>
  )
}
