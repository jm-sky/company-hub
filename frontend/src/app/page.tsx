'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useUser } from '@/lib/hooks/useAuth'
import LandingPage from '@/components/landing/landing-page'

export default function Home() {
  const { data: user, isLoading } = useUser()
  const router = useRouter()

  // Auto-redirect authenticated users to dashboard
  useEffect(() => {
    if (!isLoading && user) {
      router.replace('/dashboard')
    }
  }, [user, isLoading, router])

  return <LandingPage />
}
