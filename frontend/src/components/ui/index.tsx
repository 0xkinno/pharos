'use client'

import type { RuleStatus, ComplianceLevel } from '@/lib/types'

// Status color utilities
export function getStatusColor(status: RuleStatus | ComplianceLevel): string {
  switch (status) {
    case 'PASS':
    case 'COMPLIANT':
      return 'var(--status-pass)'
    case 'FLAG':
    case 'AT_RISK':
      return 'var(--status-flag)'
    case 'FAIL':
    case 'NON_COMPLIANT':
      return 'var(--status-fail)'
    default:
      return 'var(--status-skip)'
  }
}

export function getStatusBgColor(status: RuleStatus | ComplianceLevel): string {
  switch (status) {
    case 'PASS':
    case 'COMPLIANT':
      return 'var(--status-pass-bg)'
    case 'FLAG':
    case 'AT_RISK':
      return 'var(--status-flag-bg)'
    case 'FAIL':
    case 'NON_COMPLIANT':
      return 'var(--status-fail-bg)'
    default:
      return 'var(--status-skip-bg)'
  }
}

interface StatusBadgeProps {
  status: RuleStatus | ComplianceLevel
  size?: 'sm' | 'md'
}

export function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const color = getStatusColor(status)
  const bg = getStatusBgColor(status)

  const label = status === 'AT_RISK' ? 'AT RISK' : status === 'NON_COMPLIANT' ? 'NON-COMPLIANT' : status

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5,
        padding: size === 'sm' ? '2px 8px' : '3px 10px',
        borderRadius: 100,
        fontSize: size === 'sm' ? 10 : 11,
        fontWeight: 600,
        letterSpacing: '0.08em',
        textTransform: 'uppercase',
        color,
        backgroundColor: bg,
        border: `1px solid ${color}40`,
        whiteSpace: 'nowrap',
      }}
    >
      <span
        style={{
          width: size === 'sm' ? 5 : 6,
          height: size === 'sm' ? 5 : 6,
          borderRadius: '50%',
          backgroundColor: color,
          flexShrink: 0,
        }}
      />
      {label}
    </span>
  )
}

// Skeleton loaders
export function SkeletonLine({ width = '100%', height = 16 }: { width?: string | number; height?: number }) {
  return (
    <div
      className="skeleton"
      style={{
        width,
        height,
        borderRadius: 4,
      }}
    />
  )
}

export function SkeletonCard({ height = 120 }: { height?: number }) {
  return (
    <div
      className="pharos-card"
      style={{
        height,
        padding: 20,
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
      }}
    >
      <SkeletonLine width="60%" height={14} />
      <SkeletonLine width="40%" height={12} />
      <SkeletonLine width="80%" height={12} />
    </div>
  )
}

// Compliance score gauge
interface ComplianceGaugeProps {
  score: number
  size?: number
  showLabel?: boolean
}

export function ComplianceGauge({ score, size = 80, showLabel = true }: ComplianceGaugeProps) {
  const radius = (size - 12) / 2
  const circumference = 2 * Math.PI * radius
  const progress = (score / 100) * circumference
  const strokeDashoffset = circumference - progress

  const color =
    score >= 80 ? 'var(--status-pass)' : score >= 50 ? 'var(--status-flag)' : 'var(--status-fail)'

  return (
    <div style={{ position: 'relative', width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--bg-tertiary)"
          strokeWidth={8}
        />
        {/* Progress */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={8}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.6s ease' }}
        />
      </svg>
      {showLabel && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <span
            style={{
              fontSize: size < 70 ? 13 : 16,
              fontWeight: 700,
              color,
              fontFamily: 'monospace',
              lineHeight: 1,
            }}
          >
            {Math.round(score)}
          </span>
          {size >= 80 && (
            <span style={{ fontSize: 9, color: 'var(--text-tertiary)', marginTop: 2 }}>
              /100
            </span>
          )}
        </div>
      )}
    </div>
  )
}

// Monospace data value
export function DataValue({ value, unit }: { value: string | number; unit?: string }) {
  return (
    <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 13 }}>
      {value}
      {unit && (
        <span style={{ fontSize: 11, color: 'var(--text-tertiary)', marginLeft: 4 }}>
          {unit}
        </span>
      )}
    </span>
  )
}
