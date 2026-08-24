'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import StarField from '@/components/globe/StarField'
import Footer from '@/components/layout/Footer'
import Navbar from '@/components/layout/Navbar'

const HOW_IT_WORKS = [
  {
    step: '01',
    title: 'Search Any Satellite',
    desc: 'Enter a satellite name or NORAD catalog ID. Real-time orbital data is fetched from CelesTrak\'s public GP API.',
  },
  {
    step: '02',
    title: 'SGP4 Propagation',
    desc: 'The python-sgp4 library (Vallado et al.) propagates the orbital elements to compute current position and velocity.',
  },
  {
    step: '03',
    title: 'Lifetime Estimation',
    desc: 'A King-Hele atmospheric decay model estimates how long the satellite will remain in orbit before natural reentry.',
  },
  {
    step: '04',
    title: 'Rule Evaluation',
    desc: '20 coded rules from 5 regulatory bodies (FCC, IADC, ISO, ESA, COPUOS) are evaluated deterministically. AI never decides compliance.',
  },
  {
    step: '05',
    title: 'Granite Citations',
    desc: 'Every flag retrieves the exact standard clause by semantic meaning using IBM Granite Embedding RAG over the parsed regulatory corpus.',
  },
  {
    step: '06',
    title: 'AI Report',
    desc: 'IBM Granite 3.1 8B Instruct generates a plain-language compliance assessment. Granite Guardian screens it for safety before serving.',
  },
]

