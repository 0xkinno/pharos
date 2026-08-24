'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'

const NAV_LINKS = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/standards', label: 'Standards' },
  { href: '/judges', label: 'Judges' },
]

export default function Navbar() {
  const pathname = usePathname()
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        backgroundColor: 'rgba(10, 10, 15, 0.85)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid var(--border)',
      }}
    >
      <nav
        style={{
          maxWidth: 1280,
          margin: '0 auto',
          padding: '0 24px',
          height: 56,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        {/* Logo */}
        <Link
          href="/"
          style={{
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <span
            style={{
              fontSize: 18,
              fontWeight: 700,
              color: 'var(--accent-blue)',
              letterSpacing: '0.1em',
            }}
          >
            ◈ PHAROS
          </span>
        </Link>

        {/* Desktop nav */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 4,
          }}
          className="hidden md:flex"
        >
          {NAV_LINKS.map(({ href, label }) => {
            const active = pathname.startsWith(href)
            return (
              <Link
                key={href}
                href={href}
                style={{
                  padding: '6px 14px',
                  borderRadius: 6,
                  fontSize: 14,
                  fontWeight: 500,
                  textDecoration: 'none',
                  color: active ? 'var(--accent-blue)' : 'var(--text-secondary)',
                  backgroundColor: active ? 'rgba(59, 130, 246, 0.08)' : 'transparent',
                  transition: 'all 150ms ease',
                }}
              >
                {label}
              </Link>
            )
          })}

          <Link
            href="/dashboard"
            style={{
              marginLeft: 12,
              padding: '7px 16px',
              borderRadius: 6,
              fontSize: 13,
              fontWeight: 600,
              textDecoration: 'none',
              color: '#fff',
              backgroundColor: 'var(--accent-blue)',
              transition: 'opacity 150ms ease',
            }}
          >
            Check Compliance →
          </Link>
        </div>

        {/* Mobile menu button */}
        <button
          className="md:hidden"
          onClick={() => setMenuOpen(!menuOpen)}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: 'var(--text-primary)',
            fontSize: 20,
            padding: 4,
          }}
          aria-label="Toggle menu"
        >
          {menuOpen ? '✕' : '☰'}
        </button>
      </nav>

      {/* Mobile menu */}
      {menuOpen && (
        <div
          style={{
            backgroundColor: 'var(--bg-secondary)',
            borderTop: '1px solid var(--border)',
            padding: 16,
          }}
          className="md:hidden"
        >
          {NAV_LINKS.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              onClick={() => setMenuOpen(false)}
              style={{
                display: 'block',
                padding: '10px 0',
                fontSize: 15,
                textDecoration: 'none',
                color: 'var(--text-primary)',
                borderBottom: '1px solid var(--border)',
              }}
            >
              {label}
            </Link>
          ))}
        </div>
      )}
    </header>
  )
}
