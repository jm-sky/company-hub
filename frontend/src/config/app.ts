export const APP_CONFIG = {
  name: 'CompanyHub',
  displayName: {
    company: 'Company',
    hub: 'Hub'
  },
  description: 'Centralized API service for Polish company data aggregation'
} as const

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export const API_DOCS_URL = `${API_URL}/docs`