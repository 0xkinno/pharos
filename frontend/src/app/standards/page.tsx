'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import { api } from '@/lib/api'
import type { StandardsResponse } from '@/lib/types'
import { BookOpen, ShieldCheck, ChevronDown, ChevronUp, Scale, BookmarkCheck } from 'lucide-react'

const BODY_DESCRIPTIONS: Record<string, { title: string; desc: string; region: string }> = {
  FCC: {
    title: 'Federal Communications Commission',
    desc: 'Regulates US-licensed commercial satellite systems. The 5-year deorbit rule (47 CFR Part 25.114) became legally enforceable in September 2024 with substantial non-compliance penalties.',
    region: 'United States',
  },
  IADC: {
    title: 'Inter-Agency Space Debris Coordination Committee',
    desc: '13-agency international committee comprising NASA, ESA, JAXA, ISRO, and others. The IADC 25-year post-mission guideline serves as the foundational consensus baseline for LEO disposal.',
    region: 'Global / 13 Space Agencies',
  },
  ISO: {
    title: 'International Organization for Standardization',
    desc: 'ISO 24113:2019 defines explicit protected orbital regions, probability of collision thresholds, and operational spacecraft disposal standards for commercial aerospace manufacturing.',
    region: 'International Standards',
  },
  ESA: {
    title: 'European Space Agency Zero Debris Charter',
    desc: 'Adopted in November 2023. Mandates ambitious near-zero debris creation by 2030, establishing a rigorous 99% casualty risk threshold and aggressive disposal timelines.',
    region: 'European Union',
  },
  COPUOS: {
    title: 'UN Committee on the Peaceful Uses of Outer Space',
    desc: '21 Long-Term Sustainability Guidelines (2019) covering mandatory space object registration, international SSA telemetry sharing, and collision risk avoidance protocols.',
    region: 'United Nations / Global',
  },
}

const SEVERITY_STYLES: Record<string, { text: string; bg: string; border: string }> = {
  critical: {
    text: 'text-status-fail',
    bg: 'bg-status-fail/10',
    border: 'border-status-fail/20',
  },
  high: {
    text: 'text-status-flag',
    bg: 'bg-status-flag/10',
    border: 'border-status-flag/20',
  },
  medium: {
    text: 'text-accent-primary',
    bg: 'bg-accent-primary/10',
    border: 'border-accent-primary/20',
  },
  low: {
    text: 'text-text-secondary',
    bg: 'bg-bg-elevated',
    border: 'border-border-subtle',
  },
}

