'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useTheme } from '@/components/theme/ThemeProvider'
import { Sun, Moon, Menu, X, ArrowRight } from 'lucide-react'

const NAV_LINKS = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/standards', label: 'Standards' },
  { href: '/judges', label: 'Judges' },
]

function GitHubIcon({ className = 'w-4 h-4' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
      />
    </svg>
  )
}

export default function Navbar() {
  const pathname = usePathname()
  const [menuOpen, setMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const { theme, toggleTheme } = useTheme()

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Close mobile menu on route change
  useEffect(() => {
    setMenuOpen(false)
  }, [pathname])

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-200 ${
        scrolled
          ? 'bg-bg-base/85 backdrop-blur-xl border-b border-border-hover py-2.5'
          : 'bg-bg-base/70 backdrop-blur-lg border-b border-border-subtle py-3'
      }`}
    >
      <nav className="max-w-container mx-auto px-4 sm:px-6 flex items-center justify-between">
        {/* Brand / Logo */}
        <Link
          href="/"
          className="flex items-center gap-2.5 text-decoration-none group"
          aria-label="PHAROS Home"
        >
          <div className="w-7 h-7 rounded-lg bg-accent-primary/10 border border-accent-primary/30 flex items-center justify-center text-accent-primary transition-transform group-hover:scale-105">
            <span className="text-sm font-bold">◈</span>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="font-display font-bold text-lg tracking-tight text-text-primary">
              PHAROS
            </span>
            <span className="text-[10px] font-mono text-accent-cyan tracking-wider font-semibold uppercase px-1.5 py-0.5 rounded bg-accent-cyan/10 border border-accent-cyan/20 hidden sm:inline-block">
              LEO INTEL
            </span>
          </div>
        </Link>

        {/* Desktop Nav Links */}
        <div className="hidden md:flex items-center gap-1.5 bg-bg-surface/90 border border-border-subtle p-1 rounded-full backdrop-blur-md">
          {NAV_LINKS.map(({ href, label }) => {
            const active = pathname === href || (href !== '/' && pathname.startsWith(href))
            return (
              <Link
                key={href}
                href={href}
                className={`relative px-4 py-1.5 rounded-full text-xs font-medium tracking-wide transition-all duration-200 ${
                  active
                    ? 'text-accent-primary bg-bg-elevated border border-accent-primary/20'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-elevated/50'
                }`}
              >
                {label}
              </Link>
            )
          })}

          {/* GitHub link directly after Judges */}
          <a
            href="https://github.com/0xkinno/pharos"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium tracking-wide text-text-secondary hover:text-text-primary hover:bg-bg-elevated/50 transition-all duration-200 border border-transparent hover:border-border-subtle"
            title="View PHAROS on GitHub"
          >
            <GitHubIcon className="w-3.5 h-3.5" />
            <span>GitHub</span>
          </a>
        </div>

        {/* Action controls (Theme switch + CTA) */}
        <div className="hidden md:flex items-center gap-3">
          {/* Theme Toggle */}
          <button
            type="button"
            onClick={toggleTheme}
            className="w-8 h-8 rounded-full flex items-center justify-center text-text-secondary hover:text-text-primary hover:bg-bg-surface border border-border-subtle hover:border-border-hover transition-colors"
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-accent-primary" />
            )}
          </button>

          {/* Primary CTA */}
          <Link
            href="/dashboard"
            className="btn-primary text-xs py-2 px-4 rounded-full font-semibold shadow-none hover:shadow-glow-primary transition-all duration-200"
          >
            <span>Check Compliance</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Mobile controls */}
        <div className="flex md:hidden items-center gap-2">
          <button
            type="button"
            onClick={toggleTheme}
            className="w-8 h-8 rounded-full flex items-center justify-center text-text-secondary border border-border-subtle"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-accent-primary" />}
          </button>
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-text-primary border border-border-subtle hover:bg-bg-surface"
            aria-label="Toggle menu"
          >
            {menuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>
        </div>
      </nav>

      {/* Mobile Slide-in Drawer */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden border-b border-border-subtle bg-bg-surface/98 backdrop-blur-xl px-6 py-5 overflow-hidden"
          >
            <div className="flex flex-col gap-3">
              {NAV_LINKS.map(({ href, label }) => {
                const active = pathname === href || (href !== '/' && pathname.startsWith(href))
                return (
                  <Link
                    key={href}
                    href={href}
                    onClick={() => setMenuOpen(false)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium ${
                      active
                        ? 'bg-accent-primary/10 text-accent-primary font-semibold'
                        : 'text-text-secondary hover:text-text-primary'
                    }`}
                  >
                    {label}
                  </Link>
                )
              })}

              <a
                href="https://github.com/0xkinno/pharos"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-text-secondary hover:text-text-primary"
              >
                <GitHubIcon className="w-4 h-4" />
                <span>GitHub Repository ↗</span>
              </a>

              <div className="pt-3 border-t border-border-subtle mt-1">
                <Link
                  href="/dashboard"
                  onClick={() => setMenuOpen(false)}
                  className="btn-primary w-full text-center text-sm py-2.5 rounded-lg justify-center"
                >
                  Check Compliance →
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
