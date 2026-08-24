import Link from 'next/link'

export default function Footer() {
  return (
    <footer
      style={{
        borderTop: '1px solid var(--border)',
        marginTop: 80,
        padding: '32px 24px',
        backgroundColor: 'var(--bg-primary)',
      }}
    >
      <div
        style={{
          maxWidth: 1280,
          margin: '0 auto',
          display: 'flex',
          flexWrap: 'wrap',
          gap: 32,
          justifyContent: 'space-between',
          alignItems: 'flex-start',
        }}
      >
        {/* Brand */}
        <div>
          <div
            style={{
              fontSize: 16,
              fontWeight: 700,
              color: 'var(--accent-blue)',
              letterSpacing: '0.1em',
              marginBottom: 8,
            }}
          >
            ◈ PHAROS
          </div>
          <div
            style={{
              fontSize: 12,
              color: 'var(--text-tertiary)',
              maxWidth: 280,
              lineHeight: 1.6,
            }}
          >
            Satellite compliance intelligence for the orbital debris era.
            Built for the IBM AI Builders Challenge August 2026.
          </div>
        </div>

        {/* Links */}
        <div style={{ display: 'flex', gap: 48 }}>
          <div>
            <div
              style={{
                fontSize: 11,
                fontWeight: 600,
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                color: 'var(--text-tertiary)',
                marginBottom: 10,
              }}
            >
              Product
            </div>
            {[
              { href: '/dashboard', label: 'Dashboard' },
              { href: '/standards', label: 'Standards' },
              { href: '/judges', label: 'Judges' },
            ].map(({ href, label }) => (
              <div key={href} style={{ marginBottom: 6 }}>
                <Link
                  href={href}
                  style={{
                    fontSize: 13,
                    color: 'var(--text-secondary)',
                    textDecoration: 'none',
                    transition: 'color 150ms',
                  }}
                >
                  {label}
                </Link>
              </div>
            ))}
          </div>

          <div>
            <div
              style={{
                fontSize: 11,
                fontWeight: 600,
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                color: 'var(--text-tertiary)',
                marginBottom: 10,
              }}
            >
              Standards
            </div>
            {['FCC', 'IADC', 'ISO 24113', 'ESA Zero Debris', 'COPUOS'].map((s) => (
              <div key={s} style={{ marginBottom: 6 }}>
                <span style={{ fontSize: 12, color: 'var(--text-tertiary)', fontFamily: 'monospace' }}>
                  {s}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div
        style={{
          maxWidth: 1280,
          margin: '24px auto 0',
          paddingTop: 16,
          borderTop: '1px solid var(--border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 8,
          fontSize: 12,
          color: 'var(--text-tertiary)',
        }}
      >
        <span>© 2026 PHAROS. MIT License.</span>
        <span>Built with IBM Granite, Docling, and SGP4. Data: CelesTrak.</span>
      </div>
    </footer>
  )
}
