'use client'

import Link from 'next/link'
import { ComplianceGauge, StatusBadge, DataValue } from '@/components/ui'
import type { DemoSatelliteSummary } from '@/lib/types'

interface SatelliteCardProps {
  satellite: DemoSatelliteSummary
}

export default function SatelliteCard({ satellite: sat }: SatelliteCardProps) {
  const passedWidth = (sat.rules_passed / Math.max(sat.rules_passed + sat.rules_flagged + sat.rules_failed, 1)) * 100
  const flaggedWidth = (sat.rules_flagged / Math.max(sat.rules_passed + sat.rules_flagged + sat.rules_failed, 1)) * 100
  const failedWidth = (sat.rules_failed / Math.max(sat.rules_passed + sat.rules_flagged + sat.rules_failed, 1)) * 100

  return (
    <Link
      href={`/satellite/${sat.norad_cat_id}`}
      style={{ textDecoration: 'none' }}
    >
      <div
        className="pharos-card pharos-card-glow"
        style={{
          padding: 20,
          cursor: 'pointer',
          transition: 'border-color 150ms, transform 150ms',
          display: 'flex',
          flexDirection: 'column',
          gap: 14,
          height: '100%',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)'
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
          <div>
            <div
              style={{
                fontSize: 14,
                fontWeight: 600,
                color: 'var(--text-primary)',
                marginBottom: 3,
                lineHeight: 1.3,
              }}
            >
              {sat.object_name}
            </div>
            <div
              style={{
                fontSize: 11,
                color: 'var(--text-tertiary)',
                fontFamily: 'IBM Plex Mono, monospace',
              }}
            >
              NORAD {sat.norad_cat_id} · {sat.orbit_type}
            </div>
          </div>
          <ComplianceGauge score={sat.compliance_score} size={56} />
        </div>

        {/* Altitude */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 8,
          }}
        >
          <div>
            <div style={{ fontSize: 10, color: 'var(--text-tertiary)', marginBottom: 2, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Altitude
            </div>
            <DataValue value={Math.round(sat.mean_altitude_km)} unit="km" />
          </div>
          <div>
            <div style={{ fontSize: 10, color: 'var(--text-tertiary)', marginBottom: 2, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Est. Lifetime
            </div>
            <DataValue
              value={sat.estimated_orbital_lifetime_years >= 999 ? '∞' : sat.estimated_orbital_lifetime_years.toFixed(1)}
              unit={sat.estimated_orbital_lifetime_years < 999 ? 'yr' : undefined}
            />
          </div>
        </div>

        {/* Rule bar */}
        <div>
          <div
            style={{
              display: 'flex',
              height: 4,
              borderRadius: 2,
              overflow: 'hidden',
              backgroundColor: 'var(--bg-tertiary)',
              gap: 1,
            }}
          >
            {passedWidth > 0 && (
              <div
                style={{
                  width: `${passedWidth}%`,
                  backgroundColor: 'var(--status-pass)',
                  borderRadius: '2px 0 0 2px',
                }}
              />
            )}
            {flaggedWidth > 0 && (
              <div
                style={{
                  width: `${flaggedWidth}%`,
                  backgroundColor: 'var(--status-flag)',
                }}
              />
            )}
            {failedWidth > 0 && (
              <div
                style={{
                  width: `${failedWidth}%`,
                  backgroundColor: 'var(--status-fail)',
                  borderRadius: '0 2px 2px 0',
                }}
              />
            )}
          </div>
          <div
            style={{
              display: 'flex',
              gap: 12,
              marginTop: 6,
              fontSize: 11,
              fontFamily: 'monospace',
            }}
          >
            <span style={{ color: 'var(--status-pass)' }}>✓ {sat.rules_passed}</span>
            <span style={{ color: 'var(--status-flag)' }}>⚠ {sat.rules_flagged}</span>
            <span style={{ color: 'var(--status-fail)' }}>✗ {sat.rules_failed}</span>
          </div>
        </div>

        {/* Status badge */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <StatusBadge status={sat.compliance_level} size="sm" />
          <span
            style={{
              fontSize: 11,
              color: 'var(--accent-blue)',
            }}
          >
            View report →
          </span>
        </div>
      </div>
    </Link>
  )
}
