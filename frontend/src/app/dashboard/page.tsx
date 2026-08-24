'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import SatelliteSearch from '@/components/dashboard/SatelliteSearch'
import SatelliteCard from '@/components/satellite/SatelliteCard'
import { SkeletonCard, NumberCounter } from '@/components/ui'
import { api } from '@/lib/api'
import type { DemoDataset, DemoSatelliteSummary, SatelliteSearchResult } from '@/lib/types'
import Link from 'next/link'
import { Radio, ShieldAlert, ArrowRight, Layers, AlertCircle } from 'lucide-react'

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
    <div className="bg-bg-base text-text-primary min-h-screen">
      <Navbar />

      <main className="max-w-container mx-auto px-4 sm:px-6 pt-28 pb-16">
        {/* Page Header */}
        <div className="mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-primary/10 border border-accent-primary/20 text-accent-primary text-xs font-mono uppercase tracking-wider mb-2.5">
            <Radio className="w-3 h-3 animate-pulse" />
            <span>Live LEO Monitor · CelesTrak GP API</span>
          </div>
          <h1 className="font-display text-2xl sm:text-4xl font-bold tracking-tight text-text-primary mb-2">
            Compliance Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-text-secondary max-w-2xl leading-relaxed">
            Instant orbital telemetry verification against 20+ statutory rules across 5 space agencies.
            Deterministic rule engine with mathematical orbital lifetime modeling.
          </p>
        </div>

        {/* Search Panel */}
        <div className="pharos-card p-5 sm:p-6 mb-8 border border-border-subtle bg-bg-surface/80 backdrop-blur-md">
          <SatelliteSearch onSearch={handleSearch} loading={searching} />

          {searchError && (
            <div className="mt-4 p-3.5 bg-status-fail-bg border border-status-fail/20 rounded-xl text-status-fail text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{searchError}</span>
            </div>
          )}

          {/* Search Results Dropdown/Grid */}
          {searchResults && searchResults.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-5 pt-4 border-t border-border-subtle"
            >
              <div className="text-[11px] font-mono text-text-tertiary uppercase tracking-wider mb-3">
                Found {searchResults.length} Satellite{searchResults.length !== 1 ? 's' : ''} in CelesTrak
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {searchResults.map((sat) => (
                  <Link
                    key={sat.norad_cat_id}
                    href={`/satellite/${sat.norad_cat_id}`}
                    className="flex items-center justify-between p-3 rounded-xl bg-bg-elevated/50 hover:bg-bg-elevated border border-border-subtle hover:border-accent-primary/40 transition-all duration-150 group"
                  >
                    <div className="min-w-0 pr-3">
                      <div className="font-sans font-semibold text-xs text-text-primary group-hover:text-accent-primary transition-colors truncate">
                        {sat.object_name}
                      </div>
                      <div className="text-[11px] font-mono text-text-tertiary">
                        NORAD {sat.norad_cat_id} · {sat.object_type || 'PAYLOAD'}
                      </div>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      {sat.mean_altitude_km != null && (
                        <span className="text-xs font-mono text-text-secondary">
                          {Math.round(sat.mean_altitude_km)} km
                        </span>
                      )}
                      <span className="text-xs font-mono text-accent-primary group-hover:translate-x-0.5 transition-transform flex items-center">
                        <ArrowRight className="w-3.5 h-3.5" />
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            </motion.div>
          )}

          {searchResults && searchResults.length === 0 && !searching && (
            <div className="mt-4 p-4 text-center rounded-xl bg-bg-elevated/30 border border-border-subtle text-xs text-text-tertiary">
              No matching satellites found in CelesTrak database. Please check the NORAD catalog number or spelling.
            </div>
          )}
        </div>

        {/* Demo Summary Stats Cards */}
        {demo && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 mb-8">
            {[
              {
                label: 'Monitored Fleet',
                value: demo.summary.total_satellites,
                color: 'text-text-primary',
                desc: 'Active cataloged objects',
              },
              {
                label: 'Compliant',
                value: demo.summary.compliant,
                color: 'text-status-pass',
                desc: 'Passes all regulations',
              },
              {
                label: 'At Risk',
                value: demo.summary.at_risk,
                color: 'text-status-flag',
                desc: 'Near threshold limits',
              },
              {
                label: 'Non-Compliant',
                value: demo.summary.non_compliant,
                color: 'text-status-fail',
                desc: 'Violates statutory limits',
              },
              {
                label: 'Fleet Score',
                value: `${Math.round(demo.summary.average_score)}`,
                color: 'text-accent-primary',
                desc: 'Average / 100 benchmark',
              },
            ].map(({ label, value, color, desc }) => (
              <div key={label} className="pharos-card p-4 flex flex-col justify-between">
                <div>
                  <div className={`text-2xl sm:text-3xl font-bold font-mono ${color} mb-1`}>
                    {value}
                  </div>
                  <div className="text-[11px] font-mono font-semibold uppercase text-text-primary tracking-wide">
                    {label}
                  </div>
                </div>
                <div className="text-[10px] text-text-tertiary font-sans mt-2 pt-2 border-t border-border-subtle truncate">
                  {desc}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Filter Controls Row */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs font-mono text-text-tertiary mr-2 uppercase tracking-wide">
              Filter By:
            </span>
            {[
              { key: 'ALL', label: 'ALL SATELLITES' },
              { key: 'COMPLIANT', label: 'COMPLIANT' },
              { key: 'AT_RISK', label: 'AT RISK' },
              { key: 'NON_COMPLIANT', label: 'NON-COMPLIANT' },
            ].map(({ key, label }) => {
              const active = statusFilter === key
              return (
                <button
                  key={key}
                  type="button"
                  onClick={() => setStatusFilter(key)}
                  className={`px-3 py-1.5 rounded-full text-xs font-mono font-semibold transition-all duration-150 ${
                    active
                      ? 'bg-accent-primary text-white border border-accent-primary shadow-glow-primary'
                      : 'bg-bg-surface hover:bg-bg-elevated text-text-secondary hover:text-text-primary border border-border-subtle'
                  }`}
                >
                  {label}
                </button>
              )
            })}
          </div>

          <div className="text-xs font-mono text-text-tertiary">
            Showing {displaySatellites.length} satellite{displaySatellites.length !== 1 ? 's' : ''}
          </div>
        </div>

        {/* Loading Skeletons */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonCard key={i} height={230} />
            ))}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="pharos-card p-8 text-center bg-status-fail-bg border border-status-fail/20 rounded-2xl max-w-lg mx-auto">
            <div className="w-10 h-10 rounded-full bg-status-fail/20 text-status-fail flex items-center justify-center mx-auto mb-3">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-status-fail mb-1">
              Failed to load satellite dataset
            </h3>
            <p className="text-xs text-text-secondary mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="btn-secondary text-xs py-2 px-4 rounded-lg"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Satellites Grid */}
        {!loading && !error && (
          <motion.div
            layout
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"
          >
            <AnimatePresence>
              {displaySatellites.map((sat) => (
                <motion.div
                  key={sat.norad_cat_id}
                  layout
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                >
                  <SatelliteCard satellite={sat} />
                </motion.div>
              ))}
            </AnimatePresence>
          </motion.div>
        )}

        {/* Empty State */}
        {!loading && !error && displaySatellites.length === 0 && (
          <div className="pharos-card p-12 text-center border border-dashed border-border-subtle rounded-2xl">
            <Layers className="w-8 h-8 text-text-tertiary mx-auto mb-2" />
            <div className="text-sm font-semibold text-text-primary mb-1">
              No satellites found
            </div>
            <p className="text-xs text-text-secondary max-w-sm mx-auto mb-4">
              No satellites currently in the catalog match the selected filter &quot;{statusFilter.replace('_', ' ')}&quot;.
            </p>
            <button
              onClick={() => setStatusFilter('ALL')}
              className="btn-secondary text-xs py-1.5 px-3 rounded-lg font-mono"
            >
              Reset Filter
            </button>
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}
