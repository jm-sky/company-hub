/**
 * Utility functions for handling company data
 */

/**
 * Type guard to safely access properties from unknown Record types
 */
export function getProperty(data: Record<string, unknown>, key: string): string | null {
  if (key in data && typeof data[key] === 'string') {
    return data[key] as string
  }
  return null
}

/**
 * Safe access to REGON data properties
 */
export function getRegonProperty(regonData: Record<string, unknown>, key: string): string | null {
  return getProperty(regonData, key)
}

/**
 * Get status icon and color for provider status
 */
export function getProviderStatusInfo(status: string) {
  switch (status) {
    case 'fresh':
    case 'cached':
      return { icon: 'CheckCircle', color: 'text-green-500', label: 'Available' }
    case 'rate_limited':
      return { icon: 'Clock', color: 'text-yellow-500', label: 'Rate Limited' }
    case 'error':
      return { icon: 'AlertCircle', color: 'text-red-500', label: 'Error' }
    default:
      return { icon: 'AlertCircle', color: 'text-gray-500', label: 'Unknown' }
  }
}

/**
 * Get human-readable status text
 */
export function getStatusText(status: string): string {
  switch (status) {
    case 'fresh':
      return 'Fresh data'
    case 'cached':
      return 'Cached data'
    case 'cached_due_to_rate_limit':
      return 'Cached (rate limited)'
    case 'rate_limited':
      return 'Rate limited'
    case 'error':
      return 'Error'
    default:
      return 'Unknown'
  }
}

/**
 * Check if company has any data available
 */
export function hasCompanyData(companyResponse: { data: { regon?: unknown; mf?: unknown; vies?: unknown } }): boolean {
  return !!(companyResponse?.data?.regon || companyResponse?.data?.mf || companyResponse?.data?.vies)
}