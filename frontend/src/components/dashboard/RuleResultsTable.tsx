'use client'

import { useState } from 'react'
import { StatusBadge } from '@/components/ui'
import type { RuleResult } from '@/lib/types'
import { CheckCircle2, AlertTriangle, XCircle, ChevronDown, ChevronUp, FileCode2, Sparkles } from 'lucide-react'

interface RuleResultsTableProps {
  rules: RuleResult[]
  showSkipped?: boolean
}

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case 'PASS':
      return <CheckCircle2 className="w-4 h-4 text-status-pass shrink-0" />
    case 'FLAG':
      return <AlertTriangle className="w-4 h-4 text-status-flag shrink-0" />
    case 'FAIL':
      return <XCircle className="w-4 h-4 text-status-fail shrink-0" />
    default:
      return <div className="w-2 h-2 rounded-full bg-text-tertiary shrink-0" />
  }
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
    <div className="w-full space-y-4">
      {/* Filter Tabs */}
      <div className="flex items-center gap-1.5 flex-wrap">
        {(['ALL', 'PASS', 'FLAG', 'FAIL'] as const).map((f) => {
          const count =
            f === 'ALL'
              ? rules.filter((r) => r.status !== 'SKIP').length
              : rules.filter((r) => r.status === f).length

          const active = filter === f
          return (
            <button
              key={f}
              type="button"
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-full text-xs font-mono font-semibold transition-all duration-150 ${
                active
                  ? 'bg-accent-primary text-white border border-accent-primary'
                  : 'bg-bg-elevated/80 text-text-secondary hover:text-text-primary border border-border-subtle hover:border-border-hover'
              }`}
            >
              {f} ({count})
            </button>
          )
        })}
      </div>

      {/* Table Container */}
      <div className="rounded-xl border border-border-subtle overflow-hidden bg-bg-surface">
        <div className="overflow-x-auto">
          <table className="pharos-table">
            <thead>
              <tr>
                <th className="w-8"></th>
                <th>Rule ID</th>
                <th>Body</th>
                <th>Status</th>
                <th>Value / Threshold</th>
                <th>Standard Clause</th>
                <th className="w-8"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {displayed.map((rule) => {
                const isExpanded = expandedRow === rule.rule_id
                return (
                  <tr
                    key={rule.rule_id}
                    onClick={() => setExpandedRow(isExpanded ? null : rule.rule_id)}
                    className="cursor-pointer hover:bg-bg-elevated/40 transition-colors"
                  >
                    <td className="pl-4 pr-1">
                      <StatusIcon status={rule.status} />
                    </td>
                    <td>
                      <span className="font-mono text-xs font-bold text-accent-primary">
                        {rule.rule_id}
                      </span>
                    </td>
                    <td>
                      <span className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded bg-bg-elevated text-text-secondary border border-border-subtle">
                        {rule.body}
                      </span>
                    </td>
                    <td>
                      <StatusBadge status={rule.status} size="sm" />
                    </td>
                    <td>
                      {rule.value !== null && rule.threshold !== null ? (
                        <span className="font-mono text-xs text-text-primary">
                          <span className="font-semibold">
                            {typeof rule.value === 'number' ? rule.value.toFixed(2) : rule.value}
                          </span>
                          <span className="text-text-tertiary mx-1">/</span>
                          <span className="text-text-secondary">
                            {typeof rule.threshold === 'number' ? rule.threshold.toFixed(2) : rule.threshold}
                          </span>
                          {rule.unit && (
                            <span className="text-[10px] text-text-tertiary ml-1 font-sans">
                              {rule.unit}
                            </span>
                          )}
                        </span>
                      ) : (
                        <span className="text-text-tertiary text-xs font-mono">—</span>
                      )}
                    </td>
                    <td className="max-w-[280px]">
                      <span
                        className="text-xs text-text-secondary truncate block font-sans"
                        title={rule.standard_clause}
                      >
                        {rule.standard_clause}
                      </span>
                    </td>
                    <td className="pr-4 text-text-tertiary">
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-accent-primary" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Expanded Row Detail Section */}
        {expandedRow && (() => {
          const rule = rules.find((r) => r.rule_id === expandedRow)
          if (!rule) return null
          return (
            <div className="p-5 bg-bg-elevated/70 border-t border-border-hover space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileCode2 className="w-4 h-4 text-accent-primary" />
                  <span className="font-mono text-xs font-bold text-text-primary">
                    Evaluation Details for {rule.rule_id} ({rule.body})
                  </span>
                </div>
                <StatusBadge status={rule.status} size="sm" />
              </div>

              <p className="text-xs text-text-primary leading-relaxed font-sans bg-bg-surface/80 p-3 rounded-lg border border-border-subtle">
                {rule.message}
              </p>

              {rule.retrieved_clause_text && (
                <div className="p-4 rounded-xl bg-bg-surface border-l-4 border-accent-primary border-y border-r border-border-subtle space-y-2">
                  <div className="flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-wider text-accent-primary font-semibold">
                    <Sparkles className="w-3 h-3" />
                    <span>Statutory Standard Clause (retrieved by IBM Granite Embedding RAG)</span>
                  </div>
                  <p className="text-xs text-text-secondary leading-relaxed italic font-serif pl-1">
                    &ldquo;{rule.retrieved_clause_text}&rdquo;
                  </p>
                  {rule.retrieved_clause_source && (
                    <div className="text-[10px] font-mono text-text-tertiary pt-1 border-t border-border-subtle">
                      Source Authority: {rule.retrieved_clause_source}
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })()}
      </div>

      {displayed.length === 0 && (
        <div className="p-8 text-center text-xs font-mono text-text-tertiary bg-bg-surface rounded-xl border border-border-subtle">
          No compliance rules found for filter category &quot;{filter}&quot;.
        </div>
      )}
    </div>
  )
}