export default function StandardsPage() {
  const [data, setData] = useState<StandardsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedBody, setExpandedBody] = useState<string | null>('FCC')

  useEffect(() => {
    api.getStandards()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="bg-bg-base text-text-primary min-h-screen">
      <Navbar />

      <main className="max-w-container mx-auto px-4 sm:px-6 pt-28 pb-20">
        {/* Page Header */}
        <div className="mb-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-primary/10 border border-accent-primary/20 text-accent-primary text-xs font-mono uppercase tracking-wider mb-2.5">
            <Scale className="w-3.5 h-3.5" />
            <span>Statutory Knowledge Base · 5 Space Jurisdictions</span>
          </div>
          <h1 className="font-display text-2xl sm:text-4xl font-bold tracking-tight text-text-primary mb-2">
            Standards Explorer
          </h1>
          <p className="text-xs sm:text-sm text-text-secondary max-w-2xl leading-relaxed">
            Every PHAROS rule evaluates deterministically against committed standard clauses.
            Explore all coded statutory thresholds and regulatory requirements below.
          </p>
        </div>

        {/* Loading Skeletons */}
        {loading && (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="pharos-card p-6 h-24 skeleton" />
            ))}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="pharos-card p-6 bg-status-fail-bg border border-status-fail/20 rounded-xl text-center text-status-fail text-xs">
            Failed to load regulatory standards: {error}
          </div>
        )}

        {/* Body Cards List */}
        {data && (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs font-mono text-text-tertiary mb-2 px-1">
              <span>{data.total_rules} Total Statutory Coded Rules</span>
              <span>5 Verified Space Jurisdictions</span>
            </div>

            {data.bodies.map((body) => {
              const info = BODY_DESCRIPTIONS[body.body] || {
                title: body.body,
                desc: 'Regulatory standards body',
                region: 'Global',
              }
              const isExpanded = expandedBody === body.body

              return (
                <div
                  key={body.body}
                  className={`pharos-card overflow-hidden border transition-all duration-200 ${
                    isExpanded ? 'border-border-hover bg-bg-surface/95' : 'border-border-subtle hover:border-border-hover'
                  }`}
                >
                  {/* Body Accordion Header */}
                  <button
                    type="button"
                    onClick={() => setExpandedBody(isExpanded ? null : body.body)}
                    className="w-full p-5 sm:p-6 text-left flex items-start sm:items-center justify-between gap-4 cursor-pointer focus:outline-none transition-colors"
                  >
                    <div className="space-y-1.5 flex-1 min-w-0">
                      <div className="flex items-center gap-2.5 flex-wrap">
                        <span className="font-mono text-xs font-bold text-accent-primary px-2.5 py-1 rounded-md bg-accent-primary/10 border border-accent-primary/20">
                          {body.body}
                        </span>
                        <span className="font-sans font-bold text-sm sm:text-base text-text-primary">
                          {info.title}
                        </span>
                        <span className="text-[11px] font-mono text-text-tertiary px-2 py-0.5 rounded bg-bg-elevated border border-border-subtle hidden sm:inline-block">
                          {info.region}
                        </span>
                        <span className="text-xs font-mono text-accent-cyan ml-auto sm:ml-0 font-medium">
                          {body.rules.length} Rules Active
                        </span>
                      </div>

                      <p className="text-xs text-text-secondary leading-relaxed max-w-3xl">
                        {info.desc}
                      </p>
                    </div>

                    <div className="text-text-tertiary p-1 shrink-0">
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5 text-accent-primary" />
                      ) : (
                        <ChevronDown className="w-5 h-5" />
                      )}
                    </div>
                  </button>

                  {/* Rules Sub-list */}
                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.2 }}
                        className="border-t border-border-subtle divide-y divide-border-subtle bg-bg-elevated/20"
                      >
                        {body.rules.map((rule) => {
                          const severity = SEVERITY_STYLES[rule.severity] || SEVERITY_STYLES.medium

                          return (
                            <div key={rule.id} className="p-5 sm:p-6 hover:bg-bg-elevated/40 transition-colors">
                              <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                                <div className="space-y-2 flex-1">
                                  {/* Rule Meta Row */}
                                  <div className="flex items-center gap-2 flex-wrap">
                                    <span className="font-mono text-xs font-bold text-accent-primary">
                                      {rule.id}
                                    </span>
                                    <span
                                      className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded uppercase tracking-wider ${severity.bg} ${severity.text} border ${severity.border}`}
                                    >
                                      {rule.severity} Priority
                                    </span>
                                    <span className="text-xs font-mono text-text-tertiary">
                                      Clause: <strong className="text-text-secondary">{rule.standard}</strong>
                                    </span>
                                  </div>

                                  {/* Title & Description */}
                                  <h3 className="font-sans font-bold text-sm text-text-primary">
                                    {rule.title}
                                  </h3>
                                  <p className="text-xs text-text-secondary leading-relaxed font-sans max-w-3xl">
                                    {rule.description}
                                  </p>
                                </div>

                                {/* Rule Threshold Card */}
                                {rule.threshold && (
                                  <div className="p-3 rounded-xl bg-bg-surface border border-border-subtle shrink-0 min-w-[200px]">
                                    <div className="text-[10px] font-mono text-text-tertiary uppercase tracking-wider mb-1.5 flex items-center gap-1">
                                      <BookmarkCheck className="w-3 h-3 text-accent-primary" />
                                      <span>Rule Threshold</span>
                                    </div>
                                    <div className="space-y-1">
                                      {Object.entries(rule.threshold).map(([k, v]) => (
                                        <div key={k} className="text-xs font-mono flex items-center justify-between gap-2">
                                          <span className="text-text-secondary capitalize">
                                            {k.replace(/_/g, ' ')}:
                                          </span>
                                          <span className="font-bold text-accent-cyan">
                                            {v}
                                          </span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          )
                        })}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )
            })}
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}
