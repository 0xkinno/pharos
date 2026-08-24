'use client'

import { useState, useEffect, useCallback } from 'react'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import SatelliteSearch from '@/components/dashboard/SatelliteSearch'
import SatelliteCard from '@/components/satellite/SatelliteCard'
import { SkeletonCard, ComplianceGauge } from '@/components/ui'
import { api } from '@/lib/api'
import type { DemoDataset, DemoSatelliteSummary, SatelliteSearchResult } from '@/lib/types'
import Link from 'next/link'

export default function DashboardPage() {
  const [demo, setDemo] = useState<DemoDataset | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchResults, setSearchResults] = useState<SatelliteSearchResult[] | null>(null)
  const [searching, setSearching] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('ALL')

  // Load demo dataset on mount
  useEffect(() => {
    api.getDemo()
      .then(setDemo)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const handleSearch = useCallback(async (query: string) => {
    setSearching(true)
    setSearchError(null)
    try {
      const results = await api.searchSatellites(query)
      setSearchResults(results)
    } catch (e: unknown) {
      setSearchError(e instanceof Error ? e.message : 'Search failed')
      setSearchResults([])
    } finally {
      setSearching(false)
    }
  }, [])

  const displaySatellites: DemoSatelliteSummary[] = demo?.satellites.filter((s) => {
    if (statusFilter === 'ALL') return true
    return s.compliance_level === statusFilter
  }) ?? []

  return (
    <div style={{ backgroundColor: 'var(--bg-primary)', minHeight: '100vh' }}>
      <Navbar />

      <main style={{ maxWidth: 1280, margin: '0 auto', padding: '40px 24px' }}>
        {/* Page header */}
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 6 }}>
            Compliance Dashboard
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
            Check any satellite against 20+ coded rules from 5 regulatory bodies.
            Real-time data from CelesTrak · Rule engine is API-deletion-proof.
          </p>
        </div>

        {/* Search */}
        <div className="pharos-card" style={{ padding: '20px 24px', marginBottom: 32 }}>
          <SatelliteSearch onSearch={handleSearch} loading={searching} />

          {searchError && (
            <div
              style={{
                marginTop: 14,
                padding: '10px 14px',
                backgroundColor: 'var(--status-fail-bg)',
                border: '1px solid rgba(239, 68, 68, 0.2)',
                borderRadius: 6,
                color: 'var(--status-fail)',
                fontSize: 13,
              }}
            >
              {searchError}
            </div>
          )}

          {/* Search results */}
          {searchResults && searchResults.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <div style={{ fontSize: 11, color: 'var(--text-tertiary)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                {searchResults.length} result{searchResults.length !== 1 ? 's' : ''}
              </div>
              {searchResults.map((sat) => (
                <Link
                  key={sat.norad_cat_id}
                  href={`/satellite/${sat.norad_cat_id}`}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 14px',
                    borderRadius: 6,
                    textDecoration: 'none',
                    transition: 'background 150ms',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--bg-hover)' }}
                  onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent' }}
                >
                  <div>
                    <span style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 500 }}>
                      {sat.object_name}
                    </span>
                    <span style={{ fontSize: 11, color: 'var(--text-tertiary)', marginLeft: 10, fontFamily: 'monospace' }}>
                      NORAD {sat.norad_cat_id}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    {sat.mean_altitude_km && (
                      <span style={{ fontSize: 12, color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
                        {Math.round(sat.mean_altitude_km)} km
                      </span>
                    )}
                    <span style={{ fontSize: 12, color: 'var(--accent-blue)' }}>Check →</span>
                  </div>
                </Link>
              ))}
            </div>
          )}

          {searchResults && searchResults.length === 0 && !searching && (
            <div style={{ marginTop: 12, fontSize: 13, color: 'var(--text-tertiary)' }}>
              No satellites found. Try a different search term or check the NORAD catalog number.
            </div>
          )}
        </div>

        {/* Demo summary stats */}
        {demo && (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
              gap: 12,
              marginBottom: 32,
            }}
          >
            {[
              { label: 'Total Satellites', value: demo.summary.total_satellites, color: 'var(--text-primary)' },
              { label: 'Compliant', value: demo.summary.compliant, color: 'var(--status-pass)' },
              { label: 'At Risk', value: demo.summary.at_risk, color: 'var(--status-flag)' },
              { label: 'Non-Compliant', value: demo.summary.non_compliant, color: 'var(--status-fail)' },
              { label: 'Avg Score', value: `${demo.summary.average_score}`, color: 'var(--accent-blue)' },
            ].map(({ label, value, color }) => (
              <div key={label} className="pharos-card" style={{ padding: '16px 18px' }}>
                <div style={{ fontSize: 24, fontWeight: 700, color, fontFamily: 'monospace' }}>
                  {value}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-tertiary)', marginTop: 3, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  {label}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Status filter */}
        <div style={{ display: 'flex', gap: 6, marginBottom: 20, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 12, color: 'var(--text-tertiary)', alignSelf: 'center', marginRight: 6 }}>
            Filter:
          </span>
          {['ALL', 'COMPLIANT', 'AT_RISK', 'NON_COMPLIANT'].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              style={{
                padding: '5px 12px',
                borderRadius: 6,
                fontSize: 11,
                fontWeight: 600,
                cursor: 'pointer',
                border: '1px solid',
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
                transition: 'all 150ms',
                borderColor: statusFilter === s ? 'var(--accent-blue)' : 'var(--border)',
                backgroundColor: statusFilter === s ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                color: statusFilter === s ? 'var(--accent-blue)' : 'var(--text-secondary)',
              }}
            >
              {s.replace('_', ' ')}
            </button>
          ))}
        </div>

        {/* Satellite grid */}
        {loading && (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
              gap: 16,
            }}
          >
            {Array.from({ length: 5 }).map((_, i) => (
              <SkeletonCard key={i} height={200} />
            ))}
          </div>
        )}

        {error && (
          <div
            style={{
              padding: '24px',
              backgroundColor: 'var(--status-fail-bg)',
              border: '1px solid rgba(239, 68, 68, 0.2)',
              borderRadius: 8,
              color: 'var(--status-fail)',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 6 }}>
              Failed to load demo data
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{error}</div>
          </div>
        )}

        {!loading && !error && (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
              gap: 16,
            }}
          >
            {displaySatellites.map((sat) => (
              <SatelliteCard key={sat.norad_cat_id} satellite={sat} />
            ))}
          </div>
        )}

        {!loading && !error && displaySatellites.length === 0 && (
          <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-tertiary)' }}>
            No satellites match the current filter.
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}
