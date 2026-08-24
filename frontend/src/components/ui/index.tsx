'use client'

import React, { useEffect, useState, useRef } from 'react'
import { motion, useInView, animate } from 'framer-motion'
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

export function getStatusClass(status: RuleStatus | ComplianceLevel): string {
  switch (status) {
    case 'PASS':
    case 'COMPLIANT':
      return 'status-badge-pass'
    case 'FLAG':
    case 'AT_RISK':
      return 'status-badge-flag'
    case 'FAIL':
    case 'NON_COMPLIANT':
      return 'status-badge-fail'
    default:
      return 'status-badge-skip'
  }
}

interface StatusBadgeProps {
  status: RuleStatus | ComplianceLevel
  size?: 'sm' | 'md'
  showIcon?: boolean
}

export function StatusBadge({ status, size = 'md', showIcon = true }: StatusBadgeProps) {
  const color = getStatusColor(status)
  const statusClass = getStatusClass(status)
  const label =
    status === 'AT_RISK'
      ? 'AT RISK'
      : status === 'NON_COMPLIANT'
      ? 'NON-COMPLIANT'
      : status === 'COMPLIANT'
      ? 'COMPLIANT'
      : status

  return (
    <span
      className={`status-badge ${statusClass} ${
        size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-[11px]'
      }`}
    >
      {showIcon && (
        <span
          className="rounded-full inline-block shrink-0"
          style={{
            width: size === 'sm' ? 5 : 6,
            height: size === 'sm' ? 5 : 6,
            backgroundColor: color,
            boxShadow: `0 0 6px ${color}`,
          }}
        />
      )}
      {label}
    </span>
  )
}

// Animated Compliance Score Gauge
interface ComplianceGaugeProps {
  score: number
  size?: number
  strokeWidth?: number
  showLabel?: boolean
}

export function ComplianceGauge({
  score,
  size = 80,
  strokeWidth = 7,
  showLabel = true,
}: ComplianceGaugeProps) {
  const radius = (size - strokeWidth * 2) / 2
  const circumference = 2 * Math.PI * radius
  const color =
    score >= 80 ? 'var(--status-pass)' : score >= 50 ? 'var(--status-flag)' : 'var(--status-fail)'

  return (
    <div className="relative inline-flex items-center justify-center shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        {/* Background Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--border-subtle)"
          strokeWidth={strokeWidth}
        />
        {/* Animated Progress Arc */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference - (Math.min(Math.max(score, 0), 100) / 100) * circumference }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          strokeLinecap="round"
        />
      </svg>
      {showLabel && (
        <div className="absolute inset-0 flex flex-col items-center justify-center select-none pointer-events-none">
          <span
            className="font-mono font-bold leading-none"
            style={{
              fontSize: size < 65 ? 13 : size < 90 ? 16 : 22,
              color,
            }}
          >
            {Math.round(score)}
          </span>
          {size >= 80 && (
            <span className="text-[9px] text-text-tertiary font-mono tracking-tight mt-0.5">
              /100
            </span>
          )}
        </div>
      )}
    </div>
  )
}

// Animated Number Counter on Scroll Into View
interface NumberCounterProps {
  value: number | string
  suffix?: string
  prefix?: string
  duration?: number
}

export function NumberCounter({
  value,
  suffix = '',
  prefix = '',
  duration = 1.2,
}: NumberCounterProps) {
  const ref = useRef<HTMLSpanElement>(null)
  const isInView = useInView(ref, { once: true, margin: '-20px' })
  const [displayValue, setDisplayValue] = useState<string>(
    typeof value === 'number' ? '0' : value.toString().replace(/[0-9]/g, '0')
  )

  useEffect(() => {
    if (!isInView) return

    if (typeof value === 'number') {
      const controls = animate(0, value, {
        duration,
        ease: [0.16, 1, 0.3, 1],
        onUpdate(latest) {
          setDisplayValue(Math.floor(latest).toLocaleString())
        },
      })
      return () => controls.stop()
    } else {
      // String with numbers, e.g. "16,000+" or "20+"
      const numMatch = value.match(/[\d,]+/)
      if (numMatch) {
        const rawNum = parseInt(numMatch[0].replace(/,/g, ''), 10)
        const restSuffix = value.slice(numMatch.index! + numMatch[0].length)
        const restPrefix = value.slice(0, numMatch.index!)

        const controls = animate(0, rawNum, {
          duration,
          ease: [0.16, 1, 0.3, 1],
          onUpdate(latest) {
            setDisplayValue(
              `${restPrefix}${Math.floor(latest).toLocaleString()}${restSuffix}`
            )
          },
        })
        return () => controls.stop()
      } else {
        setDisplayValue(value)
      }
    }
  }, [isInView, value, duration])

  return (
    <span ref={ref} className="font-mono">
      {prefix}
      {displayValue}
      {suffix}
    </span>
  )
}

// Monospace Data Value with optional Unit
export function DataValue({
  value,
  unit,
  highlight = false,
}: {
  value: string | number
  unit?: string
  highlight?: boolean
}) {
  return (
    <span className={`font-mono text-[13px] ${highlight ? 'text-accent-primary font-medium' : 'text-text-primary'}`}>
      {value}
      {unit && (
        <span className="text-[11px] text-text-tertiary ml-1 font-normal">
          {unit}
        </span>
      )}
    </span>
  )
}

// Shimmer Skeleton Elements
export function SkeletonLine({
  width = '100%',
  height = 16,
  className = '',
}: {
  width?: string | number
  height?: number
  className?: string
}) {
  return (
    <div
      className={`skeleton ${className}`}
      style={{
        width,
        height,
      }}
    />
  )
}

export function SkeletonCard({ height = 180 }: { height?: number }) {
  return (
    <div
      className="pharos-card p-5 flex flex-col justify-between"
      style={{ height }}
    >
      <div className="flex justify-between items-start">
        <div className="space-y-2 w-3/4">
          <SkeletonLine width="60%" height={16} />
          <SkeletonLine width="40%" height={12} />
        </div>
        <SkeletonLine width={40} height={40} className="rounded-full" />
      </div>
      <div className="space-y-2 my-3">
        <SkeletonLine width="85%" height={12} />
        <SkeletonLine width="65%" height={12} />
      </div>
      <div className="flex justify-between items-center pt-2 border-t border-border-subtle">
        <SkeletonLine width="30%" height={18} className="rounded-full" />
        <SkeletonLine width="25%" height={12} />
      </div>
    </div>
  )
}
