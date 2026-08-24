/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'bg-base': 'var(--bg-base)',
        'bg-surface': 'var(--bg-surface)',
        'bg-elevated': 'var(--bg-elevated)',
        'bg-overlay': 'var(--bg-overlay)',
        'text-primary': 'var(--text-primary)',
        'text-secondary': 'var(--text-secondary)',
        'text-tertiary': 'var(--text-tertiary)',
        'accent-primary': 'var(--accent-primary)',
        'accent-blue': 'var(--accent-primary)',
        'accent-glow': 'var(--accent-glow)',
        'accent-cyan': 'var(--accent-cyan)',
        'status-pass': 'var(--status-pass)',
        'status-flag': 'var(--status-flag)',
        'status-fail': 'var(--status-fail)',
        'border-subtle': 'var(--border-subtle)',
        'border-hover': 'var(--border-hover)',
      },
      fontFamily: {
        display: ['var(--font-display)', 'var(--font-sans)', 'system-ui', 'sans-serif'],
        sans: ['var(--font-sans)', 'IBM Plex Sans', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'IBM Plex Mono', 'monospace'],
      },
      letterSpacing: {
        tightest: '-0.04em',
        tighter: '-0.03em',
        tight: '-0.02em',
        tracked: '0.2em',
        label: '0.12em',
      },
      maxWidth: {
        container: '1280px',
      },
      boxShadow: {
        'glow-primary': '0 0 24px var(--accent-glow)',
        'glow-cyan': '0 0 24px rgba(34, 211, 238, 0.2)',
      },
    },
  },
  plugins: [],
}
