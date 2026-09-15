import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Healthcare Operations Assistant',
  description: 'Real-Time Healthcare Operations Assistant with Voice AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
