'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import RuleResultsTable from '@/components/dashboard/RuleResultsTable'
import { ComplianceGauge, StatusBadge, DataValue, SkeletonCard } from '@/components/ui'
import { api, ApiError } from '@/lib/api'
import type { ComplianceReport } from '@/lib/types'

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
      <div style={{ backgroundColor: 'var(--bg-primary)', minHeight: '100vh' }}>
        <Navbar />
        <main style={{ maxWidth: 1100, margin: '0 auto', padding: '40px 24px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <SkeletonCard height={140} />
            <SkeletonCard height={200} />
            <SkeletonCard height={400} />
          </div>
        </main>
      </div>
    )
  }

  if (error || !report) {
    return (
      <div style={{ backgroundColor: 'var(--bg-primary)', minHeight: '100vh' }}>
        <Navbar />
        <main style={{ maxWidth: 1100, margin: '0 auto', padding: '40px 24px' }}>
          <div
            style={{
              padding: 32,
              backgroundColor: 'var(--status-fail-bg)',
              border: '1px solid rgba(239,68,68,0.2)',
              borderRadius: 8,
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: 18, color: 'var(--status-fail)', marginBottom: 8 }}>
              {error || 'Satellite not found'}
            </div>
            <Link href="/dashboard" style={{ color: 'var(--accent-blue)', fontSize: 13 }}>
              ← Back to Dashboard
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
    <div style={{ backgroundColor: 'var(--bg-primary)', minHeight: '100vh' }}>
      <Navbar />

      <main style={{ maxWidth: 1100, margin: '0 auto', padding: '40px 24px' }}>
        {/* Breadcrumb */}
        <div style={{ marginBottom: 20, fontSize: 13, color: 'var(--text-tertiary)' }}>
          <Link href="/dashboard" style={{ color: 'var(--accent-blue)', textDecoration: 'none' }}>
            Dashboard
          </Link>
          {' / '}
          <span>{report.object_name}</span>
        </div>

        {/* Header */}
        <div
          className="pharos-card"
          style={{
            padding: '24px 28px',
            marginBottom: 20,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            flexWrap: 'wrap',
            gap: 20,
          }}
        >
          <div>
            <div
              style={{
                fontSize: 24,
                fontWeight: 700,
                color: 'var(--text-primary)',
                marginBottom: 6,
                lineHeight: 1.2,
              }}
            >
              {report.object_name}
            </div>
            <div
              style={{
                fontSize: 12,
                fontFamily: 'monospace',
                color: 'var(--text-tertiary)',
                marginBottom: 10,
              }}
            >
              NORAD {report.norad_cat_id} · Epoch: {report.epoch ? new Date(report.epoch).toUTCString() : 'Unknown'}
            </div>
            <StatusBadge status={report.compliance_level} />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <ComplianceGauge score={report.compliance_score} size={90} />
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>Rules</div>
              <div style={{ display: 'flex', gap: 12, fontSize: 13, fontFamily: 'monospace' }}>
                <span style={{ color: 'var(--status-pass)' }}>✓ {report.rules_passed}</span>
                <span style={{ color: 'var(--status-flag)' }}>⚠ {report.rules_flagged}</span>
                <span style={{ color: 'var(--status-fail)' }}>✗ {report.rules_failed}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Two-column layout */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 20,
            marginBottom: 20,
          }}
        >
          {/* Orbital parameters */}
          <div className="pharos-card" style={{ padding: '20px 22px' }}>
            <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 16, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary)' }}>
              Orbital Parameters
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                { label: 'Orbit Type', value: report.orbit_type },
                { label: 'Mean Altitude', value: `${Math.round(report.mean_altitude_km)} km` },
                { label: 'Perigee', value: `${Math.round(report.perigee_km)} km` },
                { label: 'Apogee', value: `${Math.round(report.apogee_km)} km` },
                { label: 'Inclination', value: `${report.inclination_deg.toFixed(2)}°` },
                { label: 'Eccentricity', value: report.eccentricity.toFixed(6) },
                { label: 'Mean Motion', value: `${report.mean_motion_rev_per_day.toFixed(4)} rev/day` },
                {
                  label: 'Est. Lifetime',
                  value: report.estimated_orbital_lifetime_years >= 999
                    ? '> 999 years'
                    : `${report.estimated_orbital_lifetime_years.toFixed(1)} years`,
                },
              ].map(({ label, value }) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>{label}</span>
                  <span style={{ fontSize: 12, fontFamily: 'monospace', color: 'var(--text-primary)' }}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Compliance stats */}
          <div className="pharos-card" style={{ padding: '20px 22px' }}>
            <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 16, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary)' }}>
              Compliance Summary
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>Standards Checked</span>
                <span style={{ fontSize: 12, fontFamily: 'monospace', color: 'var(--text-primary)' }}>
                  {report.standards_checked.length}
                </span>
              </div>
              {report.data_sources.map((ds) => (
                <div key={ds} style={{ fontSize: 11, color: 'var(--text-tertiary)', fontFamily: 'monospace' }}>
                  → {ds}
                </div>
              ))}
              <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid var(--border)' }}>
                <div style={{ fontSize: 11, color: 'var(--text-tertiary)', marginBottom: 4 }}>
                  AI Report
                </div>
                <div style={{ fontSize: 11, fontFamily: 'monospace', color: report.ai_available ? 'var(--status-pass)' : 'var(--text-tertiary)' }}>
                  {report.ai_available ? '✓ Granite Instruct (watsonx.ai)' : '→ Structured fallback (no API key)'}
                </div>
              </div>
            </div>

            {/* Export buttons */}
            <div style={{ display: 'flex', gap: 8, marginTop: 20 }}>
              <a
                href={jsonUrl}
                target="_blank"
                rel="noopener"
                style={{
                  flex: 1,
                  padding: '8px',
                  textAlign: 'center',
                  border: '1px solid var(--border)',
                  borderRadius: 6,
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  textDecoration: 'none',
                  transition: 'border-color 150ms',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--accent-blue)' }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)' }}
              >
                ↓ JSON
              </a>
              <a
                href={pdfUrl}
                target="_blank"
                rel="noopener"
                style={{
                  flex: 1,
                  padding: '8px',
                  textAlign: 'center',
                  border: '1px solid var(--border)',
                  borderRadius: 6,
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  textDecoration: 'none',
                  transition: 'border-color 150ms',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--accent-cyan)' }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)' }}
              >
                ↓ PDF
              </a>
            </div>
          </div>
        </div>

        {/* Rule Results Table */}
        <div className="pharos-card" style={{ padding: '20px 22px', marginBottom: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>
            Rule Evaluation Results
            <span style={{ fontSize: 11, color: 'var(--text-tertiary)', marginLeft: 8, fontWeight: 400 }}>
              Click any row to expand and see the standard clause
            </span>
          </h3>
          <RuleResultsTable rules={report.rule_results} />
        </div>

        {/* AI Report */}
        {report.ai_report_text && (
          <div className="pharos-card" style={{ padding: '20px 22px' }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 6 }}>
              AI Compliance Assessment
            </h3>
            <div style={{ fontSize: 11, color: 'var(--text-tertiary)', marginBottom: 14, fontFamily: 'monospace' }}>
              Generated by {report.ai_available ? 'IBM Granite 3.1 8B Instruct via watsonx.ai' : 'structured fallback (no API)'}
              {report.ai_report_safe === true && ' · Screened by Granite Guardian ✓'}
            </div>
            <div
              style={{
                fontSize: 13,
                color: 'var(--text-secondary)',
                lineHeight: 1.7,
                whiteSpace: 'pre-wrap',
              }}
            >
              {report.ai_report_text}
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}
