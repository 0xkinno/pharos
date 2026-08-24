'use client'

import { useEffect, useState } from 'react'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import { api } from '@/lib/api'
import type { StandardsResponse } from '@/lib/types'

const BODY_DESCRIPTIONS: Record<string, string> = {
  FCC: 'Federal Communications Commission — Regulates US-licensed satellites. The 5-year deorbit rule (47 CFR Part 25.114) has been in effect since September 2024.',
  IADC: 'Inter-Agency Space Debris Coordination Committee — 13-agency international body. The IADC 25-year guideline is the foundational international consensus for LEO disposal.',
  ISO: 'International Organization for Standardization — ISO 24113:2019 defines protected orbital regions and disposal requirements for the global space industry.',
  ESA: 'European Space Agency Zero Debris Charter — Adopted November 2023. Targets near-zero debris creation by 2030. More stringent than existing guidelines.',
  COPUOS: 'UN Committee on the Peaceful Uses of Outer Space — 21 Long-Term Sustainability Guidelines (2019) covering registration, data sharing, and operational best practices.',
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: 'var(--status-fail)',
  high: 'var(--status-flag)',
  medium: 'var(--accent-blue)',
  low: 'var(--text-secondary)',
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
    <div style={{ backgroundColor: 'var(--bg-primary)', minHeight: '100vh' }}>
      <Navbar />
      <main style={{ maxWidth: 1100, margin: '0 auto', padding: '40px 24px' }}>
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 6 }}>
            Standards Explorer
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, maxWidth: 700 }}>
            PHAROS codes rules from 5 regulatory bodies. Every rule maps to a specific
            clause in a specific standard. AI never determines compliance — it only
            explains what the deterministic engine found.
          </p>
        </div>

        {loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 60, borderRadius: 8 }} />
            ))}
          </div>
        )}

        {error && (
          <div
            style={{
              padding: 24,
              backgroundColor: 'var(--status-fail-bg)',
              border: '1px solid rgba(239,68,68,0.2)',
              borderRadius: 8,
              color: 'var(--status-fail)',
            }}
          >
            {error}
          </div>
        )}

        {data && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div
              style={{
                display: 'flex',
                gap: 8,
                marginBottom: 8,
                fontSize: 13,
                color: 'var(--text-tertiary)',
              }}
            >
              <span style={{ fontFamily: 'monospace' }}>{data.total_rules} total coded rules</span>
              <span>·</span>
              <span>5 regulatory bodies</span>
            </div>

            {data.bodies.map((body) => (
              <div key={body.body} className="pharos-card" style={{ overflow: 'hidden' }}>
                {/* Body header */}
                <button
                  onClick={() => setExpandedBody(expandedBody === body.body ? null : body.body)}
                  style={{
                    width: '100%',
                    padding: '16px 20px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    textAlign: 'left',
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span
                        style={{
                          fontSize: 13,
                          fontWeight: 700,
                          fontFamily: 'monospace',
                          color: 'var(--accent-blue)',
                          padding: '2px 8px',
                          background: 'rgba(59, 130, 246, 0.1)',
                          borderRadius: 4,
                        }}
                      >
                        {body.body}
                      </span>
                      <span
                        style={{
                          fontSize: 12,
                          color: 'var(--text-tertiary)',
                          fontFamily: 'monospace',
                        }}
                      >
                        {body.rules.length} rules
                      </span>
                    </div>
                    <div
                      style={{
                        fontSize: 12,
                        color: 'var(--text-secondary)',
                        marginTop: 4,
                        maxWidth: 700,
                      }}
                    >
                      {BODY_DESCRIPTIONS[body.body]}
                    </div>
                  </div>
                  <span style={{ color: 'var(--text-tertiary)', fontSize: 14, marginLeft: 16 }}>
                    {expandedBody === body.body ? '▲' : '▼'}
                  </span>
                </button>

                {/* Rules list */}
                {expandedBody === body.body && (
                  <div style={{ borderTop: '1px solid var(--border)' }}>
                    {body.rules.map((rule, i) => (
                      <div
                        key={rule.id}
                        style={{
                          padding: '14px 20px',
                          borderBottom: i < body.rules.length - 1 ? '1px solid rgba(30,30,48,0.5)' : 'none',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
                          <div style={{ flex: 1 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                              <span
                                style={{
                                  fontSize: 11,
                                  fontFamily: 'monospace',
                                  color: 'var(--accent-blue)',
                                  fontWeight: 600,
                                }}
                              >
                                {rule.id}
                              </span>
                              <span
                                style={{
                                  fontSize: 10,
                                  padding: '1px 6px',
                                  borderRadius: 3,
                                  color: SEVERITY_COLORS[rule.severity] || 'var(--text-tertiary)',
                                  backgroundColor: `${SEVERITY_COLORS[rule.severity] || 'var(--text-tertiary)'}15`,
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.06em',
                                  fontWeight: 600,
                                }}
                              >
                                {rule.severity}
                              </span>
                            </div>
                            <div style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 500, marginBottom: 3 }}>
                              {rule.title}
                            </div>
                            <div style={{ fontSize: 11, color: 'var(--text-tertiary)', fontFamily: 'monospace', marginBottom: 5 }}>
                              {rule.standard}
                            </div>
                            <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                              {rule.description}
                            </div>
                          </div>

                          {rule.threshold && (
                            <div
                              style={{
                                flexShrink: 0,
                                backgroundColor: 'var(--bg-primary)',
                                border: '1px solid var(--border)',
                                borderRadius: 6,
                                padding: '8px 12px',
                                minWidth: 120,
                              }}
                            >
                              <div style={{ fontSize: 10, color: 'var(--text-tertiary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                                Threshold
                              </div>
                              {Object.entries(rule.threshold).map(([k, v]) => (
                                <div key={k} style={{ fontSize: 11, fontFamily: 'monospace', color: 'var(--text-secondary)' }}>
                                  {k.replace(/_/g, ' ')}: {v}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
      <Footer />
    </div>
  )
}
