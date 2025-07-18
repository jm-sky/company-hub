// Union types
export type CompanyStatus = 'active' | 'inactive';
export type VatStatus = 'active' | 'inactive' | 'exempt';
export type SubscriptionTier = 'free' | 'pro' | 'enterprise';
export type ProviderStatus = 'fresh' | 'cached' | 'rate_limited' | 'error' | 'unknown';

export interface ApiResponse<T = unknown> {
  data: T;
  message?: string;
  success: boolean;
}

export interface Company {
  nip: string;
  name: string;
  regon?: string;
  status: CompanyStatus;
  address?: {
    street: string;
    city: string;
    postal_code: string;
    country: string;
  };
  vat_status?: VatStatus;
  bank_accounts?: Array<{
    account_number: string;
    bank_name?: string;
    currency?: string;
    is_valid?: boolean;
  }>;
  last_updated: string;
  data_sources: string[];
}

export interface User {
  id: string;
  email: string;
  name?: string;
  subscription_tier: SubscriptionTier;
  api_calls_used: number;
  api_calls_limit: number;
  created_at: string;
}

export interface ApiKey {
  id: string;
  name: string;
  key: string;
  last_used?: string;
  created_at: string;
  is_active: boolean;
}

export interface Webhook {
  id: string;
  url: string;
  events: string[];
  secret: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface SearchCompaniesResponse {
  companies: Company[];
  total: number;
  page: number;
  limit: number;
}

export interface SubscriptionInfo {
  tier: SubscriptionTier;
  usage: number;
  limit: number;
}

export interface CheckoutSession {
  checkout_url: string;
}

// Provider metadata for company data
export interface ProviderMetadata {
  status: ProviderStatus;
  cached_at?: string;
  fetched_at?: string;
  next_available_at?: string;
  error_message?: string;
}

// REGON API response structures
export interface RegonSearchData {
  Regon: string;
  Nip: string;
  StatusNip: string | null;
  Nazwa: string;
  Wojewodztwo: string;
  Powiat: string;
  Gmina: string;
  Miejscowosc: string;
  KodPocztowy: string;
  Ulica: string;
  NrNieruchomosci: string;
  NrLokalu: string | null;
  Typ: string;
  SilosID: string;
  DataZakonczeniaDzialalnosci: string | null;
  MiejscowoscPoczty: string;
}

export interface RegonDetailedData {
  raw_response: string;
  report_type: string;
  parsed_data?: Record<string, string>;
}

export interface RegonCompanyData {
  found: boolean;
  nip: string;
  regon?: string;
  name?: string;
  entity_type?: string;
  search_result?: {
    found: boolean;
    data: RegonSearchData;
  };
  detailed_data?: RegonDetailedData;
  report_type?: string;
  fetched_at: string;
  message?: string;
  detailed_error?: string;
}

// Updated Company interface to match backend response structure
export interface CompanyData {
  nip: string;
  regon?: RegonCompanyData;
  mf?: Record<string, unknown>;
  vies?: Record<string, unknown>;
  bank_accounts?: Record<string, unknown>[];
}

export interface CompanyMetadata {
  regon?: ProviderMetadata;
  mf?: ProviderMetadata;
  vies?: ProviderMetadata;
}

// Company response uses the standard ApiResponse pattern
export interface CompanyResponse {
  data: CompanyData;
  metadata: CompanyMetadata;
}
