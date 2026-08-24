'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import StarField from '@/components/globe/StarField'
import Footer from '@/components/layout/Footer'
import Navbar from '@/components/layout/Navbar'
import { NumberCounter } from '@/components/ui'
import { ArrowRight, ShieldCheck, Cpu, Database, FileText, CheckCircle2, ChevronRight } from 'lucide-react'

const HOW_IT_WORKS = [
  {
    step: '01',
    title: 'Search Any Satellite',
    desc: "Enter a satellite name or NORAD catalog ID. Real-time orbital data is fetched instantly from CelesTrak's public GP API.",
  },
  {
    step: '02',
    title: 'SGP4 Propagation',
    desc: 'The python-sgp4 library propagates the orbital elements to compute exact instantaneous position and velocity vectors.',
  },
  {
    step: '03',
    title: 'Lifetime Estimation',
    desc: 'A King-Hele atmospheric decay model estimates how long the satellite will remain in orbit before natural atmospheric reentry.',
  },
  {
    step: '04',
    title: 'Deterministic Rules',
    desc: '20 coded rules from 5 regulatory bodies (FCC, IADC, ISO, ESA, COPUOS) are evaluated deterministically. AI never guesses compliance.',
  },
  {
    step: '05',
    title: 'Granite Citations',
    desc: 'Every flag retrieves the exact governing standard clause using IBM Granite Embedding RAG over the verified regulatory corpus.',
  },
  {
    step: '06',
    title: 'AI Report & Guardrails',
    desc: 'IBM Granite 3.1 8B Instruct generates plain-language executive compliance reports, screened by Granite Guardian for safety.',
  },
]

const IBM_TOOLS = [
  {
    tool: 'IBM Bob',
    role: 'Primary autonomous development agent — authored the core engine, mathematical models, verification test suite, and frontend.',
    tag: 'Dev Agent',
  },
  {
    tool: 'Granite 3.1 8B Instruct',
    role: 'Plain-language regulatory compliance assessment and multi-jurisdiction risk analysis synthesis.',
    tag: 'watsonx.ai',
  },
  {
    tool: 'Granite Embedding',
    role: 'Dense vector retrieval (RAG) mapping compliance flags to exact standard clauses in FCC, IADC, ISO, and ESA documents.',
    tag: 'RAG Pipeline',
  },
  {
    tool: 'Granite Guardian',
    role: 'Safety & hallucination guardrail screening all AI-generated compliance assessments prior to serving.',
    tag: 'Safety Guard',
  },
  {
    tool: 'Docling',
    role: 'High-fidelity parsing of complex regulatory PDF standards into structured, chunked, indexable knowledge bases.',
    tag: 'Doc Parser',
  },
]

