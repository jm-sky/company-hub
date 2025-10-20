'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useUser } from '@/lib/hooks/useAuth'
import { Building2, Search, CreditCard, Activity, TrendingUp, InfoIcon } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { useTranslations } from 'next-intl'

export default function DashboardPage() {
  const { data: user } = useUser()
  const t = useTranslations('dashboard')
  const common = useTranslations('common')
  const company = useTranslations('company')

  const stats = [
    {
      name: t('companiesSearched'),
      value: '127',
      icon: Building2,
      change: '+12%',
      changeType: 'positive' as const,
    },
    {
      name: t('apiCallsThisMonth'),
      value: '89',
      icon: Activity,
      change: '+8%',
      changeType: 'positive' as const,
    },
    {
      name: t('planUsage'),
      value: user?.subscription_tier === 'free' ? '89/100' : '89/1000', // TODO: change to actual usage
      icon: TrendingUp,
      change: user?.subscription_tier === 'free' ? '89%' : '8.9%', // TODO: change to actual usage
      changeType: user?.subscription_tier === 'free' ? 'warning' : 'positive' as const, // TODO: change to actual usage
    },
  ]

  const quickActions = [
    {
      title: company('searchCompany'),
      description: company('lookUpCompanyInformation'),
      icon: Search,
      href: '/dashboard/search',
      color: 'bg-blue-500',
    },
    {
      title: t('companies'),
      description: company('browseYourSavedCompanies'),
      icon: Building2,
      href: '/dashboard/companies',
      color: 'bg-green-500',
      disabled: true,
    },
    {
      title: t('upgradePlan'),
      description: t('getMoreApiCalls'),
      icon: CreditCard,
      href: '/dashboard/subscription',
      color: 'bg-purple-500',
      disabled: true,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">{t('dashboard')}</h1>
        <p className="text-muted-foreground">
          {t('welcomeBack')} {user?.name ?? user?.email}. {t('heresWhatHappening')}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat) => (
          <Card key={stat.name}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.name}</CardTitle>
              <stat.icon className="size-4 text-gray-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className={`text-xs ${
                stat.changeType === 'positive'
                  ? 'text-green-600'
                  : stat.changeType === 'warning'
                  ? 'text-yellow-600'
                  : 'text-red-600'
              }`}>
                {stat.change} {common('fromLastMonth')}
              </p>
              <p className="text-xs text-muted-foreground">
                {common('mockData')}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('quickActions')}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {quickActions.map((action) => (
            <Card key={action.title} className={`cursor-pointer hover:shadow-md transition-shadow ${action.disabled ? 'opacity-50 cursor-not-allowed' : ''}`}>
              <CardHeader>
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${action.color}`}>
                    <action.icon className="size-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-base">{action.title}</CardTitle>
                  </div>
                </div>
                <CardDescription>{action.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" size="sm" asChild>
                  <a href={action.href}>{common('getStarted')}</a>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {t('recentActivity')}
            <Badge variant="warning" className="flex items-center gap-2 text-xs">
              <InfoIcon className="size-4" />
              {common('mockedData')}
            </Badge>
          </CardTitle>
          <CardDescription>{t('yourLatestCompanySearches')}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center space-x-3">
                <Building2 className="size-4 text-gray-400" />
                <div>
                  <p className="text-sm font-medium">{company('searched')} ABC Company Sp. z o.o.</p>
                  <p className="text-xs text-gray-500">NIP: 1234567890</p>
                </div>
              </div>
              <p className="text-xs text-gray-500">2 {common('hoursAgo')}</p>
            </div>
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center space-x-3">
                <Building2 className="size-4 text-gray-400" />
                <div>
                  <p className="text-sm font-medium">{company('searched')} XYZ Corporation S.A.</p>
                  <p className="text-xs text-gray-500">NIP: 9876543210</p>
                </div>
              </div>
              <p className="text-xs text-gray-500">1 {common('daysAgo')}</p>
            </div>
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center space-x-3">
                <Activity className="size-4 text-gray-400" />
                <div>
                  <p className="text-sm font-medium">{company('apiCall')} {company('webhookUpdated')}</p>
                  <p className="text-xs text-gray-500">{company('dataChangedEvent')}</p>
                </div>
              </div>
              <p className="text-xs text-gray-500">2 {common('daysAgo')}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
