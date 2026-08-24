import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
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
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-bg-primary text-text-primary antialiased">
        {children}
      </body>
    </html>
  )
}
