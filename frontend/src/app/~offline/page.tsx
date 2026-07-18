import Link from 'next/link'
import { APP_CONFIG } from '@/config/app'

export const dynamic = 'force-static'

export default function OfflinePage() {
  return (
    <main
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
        textAlign: 'center',
        fontFamily: 'system-ui, sans-serif',
        background: '#ffffff',
        color: '#0a0a0a',
      }}
    >
      <h1 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>
        You&apos;re offline
      </h1>
      <p style={{ color: '#737373', marginBottom: '1.5rem' }}>
        {APP_CONFIG.name} needs a network connection for this page.
      </p>
      <Link
        href="/"
        style={{
          color: '#3B5BDB',
          textDecoration: 'underline',
          fontWeight: 600,
        }}
      >
        Try again
      </Link>
    </main>
  )
}