export default function LandingPage() {
  return (
    <div className="bg-bg-base text-text-primary min-h-screen relative selection:bg-accent-primary/30">
      <StarField starCount={140} />
      <Navbar />

      <main className="relative z-10">
        {/* ── HERO SECTION ── */}
        <section
          className="min-h-screen flex flex-col items-center justify-center text-center px-4 sm:px-6 pt-24 pb-16 relative overflow-hidden"
          style={{
            backgroundImage: `linear-gradient(
              to bottom,
              rgba(13, 13, 20, 0.72) 0%,
              rgba(13, 13, 20, 0.88) 55%,
              rgba(13, 13, 20, 1) 100%
            ), url('/images/hero-bg.png')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          {/* Subtle Ambient Radial Glow */}
          <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-accent-primary/10 rounded-full blur-[120px] pointer-events-none" />

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="max-w-4xl mx-auto flex flex-col items-center"
          >
            {/* Top Pill Badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-border-hover bg-bg-surface/80 backdrop-blur-md mb-8 text-xs text-text-secondary">
              <span className="w-2 h-2 rounded-full bg-accent-cyan animate-pulse" />
              <span>IBM AI Builders Challenge · August 2026</span>
              <span className="text-text-tertiary">|</span>
              <span className="text-accent-primary font-medium">Advance Space Exploration with AI</span>
            </div>

            {/* Massive Display Title */}
            <h1 className="font-display font-extrabold text-6xl sm:text-7xl md:text-8xl lg:text-9xl tracking-tight leading-[0.9] text-text-primary mb-4 select-none">
              PHAROS
            </h1>

            {/* Tracked Subtitle */}
            <div className="font-sans text-xs sm:text-sm font-semibold label-tracked text-text-secondary mb-8 text-accent-cyan">
              SATELLITE COMPLIANCE INTELLIGENCE
            </div>

            {/* Editorial One-Liner */}
            <p className="max-w-2xl text-base sm:text-lg md:text-xl text-text-secondary leading-relaxed font-normal mb-12">
              Check any satellite against every deorbit and debris-mitigation standard
              that governs low Earth orbit,{' '}
              <span className="text-text-primary font-medium">
                before regulators find violations.
              </span>
            </p>

            {/* Three Stat Counters */}
            <div className="grid grid-cols-3 gap-6 sm:gap-12 py-6 px-8 rounded-2xl glass-panel mb-10 w-full max-w-2xl">
              <div className="text-center">
                <div className="text-2xl sm:text-4xl font-bold font-mono text-accent-primary">
                  <NumberCounter value="5" />
                </div>
                <div className="text-[11px] sm:text-xs text-text-tertiary uppercase tracking-wider mt-1 font-mono">
                  Regulatory Bodies
                </div>
              </div>
              <div className="text-center border-x border-border-subtle">
                <div className="text-2xl sm:text-4xl font-bold font-mono text-accent-cyan">
                  <NumberCounter value="16" suffix="+" />
                </div>
                <div className="text-[11px] sm:text-xs text-text-tertiary uppercase tracking-wider mt-1 font-mono">
                  Coded Rules
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl sm:text-4xl font-bold font-mono text-text-primary">
                  <NumberCounter value="16,000" suffix="+" />
                </div>
                <div className="text-[11px] sm:text-xs text-text-tertiary uppercase tracking-wider mt-1 font-mono">
                  LEO Satellites
                </div>
              </div>
            </div>

            {/* Hero CTAs */}
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link
                href="/dashboard"
                className="btn-primary text-sm py-3 px-7 rounded-xl font-semibold hover:scale-[1.02] active:scale-[0.98] transition-all duration-200"
              >
                <span>Check Compliance</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/judges"
                className="btn-secondary text-sm py-3 px-7 rounded-xl font-medium hover:border-accent-primary hover:text-text-primary transition-all duration-200"
              >
                For Judges
              </Link>
            </div>
          </motion.div>
        </section>

        {/* ── PROBLEM / CONTEXT SECTION ── */}
        <section className="max-w-container mx-auto px-4 sm:px-6 py-20">
          <div className="max-w-4xl mx-auto space-y-12">
            {/* Editorial Quote Card */}
            <div className="pharos-card p-8 sm:p-10 border border-border-subtle bg-bg-surface/90 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-status-fail" />
              <p className="text-base sm:text-lg text-text-secondary leading-relaxed italic mb-6">
                &ldquo;On February 10, 2009, Iridium 33 and Cosmos 2251 collided at 11.7 km/s,
                generating over 2,000 trackable debris fragments. In September 2022, the FCC cut
                the post-mission orbital lifetime limit from 25 years to{' '}
                <strong className="text-status-fail not-italic font-semibold">5 years</strong>.
                As of 2026, over 16,000 satellites share low Earth orbit.
                <strong className="text-text-primary not-italic font-semibold">
                  {' '}No open-source tool checks whether any of them comply. PHAROS does.
                </strong>&rdquo;
              </p>
              <div className="flex items-center gap-2 text-xs font-mono text-text-tertiary">
                <span className="w-1.5 h-1.5 rounded-full bg-status-flag" />
                <span>FCC 47 CFR §25.114 · IADC-02-01 · ISO 24113:2019</span>
              </div>
            </div>

            {/* 4 Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                {
                  stat: '$150K+',
                  label: 'FCC Daily Fines',
                  desc: 'Per violation per day under 47 CFR Part 25 enforcement rules.',
                  color: 'text-status-fail',
                },
                {
                  stat: '5 Years',
                  label: 'FCC Deorbit Rule',
                  desc: 'Mandatory post-mission disposal threshold in effect since 2024.',
                  color: 'text-status-flag',
                },
                {
                  stat: '30,000+',
                  label: 'Tracked Debris',
                  desc: 'Objects >10cm currently cataloged and monitored in low Earth orbit.',
                  color: 'text-accent-cyan',
                },
                {
                  stat: 'Free / OSS',
                  label: 'Zero Vendor Lock',
                  desc: 'Open-source compliance intelligence. No API key required for rules.',
                  color: 'text-status-pass',
                },
              ].map(({ stat, label, desc, color }) => (
                <div
                  key={label}
                  className="pharos-card pharos-card-hoverable p-6 flex flex-col justify-between"
                >
                  <div>
                    <div className={`text-3xl font-bold font-mono ${color} mb-2`}>
                      {stat}
                    </div>
                    <div className="text-xs font-mono font-semibold text-text-primary uppercase tracking-wider mb-2">
                      {label}
                    </div>
                  </div>
                  <p className="text-xs text-text-secondary leading-relaxed">
                    {desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── HOW IT WORKS SECTION ── */}
        <section className="max-w-container mx-auto px-4 sm:px-6 py-20">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-primary/10 border border-accent-primary/20 text-accent-primary text-xs font-mono uppercase tracking-wider mb-3">
              System Architecture
            </div>
            <h2 className="font-display text-3xl sm:text-4xl font-bold tracking-tight text-text-primary mb-3">
              How PHAROS Operates
            </h2>
            <p className="text-sm text-text-secondary">
              Deterministic engines detect. IBM Granite explains. AI never determines compliance verdicts.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {HOW_IT_WORKS.map(({ step, title, desc }, index) => (
              <motion.div
                key={step}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.06 }}
                className="pharos-card pharos-card-hoverable p-6 flex flex-col justify-between border border-border-subtle relative group"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="font-mono text-xs font-bold text-accent-primary px-2 py-0.5 rounded bg-accent-primary/10 border border-accent-primary/20">
                      STEP {step}
                    </span>
                    <span className="text-text-tertiary text-xs font-mono group-hover:text-accent-cyan transition-colors">
                      0{index + 1} / 06
                    </span>
                  </div>
                  <h3 className="font-sans text-base font-semibold text-text-primary mb-2">
                    {title}
                  </h3>
                  <p className="text-xs text-text-secondary leading-relaxed">
                    {desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </section>

        {/* ── IBM STACK SECTION ── */}
        <section className="max-w-container mx-auto px-4 sm:px-6 py-20">
          <div className="max-w-4xl mx-auto">
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-cyan/10 border border-accent-cyan/20 text-accent-cyan text-xs font-mono uppercase tracking-wider mb-3">
                  IBM Watson &amp; Granite Integration
                </div>
                <h2 className="font-display text-3xl font-bold tracking-tight text-text-primary">
                  Enterprise AI Stack
                </h2>
              </div>
              <Link
                href="/judges"
                className="text-xs font-mono text-accent-primary hover:underline inline-flex items-center gap-1"
              >
                <span>Full integration evidence</span>
                <ChevronRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="pharos-card divide-y divide-border-subtle overflow-hidden">
              {IBM_TOOLS.map(({ tool, role, tag }) => (
                <div
                  key={tool}
                  className="p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-bg-elevated/40 transition-colors"
                >
                  <div className="flex items-start gap-3.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-accent-primary mt-1.5 shrink-0" />
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-sans font-bold text-sm text-text-primary">
                          {tool}
                        </span>
                        <span className="text-[10px] font-mono text-accent-primary bg-accent-primary/10 px-2 py-0.5 rounded border border-accent-primary/20">
                          {tag}
                        </span>
                      </div>
                      <p className="text-xs text-text-secondary leading-relaxed">
                        {role}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 text-center">
              <Link
                href="/judges"
                className="text-xs text-text-tertiary hover:text-accent-primary transition-colors font-mono"
              >
                Every tool is load-bearing. Delete the API — the deterministic engine still runs 100% →
              </Link>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
