'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import RuleResultsTable from '@/components/dashboard/RuleResultsTable'
import { ComplianceGauge, StatusBadge, DataValue, SkeletonCard } from '@/components/ui'
import { api, ApiError } from '@/lib/api'
import type { ComplianceReport } from '@/lib/types'
import {
  Download,
  FileCode,
  FileText,
  Sparkles,
  ShieldCheck,
  ChevronLeft,
  Orbit,
  Globe2,
  Calendar,
  Layers,
  AlertCircle
} from 'lucide-react'

export default function SatelliteReportPage() {
  const params = useParams()
  const noradId = Number(params.id)

  const [report, setReport] = useState<ComplianceReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!noradId) return

    // Try demo data first (instant), then live
    api.getDemoSatellite(noradId)
      .then(setReport)
      .catch(() => {
        // Not in demo, fetch live compliance report
        return api.getComplianceReport(noradId, true, true)
          .then(setReport)
      })
      .catch((e: unknown) => {
        setError(e instanceof ApiError ? e.message : 'Failed to load report')
      })
      .finally(() => setLoading(false))
  }, [noradId])

  if (loading) {
    return (
      <div className="bg-bg-base text-text-primary min-h-screen">
        <Navbar />
        <main className="max-w-container mx-auto px-4 sm:px-6 pt-28 pb-16">
          <div className="space-y-6 max-w-4xl mx-auto">
            <SkeletonCard height={160} />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <SkeletonCard height={280} />
              <SkeletonCard height={280} />
            </div>
            <SkeletonCard height={380} />
          </div>
        </main>
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="bg-bg-base text-text-primary min-h-screen">
        <Navbar />
        <main className="max-w-container mx-auto px-4 sm:px-6 pt-32 pb-16">
          <div className="pharos-card p-10 text-center max-w-lg mx-auto bg-status-fail-bg border border-status-fail/20 rounded-2xl">
            <div className="w-12 h-12 rounded-full bg-status-fail/20 text-status-fail flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="w-6 h-6" />
            </div>
            <h2 className="font-sans font-bold text-lg text-status-fail mb-2">
              Satellite Telemetry Not Found
            </h2>
            <p className="text-xs text-text-secondary leading-relaxed mb-6">
              {error || 'Unable to retrieve orbital ephemeris or compliance calculations for this catalog entry.'}
            </p>
            <Link
              href="/dashboard"
              className="btn-primary text-xs py-2.5 px-5 rounded-lg inline-flex items-center gap-2"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Back to Dashboard</span>
            </Link>
          </div>
        </main>
        <Footer />
      </div>
    )
  }

  const jsonUrl = api.getReportJsonUrl(noradId)
  const pdfUrl = api.getReportPdfUrl(noradId)

  return (
    <div className="bg-bg-base text-text-primary min-h-screen">
      <Navbar />

      <main className="max-w-container mx-auto px-4 sm:px-6 pt-28 pb-20">
        {/* Navigation Breadcrumb */}
        <div className="flex items-center gap-2 text-xs font-mono text-text-tertiary mb-6">
          <Link
            href="/dashboard"
            className="text-text-secondary hover:text-accent-primary transition-colors flex items-center gap-1"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </Link>
          <span>/</span>
          <span className="text-text-primary font-medium">{report.object_name}</span>
          <span>(NORAD {report.norad_cat_id})</span>
        </div>

        <div className="space-y-6">
          {/* Main Hero Header Card */}
          <div className="pharos-card p-6 sm:p-8 border border-border-subtle bg-bg-surface/90 relative overflow-hidden">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              {/* Left Column: Name, NORAD, Status */}
              <div className="space-y-3">
                <div className="flex items-center gap-2.5 flex-wrap">
                  <h1 className="font-display font-bold text-2xl sm:text-3xl text-text-primary tracking-tight">
                    {report.object_name}
                  </h1>
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-bg-elevated text-accent-cyan border border-accent-cyan/20">
                    {report.orbit_type} ORBIT
                  </span>
                  <StatusBadge status={report.compliance_level} size="md" />
                </div>

                <div className="flex items-center gap-4 text-xs font-mono text-text-tertiary flex-wrap">
                  <span>NORAD Catalog ID: <strong className="text-text-secondary">{report.norad_cat_id}</strong></span>
                  <span>·</span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3 text-text-tertiary" />
                    <span>Epoch: {report.epoch ? new Date(report.epoch).toUTCString() : 'N/A'}</span>
                  </span>
                </div>
              </div>

              {/* Right Column: Score Gauge & Rule Counters */}
              <div className="flex items-center gap-6 bg-bg-elevated/50 p-4 rounded-2xl border border-border-subtle shrink-0">
                <ComplianceGauge score={report.compliance_score} size={88} strokeWidth={8} />
                <div className="space-y-1.5">
                  <div className="text-[11px] font-mono text-text-tertiary uppercase tracking-wider">
                    Statutory Score
                  </div>
                  <div className="flex items-center gap-3 text-xs font-mono">
                    <span className="text-status-pass font-semibold">✓ {report.rules_passed} Pass</span>
                    <span className="text-status-flag font-semibold">⚠ {report.rules_flagged} Flag</span>
                    <span className="text-status-fail font-semibold">✗ {report.rules_failed} Fail</span>
                  </div>
                  <div className="text-[10px] text-text-tertiary font-mono">
                    {report.rules_passed + report.rules_flagged + report.rules_failed} Total Rules Evaluated
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Two-Column Grid: Orbital Ephemeris & Regulatory Summary */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Orbital Parameters Card */}
            <div className="pharos-card p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border-subtle">
                  <Orbit className="w-4 h-4 text-accent-cyan" />
                  <h2 className="font-mono text-xs font-bold uppercase tracking-wider text-text-secondary">
                    Orbital Ephemeris &amp; Decay Parameters
                  </h2>
                </div>

                <div className="grid grid-cols-2 gap-x-4 gap-y-3.5">
                  {[
                    { label: 'Mean Altitude', value: `${Math.round(report.mean_altitude_km)} km` },
                    { label: 'Perigee Altitude', value: `${Math.round(report.perigee_km)} km` },
                    { label: 'Apogee Altitude', value: `${Math.round(report.apogee_km)} km` },
                    { label: 'Inclination', value: `${report.inclination_deg.toFixed(2)}°` },
                    { label: 'Eccentricity', value: report.eccentricity.toFixed(6) },
                    { label: 'Mean Motion', value: `${report.mean_motion_rev_per_day.toFixed(4)} rev/day` },
                    {
                      label: 'Orbital Lifetime',
                      value: report.estimated_orbital_lifetime_years >= 999
                        ? '> 999 years'
                        : `${report.estimated_orbital_lifetime_years.toFixed(1)} years`,
                    },
                    { label: 'Disposal Limit', value: '5.0 years (FCC)' },
                  ].map(({ label, value }) => (
                    <div key={label} className="p-2.5 rounded-lg bg-bg-elevated/40 border border-border-subtle">
                      <div className="text-[10px] font-mono text-text-tertiary uppercase tracking-wider mb-0.5">
                        {label}
                      </div>
                      <div className="text-xs font-mono font-semibold text-text-primary">
                        {value}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-border-subtle text-[11px] font-mono text-text-tertiary">
                Atmospheric density modeled via King-Hele decay equations.
              </div>
            </div>

            {/* Compliance Summary & Export Card */}
            <div className="pharos-card p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4 pb-3 border-b border-border-subtle">
                  <div className="flex items-center gap-2">
                    <Globe2 className="w-4 h-4 text-accent-primary" />
                    <h2 className="font-mono text-xs font-bold uppercase tracking-wider text-text-secondary">
                      Regulatory Scope &amp; Exports
                    </h2>
                  </div>
                  {/* Export Buttons */}
                  <div className="flex items-center gap-2">
                    <a
                      href={jsonUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-mono bg-bg-elevated hover:bg-bg-elevated/80 border border-border-subtle text-text-secondary hover:text-text-primary transition-colors"
                      title="Export JSON"
                    >
                      <FileCode className="w-3.5 h-3.5 text-accent-primary" />
                      <span>JSON</span>
                    </a>
                    <a
                      href={pdfUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-mono bg-bg-elevated hover:bg-bg-elevated/80 border border-border-subtle text-text-secondary hover:text-text-primary transition-colors"
                      title="Export PDF"
                    >
                      <FileText className="w-3.5 h-3.5 text-accent-cyan" />
                      <span>PDF</span>
                    </a>
                  </div>
                </div>

                <div className="space-y-3 text-xs">
                  <div>
                    <div className="text-[10px] font-mono text-text-tertiary uppercase tracking-wider mb-1.5">
                      Jurisdictions Checked
                    </div>
                    <div className="flex items-center gap-1.5 flex-wrap">
                      {report.standards_checked.map((std) => (
                        <span
                          key={std}
                          className="px-2 py-0.5 rounded text-[11px] font-mono bg-bg-elevated text-text-primary border border-border-subtle"
                        >
                          {std}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="text-[10px] font-mono text-text-tertiary uppercase tracking-wider mb-1">
                      Data Pipeline Sources
                    </div>
                    <div className="space-y-1">
                      {report.data_sources.map((ds) => (
                        <div key={ds} className="text-[11px] font-mono text-text-secondary">
                          → {ds}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="pt-2 border-t border-border-subtle">
                    <div className="text-[10px] font-mono text-text-tertiary uppercase tracking-wider mb-1">
                      AI Inference Pipeline
                    </div>
                    <div className="text-[11px] font-mono text-status-pass flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-status-pass" />
                      <span>{report.ai_available ? 'IBM Granite 3.1 8B Instruct via watsonx.ai' : 'Deterministic engine active (fallback)'}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-border-subtle flex items-center justify-between text-[11px] font-mono text-text-tertiary">
                <span>Deterministic Verdict</span>
                <span className="text-accent-primary font-semibold">100% Rule Audit Complete</span>
              </div>
            </div>
          </div>

          {/* Rule Results Table Card */}
          <div className="pharos-card p-6 border border-border-subtle">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="font-sans font-bold text-base text-text-primary">
                  Rule Evaluation Results
                </h2>
                <p className="text-xs text-text-secondary mt-0.5">
                  Click on any row to expand the verified clause citation and reasoning.
                </p>
              </div>
              <span className="text-xs font-mono text-text-tertiary hidden sm:inline-block">
                {report.rule_results.length} Active Rules
              </span>
            </div>
            <RuleResultsTable rules={report.rule_results} />
          </div>

          {/* AI Compliance Assessment Card */}
          {report.ai_report_text && (
            <div className="pharos-card p-6 sm:p-7 border border-accent-primary/20 bg-bg-surface/95 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1.5 h-full bg-accent-primary" />
              
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-border-subtle">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-accent-primary" />
                  <h3 className="font-sans font-bold text-base text-text-primary">
                    AI Compliance Assessment
                  </h3>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-accent-primary/10 text-accent-primary border border-accent-primary/20 font-semibold">
                    IBM GRANITE
                  </span>
                </div>

                {report.ai_report_safe === true && (
                  <div className="inline-flex items-center gap-1.5 text-xs font-mono text-status-pass bg-status-pass/10 px-2.5 py-1 rounded-full border border-status-pass/20">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Screened by Granite Guardian</span>
                  </div>
                )}
              </div>

              <div className="text-xs sm:text-sm text-text-secondary leading-relaxed space-y-3 font-sans whitespace-pre-wrap">
                {report.ai_report_text}
              </div>

              <div className="mt-4 pt-3 border-t border-border-subtle text-[11px] font-mono text-text-tertiary">
                Disclaimer: AI assessment provides interpretive synthesis over deterministic orbital calculations.
              </div>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  )
}
