'use client'

import { useState } from 'react'
import { StatusBadge } from '@/components/ui'
import type { RuleResult } from '@/lib/types'

interface RuleResultsTableProps {
  rules: RuleResult[]
  showSkipped?: boolean
}

export default function RuleResultsTable({ rules, showSkipped = false }: RuleResultsTableProps) {
  const [expandedRow, setExpandedRow] = useState<string | null>(null)
  const [filter, setFilter] = useState<'ALL' | 'PASS' | 'FLAG' | 'FAIL'>('ALL')

  const displayed = rules.filter((r) => {
    if (!showSkipped && r.status === 'SKIP') return false
    if (filter !== 'ALL' && r.status !== filter) return false
    return true
  })

  return (
    <div>
      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 16 }}>
        {(['ALL', 'PASS', 'FLAG', 'FAIL'] as const).map((f) => {
          const count =
            f === 'ALL'
              ? rules.filter((r) => r.status !== 'SKIP').length
              : rules.filter((r) => r.status === f).length

          return (
            <button
              key={f}
              onClick={() => setFilter(f)}
              style={{
                padding: '5px 12px',
                borderRadius: 6,
                fontSize: 12,
                fontWeight: 500,
                cursor: 'pointer',
                border: '1px solid',
                transition: 'all 150ms',
                borderColor: filter === f ? 'var(--accent-blue)' : 'var(--border)',
                backgroundColor: filter === f ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                color: filter === f ? 'var(--accent-blue)' : 'var(--text-secondary)',
              }}
            >
              {f} ({count})
            </button>
          )
        })}
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        <table className="pharos-table">
          <thead>
            <tr>
              <th>Rule ID</th>
              <th>Body</th>
              <th>Status</th>
              <th>Value / Threshold</th>
              <th>Standard Clause</th>
            </tr>
          </thead>
          <tbody>
            {displayed.map((rule) => (
              <>
                <tr
                  key={rule.rule_id}
                  onClick={() =>
                    setExpandedRow(expandedRow === rule.rule_id ? null : rule.rule_id)
                  }
                  style={{ cursor: 'pointer' }}
                >
                  <td>
                    <span
                      style={{
                        fontFamily: 'IBM Plex Mono, monospace',
                        fontSize: 12,
                        color: 'var(--accent-blue)',
                      }}
                    >
                      {rule.rule_id}
                    </span>
                  </td>
                  <td>
                    <span
                      style={{
                        fontSize: 11,
                        fontFamily: 'monospace',
                        color: 'var(--text-secondary)',
                        padding: '2px 6px',
                        background: 'var(--bg-tertiary)',
                        borderRadius: 3,
                      }}
                    >
                      {rule.body}
                    </span>
                  </td>
                  <td>
                    <StatusBadge status={rule.status} size="sm" />
                  </td>
                  <td>
                    {rule.value !== null && rule.threshold !== null && rule.unit ? (
                      <span
                        style={{
                          fontFamily: 'monospace',
                          fontSize: 12,
                          color: 'var(--text-secondary)',
                        }}
                      >
                        {typeof rule.value === 'number' ? rule.value.toFixed(2) : rule.value}
                        {' / '}
                        {typeof rule.threshold === 'number' ? rule.threshold.toFixed(2) : rule.threshold}
                        <span style={{ color: 'var(--text-tertiary)', marginLeft: 4 }}>{rule.unit}</span>
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-tertiary)', fontSize: 12 }}>—</span>
                    )}
                  </td>
                  <td>
                    <span
                      style={{
                        fontSize: 12,
                        color: 'var(--text-secondary)',
                        maxWidth: 240,
                        display: 'block',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                      title={rule.standard_clause}
                    >
                      {rule.standard_clause}
                    </span>
                  </td>
                </tr>

                {/* Expanded row */}
                {expandedRow === rule.rule_id && (
                  <tr key={`${rule.rule_id}-expanded`}>
                    <td
                      colSpan={5}
                      style={{
                        backgroundColor: 'var(--bg-primary)',
                        padding: '12px 16px',
                      }}
                    >
                      <div style={{ marginBottom: 10 }}>
                        <div
                          style={{
                            fontSize: 12,
                            color: 'var(--text-secondary)',
                            lineHeight: 1.6,
                            marginBottom: 10,
                          }}
                        >
                          {rule.message}
                        </div>

                        {rule.retrieved_clause_text && (
                          <div
                            style={{
                              padding: '10px 14px',
                              backgroundColor: 'var(--bg-tertiary)',
                              borderLeft: '3px solid var(--accent-blue)',
                              borderRadius: '0 6px 6px 0',
                            }}
                          >
                            <div
                              style={{
                                fontSize: 10,
                                color: 'var(--text-tertiary)',
                                textTransform: 'uppercase',
                                letterSpacing: '0.08em',
                                marginBottom: 6,
                              }}
                            >
                              Standard Clause (retrieved by Granite Embedding)
                            </div>
                            <div
                              style={{
                                fontSize: 12,
                                color: 'var(--text-secondary)',
                                lineHeight: 1.6,
                                fontStyle: 'italic',
                              }}
                            >
                              {rule.retrieved_clause_text}
                            </div>
                            {rule.retrieved_clause_source && (
                              <div
                                style={{
                                  fontSize: 10,
                                  color: 'var(--text-tertiary)',
                                  marginTop: 6,
                                }}
                              >
                                Source: {rule.retrieved_clause_source}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>

      {displayed.length === 0 && (
        <div
          style={{
            textAlign: 'center',
            padding: '32px 0',
            color: 'var(--text-tertiary)',
            fontSize: 13,
          }}
        >
          No rules match the current filter.
        </div>
      )}
    </div>
  )
}
