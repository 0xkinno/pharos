'use client'

import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="border-t border-border-subtle mt-24 bg-bg-base/80 backdrop-blur-md">
      <div className="max-w-container mx-auto px-4 sm:px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          {/* Brand Col */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-md bg-accent-primary/10 border border-accent-primary/30 flex items-center justify-center text-accent-primary font-bold text-xs">
                ◈
              </div>
              <span className="font-display font-bold text-base tracking-tight text-text-primary">
                PHAROS
              </span>
              <span className="text-[10px] font-mono text-status-pass tracking-wider px-2 py-0.5 rounded-full bg-status-pass/10 border border-status-pass/20">
                SYSTEM ONLINE
              </span>
            </div>
            <p className="text-xs text-text-secondary max-w-md leading-relaxed">
              Real-time satellite compliance intelligence for the orbital debris era.
              Deterministic rule evaluation, King-Hele decay dynamics, and IBM Granite RAG citation retrieval.
            </p>
            <div className="text-[11px] font-mono text-text-tertiary pt-1">
              Built for the IBM AI Builders Challenge · August 2026
            </div>
          </div>

          {/* Product Links */}
          <div className="space-y-3">
            <div className="text-xs font-mono font-semibold tracking-label uppercase text-text-tertiary">
              Platform
            </div>
            <ul className="space-y-2 text-xs">
              <li>
                <Link
                  href="/dashboard"
                  className="text-text-secondary hover:text-text-primary transition-colors"
                >
                  Compliance Dashboard
                </Link>
              </li>
              <li>
                <Link
                  href="/standards"
                  className="text-text-secondary hover:text-text-primary transition-colors"
                >
                  Standards Explorer
                </Link>
              </li>
              <li>
                <Link
                  href="/judges"
                  className="text-text-secondary hover:text-text-primary transition-colors"
                >
                  Judges Disclosure
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/0xkinno/pharos"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-text-secondary hover:text-text-primary transition-colors inline-flex items-center gap-1"
                >
                  GitHub Repository ↗
                </a>
              </li>
            </ul>
          </div>

          {/* Standards Links */}
          <div className="space-y-3">
            <div className="text-xs font-mono font-semibold tracking-label uppercase text-text-tertiary">
              Governing Bodies
            </div>
            <div className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-xs font-mono">
              <span className="text-text-secondary hover:text-accent-primary transition-colors cursor-default">
                FCC 47 CFR §25
              </span>
              <span className="text-text-secondary hover:text-accent-primary transition-colors cursor-default">
                IADC Guidelines
              </span>
              <span className="text-text-secondary hover:text-accent-primary transition-colors cursor-default">
                ISO 24113:2019
              </span>
              <span className="text-text-secondary hover:text-accent-primary transition-colors cursor-default">
                ESA Zero Debris
              </span>
              <span className="text-text-secondary hover:text-accent-primary transition-colors cursor-default col-span-2">
                UN COPUOS LTS Guidelines
              </span>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-6 border-t border-border-subtle flex flex-col sm:flex-row justify-between items-center gap-3 text-xs text-text-tertiary">
          <div>
            © 2026 PHAROS. Released under the MIT License.
          </div>
          <div className="font-mono text-[11px] text-text-tertiary">
            Built with IBM Granite, Docling, and SGP4. Data: CelesTrak.
          </div>
        </div>
      </div>
    </footer>
  )
}
