'use client'

import { useState, useRef, useEffect } from 'react'

interface SatelliteSearchProps {
  onSearch: (query: string) => void
  loading?: boolean
  placeholder?: string
}

export default function SatelliteSearch({ onSearch, loading = false, placeholder }: SatelliteSearchProps) {
  const [query, setQuery] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div
        style={{
          display: 'flex',
          gap: 10,
          alignItems: 'center',
        }}
      >
        <div
          style={{
            flex: 1,
            position: 'relative',
          }}
        >
          <span
            style={{
              position: 'absolute',
              left: 14,
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-tertiary)',
              fontSize: 16,
              pointerEvents: 'none',
            }}
          >
            ⌕
          </span>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder || 'Search by satellite name or NORAD ID (e.g. STARLINK, 25544)'}
            style={{
              width: '100%',
              padding: '12px 14px 12px 40px',
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              fontSize: 14,
              color: 'var(--text-primary)',
              outline: 'none',
              transition: 'border-color 150ms',
              fontFamily: 'IBM Plex Sans, sans-serif',
            }}
            onFocus={(e) => {
              e.target.style.borderColor = 'var(--accent-blue)'
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--border)'
            }}
          />
        </div>

        <button
          type="submit"
          disabled={loading || !query.trim()}
          style={{
            padding: '12px 20px',
            backgroundColor: loading ? 'var(--bg-tertiary)' : 'var(--accent-blue)',
            color: loading ? 'var(--text-tertiary)' : '#fff',
            border: 'none',
            borderRadius: 8,
            fontSize: 14,
            fontWeight: 600,
            cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
            transition: 'all 150ms',
            whiteSpace: 'nowrap',
          }}
        >
          {loading ? 'Searching…' : 'Check Compliance'}
        </button>
      </div>

      <div style={{ marginTop: 10, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <span style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>Try:</span>
        {['STARLINK', 'ISS', '25544', 'NOAA', 'COSMOS 2251'].map((q) => (
          <button
            key={q}
            type="button"
            onClick={() => {
              setQuery(q)
              onSearch(q)
            }}
            style={{
              padding: '2px 8px',
              backgroundColor: 'var(--bg-tertiary)',
              border: '1px solid var(--border)',
              borderRadius: 4,
              fontSize: 11,
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              fontFamily: 'monospace',
              transition: 'border-color 150ms',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent-blue)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border)'
            }}
          >
            {q}
          </button>
        ))}
      </div>
    </form>
  )
}
