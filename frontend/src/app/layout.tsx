import type { Metadata, Viewport } from 'next'
import { Space_Grotesk, IBM_Plex_Sans, IBM_Plex_Mono } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/theme/ThemeProvider'

const fontDisplay = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-display',
  weight: ['600', '700'],
  display: 'swap',
})

const fontSans = IBM_Plex_Sans({
  subsets: ['latin'],
  variable: '--font-sans',
  weight: ['300', '400', '500', '600', '700'],
  display: 'swap',
})

const fontMono = IBM_Plex_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  weight: ['400', '500', '600'],
  display: 'swap',
})

export const metadata: Metadata = {
  metadataBase: new URL('https://pharos-space.com'),
  title: 'PHAROS — Satellite Compliance Intelligence',
  description:
    'Check any satellite against every deorbit and debris-mitigation standard that governs low Earth orbit, before regulators find violations.',
  keywords: [
    'satellite compliance',
    'orbital debris',
    'FCC deorbit rule',
    'IADC guidelines',
    'space debris mitigation',
    'ISO 24113',
    'ESA Zero Debris',
    'COPUOS',
    'space regulation',
  ],
  openGraph: {
    title: 'PHAROS — Satellite Compliance Intelligence',
    description: 'Check any satellite against every deorbit and debris-mitigation standard.',
    type: 'website',
    images: ['/og.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'PHAROS — Satellite Compliance Intelligence',
    description: 'Check any satellite against every deorbit and debris-mitigation standard.',
    images: ['/og.png'],
  },
}

export const viewport: Viewport = {
  themeColor: '#0d0d14',
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html
      lang="en"
      className={`${fontDisplay.variable} ${fontSans.variable} ${fontMono.variable} dark`}
      suppressHydrationWarning
    >
      <body className="bg-bg-base text-text-primary antialiased font-sans transition-colors duration-200">
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  )
}
