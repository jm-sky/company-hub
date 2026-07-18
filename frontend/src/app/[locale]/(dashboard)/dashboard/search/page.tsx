'use client'

import { useState } from 'react'
import { useTranslations } from 'next-intl'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertCircle } from 'lucide-react'
import { useCompany } from '@/lib/hooks/useCompanies'
import { CompanySearchForm } from '@/components/company/CompanySearchForm'
import { CompanyStatusIndicators } from '@/components/company/CompanyStatusIndicators'
import { CompanyDataDisplay } from '@/components/company/CompanyDataDisplay'

export default function CompanySearchPage() {
  const t = useTranslations('company')
  const errors = useTranslations('errors')
  const [queriedNip, setQueriedNip] = useState('')
  const [requestTime, setRequestTime] = useState(0)

  const { data: companyResponse, isLoading, error } = useCompany(queriedNip)

  const handleSearch = (nip: string) => {
    setRequestTime(Date.now())
    setQueriedNip(nip)
  }

  const handleClear = () => {
    setQueriedNip('')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">{t('searchPageTitle')}</h1>
        <p className="text-muted-foreground">
          {t('searchPageSubtitle')}
        </p>
      </div>

      {/* Search Form */}
      <CompanySearchForm
        onSearch={handleSearch}
        onClear={handleClear}
        isLoading={isLoading}
        currentNip={queriedNip}
      />

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="size-4" />
          <AlertDescription>
            {t('errorSearchingForCompany')} {error instanceof Error ? error.message : errors('unknownError')}
          </AlertDescription>
        </Alert>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="space-y-4">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
      )}

      {/* Results */}
      {companyResponse && !isLoading && (
        <div className="space-y-6">
          <CompanyStatusIndicators companyResponse={companyResponse} requestTime={requestTime} />
          <CompanyDataDisplay companyResponse={companyResponse} />
        </div>
      )}
    </div>
  )
}
