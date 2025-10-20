'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useUser } from '@/lib/hooks/useAuth'
import LandingPage from '@/components/landing/landing-page'
import { useLocale } from 'next-intl'

export default function Home() {
  const { data: user, isLoading } = useUser()
  const router = useRouter()
  const locale = useLocale()

  // Auto-redirect authenticated users to dashboard
  useEffect(() => {
    if (!isLoading && user) {
      router.replace(`/${locale}/dashboard`)
    }
  }, [user, isLoading, router, locale])

  return <LandingPage />
}