const IBM_TOOLS = [
  { tool: 'IBM Bob', role: 'Primary development tool — authored the engine, tests, frontend' },
  { tool: 'Granite 3.1 8B Instruct', role: 'Plain-language compliance report generation' },
  { tool: 'Granite Embedding', role: 'RAG-based citation retrieval over regulatory corpus' },
  { tool: 'Granite Guardian', role: 'Content safety screening for generated reports' },
  { tool: 'Docling', role: 'Regulatory PDF parsing into indexable corpus' },
]

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handle = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handle)
    return () => window.removeEventListener('scroll', handle)
  }, [])

  return (
    <div style={{ backgroundColor: 'var(--bg-primary)', minHeight: '100vh' }}>
      <StarField starCount={180} />
      <Navbar />

      <main style={{ position: 'relative', zIndex: 1 }}>
        {/* ── HERO ── */}
        <section
          style={{
            minHeight: '92vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            padding: '80px 24px 60px',
          }}
        >
          {/* Tag */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              padding: '5px 14px',
              borderRadius: 100,
              border: '1px solid rgba(59, 130, 246, 0.3)',
              backgroundColor: 'rgba(59, 130, 246, 0.06)',
              marginBottom: 24,
              fontSize: 12,
              color: 'var(--accent-blue)',
              letterSpacing: '0.06em',
            }}
          >
            <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: 'var(--accent-blue)', display: 'inline-block' }} />
            IBM AI Builders Challenge · August 2026 · Advance Space Exploration with AI
          </div>

          {/* Product name */}
          <h1
            style={{
              fontSize: 'clamp(56px, 12vw, 112px)',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              lineHeight: 0.9,
              color: 'var(--text-primary)',
              marginBottom: 8,
            }}
          >
            PHAROS
          </h1>

          <div
            style={{
              fontSize: 'clamp(13px, 2vw, 16px)',
              color: 'var(--text-tertiary)',
              fontFamily: 'IBM Plex Mono, monospace',
              letterSpacing: '0.15em',
              textTransform: 'uppercase',
              marginBottom: 28,
            }}
          >
            Satellite Compliance Intelligence
          </div>

          {/* Tagline */}
          <p
            style={{
              maxWidth: 680,
              fontSize: 'clamp(16px, 3vw, 20px)',
              fontWeight: 300,
              color: 'var(--text-secondary)',
              lineHeight: 1.6,
              marginBottom: 40,
            }}
          >
            Check any satellite against every deorbit and debris-mitigation
            standard that governs low Earth orbit,{' '}
            <em style={{ color: 'var(--text-primary)', fontStyle: 'normal', fontWeight: 400 }}>
              before regulators find violations.
            </em>
          </p>

          {/* Stats */}
          <div
            style={{
              display: 'flex',
              gap: 32,
              marginBottom: 44,
              flexWrap: 'wrap',
              justifyContent: 'center',
            }}
          >
            {[
              { value: '5', label: 'Regulatory Bodies' },
              { value: '20+', label: 'Coded Rules' },
              { value: '12,000+', label: 'LEO Satellites' },
            ].map(({ value, label }) => (
              <div key={label} style={{ textAlign: 'center' }}>
                <div
                  style={{
                    fontSize: 'clamp(28px, 5vw, 40px)',
                    fontWeight: 700,
                    color: 'var(--accent-blue)',
                    fontFamily: 'IBM Plex Mono, monospace',
                    letterSpacing: '-0.02em',
                  }}
                >
                  {value}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-tertiary)', marginTop: 2 }}>
                  {label}
                </div>
              </div>
            ))}
          </div>

          {/* CTAs */}
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', justifyContent: 'center' }}>
            <Link
              href="/dashboard"
              style={{
                padding: '14px 28px',
                backgroundColor: 'var(--accent-blue)',
                color: '#fff',
                borderRadius: 8,
                fontSize: 15,
                fontWeight: 600,
                textDecoration: 'none',
                transition: 'opacity 150ms, box-shadow 150ms',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 0 24px rgba(59, 130, 246, 0.4)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = 'none'
              }}
            >
              Check Compliance →
            </Link>
            <Link
              href="/judges"
              style={{
                padding: '13px 28px',
                backgroundColor: 'transparent',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-bright)',
                borderRadius: 8,
                fontSize: 15,
                fontWeight: 500,
                textDecoration: 'none',
                transition: 'border-color 150ms',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--accent-blue)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-bright)'
              }}
            >
              For Judges
            </Link>
          </div>
        </section>

        {/* ── PROBLEM ── */}
        <section style={{ maxWidth: 900, margin: '0 auto', padding: '80px 24px' }}>
          <div
            style={{
              textAlign: 'center',
              marginBottom: 48,
              padding: '32px 40px',
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--border)',
              borderRadius: 12,
            }}
          >
            <p
              style={{
                fontSize: 'clamp(14px, 2.5vw, 18px)',
                color: 'var(--text-secondary)',
                lineHeight: 1.7,
                fontStyle: 'italic',
              }}
            >
              "On February 10, 2009, Iridium 33 and Cosmos 2251 collided at 11.7 km/s,
              generating over 2,000 trackable debris fragments. Both spacecraft were
              non-compliant with debris mitigation guidelines that existed at the time.
              In September 2022, the FCC cut the acceptable post-mission orbital lifetime
              from 25 years to <strong style={{ color: 'var(--status-fail)', fontStyle: 'normal' }}>5 years</strong>.
              As of August 2026, over 12,000 active satellites share low Earth orbit.
              <strong style={{ color: 'var(--text-primary)', fontStyle: 'normal' }}> No open-source tool checks whether any of them comply. PHAROS does.</strong>"
            </p>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
              gap: 16,
            }}
          >
            {[
              { stat: '$150K+', desc: 'FCC fines per violation per day', color: 'var(--status-fail)' },
              { stat: '5 Years', desc: 'FCC deorbit requirement (since 2024)', color: 'var(--status-flag)' },
              { stat: '30,000+', desc: 'Tracked debris objects in orbit', color: 'var(--status-flag)' },
              { stat: 'Free', desc: 'PHAROS is open-source, no account required', color: 'var(--status-pass)' },
            ].map(({ stat, desc, color }) => (
              <div
                key={stat}
                className="pharos-card"
                style={{ padding: '20px 24px' }}
              >
                <div style={{ fontSize: 28, fontWeight: 700, color, fontFamily: 'monospace', marginBottom: 6 }}>
                  {stat}
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{desc}</div>
              </div>
            ))}
          </div>
        </section>

        {/* ── HOW IT WORKS ── */}
        <section style={{ maxWidth: 1100, margin: '0 auto', padding: '80px 24px' }}>
          <h2
            style={{
              fontSize: 32,
              fontWeight: 700,
              marginBottom: 8,
              color: 'var(--text-primary)',
            }}
          >
            How PHAROS Works
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 40, fontSize: 15 }}>
            The engine detects. IBM Granite explains. Compliance decisions are always deterministic.
          </p>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: 16,
            }}
          >
            {HOW_IT_WORKS.map(({ step, title, desc }) => (
              <div
                key={step}
                className="pharos-card"
                style={{ padding: '20px 22px' }}
              >
                <div
                  style={{
                    fontSize: 11,
                    fontFamily: 'monospace',
                    color: 'var(--accent-blue)',
                    marginBottom: 10,
                    letterSpacing: '0.1em',
                  }}
                >
                  STEP {step}
                </div>
                <div
                  style={{ fontSize: 15, fontWeight: 600, marginBottom: 8, color: 'var(--text-primary)' }}
                >
                  {title}
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {desc}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── IBM STACK ── */}
        <section
          style={{
            maxWidth: 900,
            margin: '0 auto',
            padding: '80px 24px',
          }}
        >
          <h2 style={{ fontSize: 32, fontWeight: 700, marginBottom: 8 }}>
            IBM Technology Stack
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 32, fontSize: 15 }}>
            Every IBM tool is load-bearing. Delete the API — the compliance engine still runs.
          </p>

          <div className="pharos-card" style={{ overflow: 'hidden' }}>
            {IBM_TOOLS.map(({ tool, role }, i) => (
              <div
                key={tool}
                style={{
                  padding: '16px 20px',
                  borderBottom: i < IBM_TOOLS.length - 1 ? '1px solid var(--border)' : 'none',
                  display: 'flex',
                  gap: 16,
                  alignItems: 'flex-start',
                }}
              >
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    backgroundColor: 'var(--accent-blue)',
                    marginTop: 5,
                    flexShrink: 0,
                  }}
                />
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>
                    {tool}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                    {role}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 20, textAlign: 'center' }}>
            <Link
              href="/judges"
              style={{
                fontSize: 13,
                color: 'var(--accent-blue)',
                textDecoration: 'none',
              }}
            >
              Full IBM integration details with evidence and API-deletion behavior →
            </Link>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
