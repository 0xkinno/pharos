'use client'

import Link from 'next/link'
import { ComplianceGauge, StatusBadge, DataValue } from '@/components/ui'
import type { DemoSatelliteSummary } from '@/lib/types'
import { ArrowUpRight } from 'lucide-react'

interface SatelliteCardProps {
  satellite: DemoSatelliteSummary
}

export default function SatelliteCard({ satellite: sat }: SatelliteCardProps) {
  const totalRules = Math.max(sat.rules_passed + sat.rules_flagged + sat.rules_failed, 1)
  const passedWidth = (sat.rules_passed / totalRules) * 100
  const flaggedWidth = (sat.rules_flagged / totalRules) * 100
  const failedWidth = (sat.rules_failed / totalRules) * 100

  return (
    <Link
      href={`/satellite/${sat.norad_cat_id}`}
      className="group block text-decoration-none h-full"
    >
      <div className="pharos-card pharos-card-hoverable p-5 flex flex-col justify-between h-full relative border border-border-subtle hover:border-border-hover transition-all duration-200">
        <div>
          {/* Header Row: Satellite Name, NORAD ID, and Mini Score Gauge */}
          <div className="flex items-start justify-between gap-3 mb-4">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-sans font-bold text-sm text-text-primary truncate group-hover:text-accent-primary transition-colors">
                  {sat.object_name}
                </h3>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-bg-elevated text-text-secondary border border-border-subtle shrink-0">
                  {sat.orbit_type}
                </span>
              </div>
              <div className="text-xs font-mono text-text-tertiary">
                NORAD {sat.norad_cat_id}
              </div>
            </div>
            <ComplianceGauge score={sat.compliance_score} size={48} strokeWidth={5} />
          </div>

          {/* Description snippet if present */}
          {sat.description && (
            <p className="text-xs text-text-secondary line-clamp-2 mb-4 leading-relaxed font-normal">
              {sat.description}
            </p>
          )}

          {/* Data Grid: Altitude & Est. Lifetime */}
          <div className="grid grid-cols-2 gap-3 py-3 border-y border-border-subtle mb-4">
            <div>
              <div className="text-[10px] font-mono text-text-tertiary uppercase tracking-wider mb-0.5">
                Mean Altitude
              </div>
              <DataValue value={Math.round(sat.mean_altitude_km)} unit="km" />
            </div>
            <div>
              <div className="text-[10px] font-mono text-text-tertiary uppercase tracking-wider mb-0.5">
                Est. Lifetime
              </div>
              <DataValue
                value={
                  sat.estimated_orbital_lifetime_years >= 999
                    ? '> 999'
                    : sat.estimated_orbital_lifetime_years.toFixed(1)
                }
                unit={sat.estimated_orbital_lifetime_years < 999 ? 'yrs' : 'yrs'}
              />
            </div>
          </div>

          {/* Rule Breakdown Mini Progress Bar */}
          <div className="space-y-1.5 mb-4">
            <div className="flex h-1.5 w-full rounded-full overflow-hidden bg-bg-elevated">
              {passedWidth > 0 && (
                <div
                  style={{ width: `${passedWidth}%` }}
                  className="bg-status-pass transition-all duration-500"
                />
              )}
              {flaggedWidth > 0 && (
                <div
                  style={{ width: `${flaggedWidth}%` }}
                  className="bg-status-flag transition-all duration-500"
                />
              )}
              {failedWidth > 0 && (
                <div
                  style={{ width: `${failedWidth}%` }}
                  className="bg-status-fail transition-all duration-500"
                />
              )}
            </div>
            <div className="flex items-center justify-between text-[11px] font-mono">
              <span className="text-status-pass">✓ {sat.rules_passed}</span>
              <span className="text-status-flag">⚠ {sat.rules_flagged}</span>
              <span className="text-status-fail">✗ {sat.rules_failed}</span>
            </div>
          </div>
        </div>

        {/* Footer: Status Badge and View Report link */}
        <div className="flex items-center justify-between pt-2 border-t border-border-subtle">
          <StatusBadge status={sat.compliance_level} size="sm" />
          <span className="text-xs font-mono text-accent-primary inline-flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform">
            <span>Report</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </span>
        </div>
      </div>
    </Link>
  )
}
