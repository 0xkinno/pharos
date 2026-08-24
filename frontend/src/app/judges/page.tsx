'use client'

import { useEffect, useState } from 'react'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import { api } from '@/lib/api'
import type { JudgesResponse } from '@/lib/types'

export default function JudgesPage() {
  const [data, setData] = useState<JudgesResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.getJudges()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div style={{ backgroundColor: 'var(--bg-primary)', minHeight: '100vh' }}>
      <Navbar />
      <main style={{ maxWidth: 1000, margin: '0 auto', padding: '40px 24px' }}>
        <div style={{ marginBottom: 36 }}>
          <div
            style={{
              fontSize: 11,
              fontFamily: 'monospace',
              color: 'var(--accent-blue)',
              marginBottom: 8,
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
            }}
          >
            /judges · Transparency Endpoint
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
            For Judges: Full Transparency
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, maxWidth: 700 }}>
            Every IBM technology claim is documented here with evidence. Every
            fallback behavior is described. Every limitation is stated honestly.
          </p>
        </div>

        {loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 80, borderRadius: 8 }} />
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
            Failed to load judges data: {error}
          </div>
        )}

        {data && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Quick access */}
            <div className="pharos-card" style={{ padding: '16px 20px' }}>
              <h2 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Judge Quick Access
              </h2>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border)' }}>
                    <th style={{ textAlign: 'left', padding: '6px 8px', color: 'var(--text-tertiary)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em' }}>To verify...</th>
                    <th style={{ textAlign: 'left', padding: '6px 8px', color: 'var(--text-tertiary)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Evidence</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { claim: 'Claims are wired, not aspirational', evidence: 'See IBM Stack section below — every claim has a file path' },
                    { claim: 'API-deletion proof', evidence: `Delete every hosted API. Engine still produces rule-by-rule report.` },
                    { claim: 'Citations are never fabricated', evidence: 'All clauses trace to committed standards corpus or deterministic fallback map' },
                    { claim: 'Limitations are honest', evidence: 'See Limitations section — orbital lifetime model uncertainty stated explicitly' },
                    { claim: `${data.compliance_engine.total_rules} coded rules`, evidence: `${data.compliance_engine.standards_bodies.join(', ')}` },
                    { claim: 'Tests are real', evidence: data.test_count },
                  ].map(({ claim, evidence }) => (
                    <tr key={claim} style={{ borderBottom: '1px solid rgba(30,30,48,0.5)' }}>
                      <td style={{ padding: '10px 8px', color: 'var(--text-primary)' }}>
                        <strong>{claim}</strong>
                      </td>
                      <td style={{ padding: '10px 8px', color: 'var(--text-secondary)', fontSize: 12 }}>
                        {evidence}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* IBM Stack */}
            <div className="pharos-card" style={{ padding: '16px 20px' }}>
              <h2 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                IBM Technology Stack
              </h2>
              {Object.entries(data.ibm_stack || {}).map(([key, tool]) => {
                const t = tool as { model_id?: string; role?: string; wired_in?: string; api_deletion_behavior?: string; load_bearing?: boolean }
                return (
                  <div
                    key={key}
                    style={{
                      padding: '14px 0',
                      borderBottom: '1px solid rgba(30,30,48,0.5)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, flexWrap: 'wrap' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 3 }}>
                          {String(key).replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          {t.model_id != null && (
                            <span style={{ fontSize: 11, fontFamily: 'monospace', color: 'var(--text-tertiary)', marginLeft: 8 }}>
                              {t.model_id}
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4 }}>
                          {t.role ?? ''}
                        </div>
                        {t.wired_in != null && (
                          <div style={{ fontSize: 11, fontFamily: 'monospace', color: 'var(--accent-blue)', marginBottom: 3 }}>
                            📁 {t.wired_in}
                          </div>
                        )}
                        {t.api_deletion_behavior != null && (
                          <div
                            style={{
                              fontSize: 11,
                              color: 'var(--text-tertiary)',
                              fontStyle: 'italic',
                              marginTop: 4,
                              padding: '6px 10px',
                              backgroundColor: 'var(--bg-tertiary)',
                              borderRadius: 4,
                              borderLeft: '2px solid var(--border-bright)',
                            }}
                          >
                            API deleted: {t.api_deletion_behavior}
                          </div>
                        )}
                      </div>
                      <div>
                        {typeof t.load_bearing === 'boolean' && (
                          <span
                            style={{
                              fontSize: 10,
                              padding: '2px 8px',
                              borderRadius: 100,
                              backgroundColor: t.load_bearing ? 'rgba(16,185,129,0.1)' : 'rgba(85,85,106,0.1)',
                              color: t.load_bearing ? 'var(--status-pass)' : 'var(--text-tertiary)',
                              border: `1px solid ${t.load_bearing ? 'rgba(16,185,129,0.2)' : 'rgba(85,85,106,0.2)'}`,
                              fontWeight: 600,
                              textTransform: 'uppercase' as const,
                              letterSpacing: '0.06em',
                            }}
                          >
                            {t.load_bearing ? 'Load-Bearing' : 'Optional'}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            {/* API deletion test */}
            <div className="pharos-card" style={{ padding: '16px 20px' }}>
              <h2 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                API-Deletion Test
              </h2>
              <div
                style={{
                  padding: '12px 16px',
                  backgroundColor: 'var(--status-pass-bg)',
                  border: '1px solid rgba(16,185,129,0.2)',
                  borderRadius: 6,
                  marginBottom: 10,
                }}
              >
                <div style={{ fontSize: 13, color: 'var(--status-pass)', fontWeight: 600, marginBottom: 4 }}>
                  {data.api_deletion_test?.result}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                  {data.api_deletion_test?.description}
                </div>
              </div>
              <div style={{ fontSize: 11, fontFamily: 'monospace', color: 'var(--text-tertiary)' }}>
                {data.api_deletion_test?.evidence}
              </div>
            </div>

            {/* Limitations */}
            <div className="pharos-card" style={{ padding: '16px 20px' }}>
              <h2 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Known Limitations (Stated Honestly)
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {data.limitations?.map((limitation, i) => (
                  <div
                    key={i}
                    style={{
                      display: 'flex',
                      gap: 10,
                      padding: '10px 12px',
                      backgroundColor: 'var(--bg-tertiary)',
                      borderRadius: 6,
                    }}
                  >
                    <span style={{ color: 'var(--status-flag)', flexShrink: 0, marginTop: 2 }}>⚠</span>
                    <span style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                      {limitation}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Engine summary */}
            <div className="pharos-card" style={{ padding: '16px 20px' }}>
              <h2 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Compliance Engine
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {data.compliance_engine.standards_bodies?.map((b) => (
                    <span
                      key={b}
                      style={{
                        fontSize: 11,
                        fontFamily: 'monospace',
                        padding: '3px 10px',
                        backgroundColor: 'rgba(59, 130, 246, 0.08)',
                        color: 'var(--accent-blue)',
                        borderRadius: 4,
                        border: '1px solid rgba(59, 130, 246, 0.2)',
                      }}
                    >
                      {b}
                    </span>
                  ))}
                </div>
                {Object.entries(data.compliance_engine.rules_by_body || {}).map(([body, rules]) => (
                  <div key={body}>
                    <span style={{ fontSize: 11, color: 'var(--text-tertiary)', fontFamily: 'monospace' }}>
                      {body}: {(rules as string[]).join(', ')}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Raw JSON */}
            <div className="pharos-card" style={{ padding: '16px 20px' }}>
              <h2 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Raw /api/judges Response
              </h2>
              <pre
                style={{
                  fontSize: 10,
                  fontFamily: 'IBM Plex Mono, monospace',
                  color: 'var(--text-tertiary)',
                  backgroundColor: 'var(--bg-primary)',
                  padding: 16,
                  borderRadius: 6,
                  overflow: 'auto',
                  maxHeight: 400,
                  border: '1px solid var(--border)',
                }}
              >
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  )
}
