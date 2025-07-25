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

// Authentication endpoints
export interface LoginCredentials {
  email: string;
  password: string;
  recaptcha_token?: string;
}

export interface OAuthCallbackRequest {
  code: string;
  state: string;
  recaptcha_token?: string;
}

// Company endpoints
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
  subscription_tier?: SubscriptionTier;
  plan?: string;
  api_calls_used?: number;
  api_calls_limit?: number;
  created_at: string;
  is_active: boolean;
  oauth_provider?: string;
  github_username?: string;
  google_email?: string;
  avatar_url?: string;
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
  recaptcha_token?: string;
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

// MF (Biała Lista) API response structures
export interface MfBankAccountEnrichment {
  account_number: string;
  formatted_iban: string;
  validated: boolean;
  bank_name: string;
  bic: string;
  swift_code: string;
  bank_code: string;
  branch_code: string;
  bank_city: string;
  bank_country: string;
  bank_country_code: string;
  currency: string;
  enrichment_source: string;
  enriched_at: string;
  enrichment_available: boolean;
  enrichment_error?: string;
}

export interface MfBankAccount {
  account_number: string;
  validated: boolean;
  date: string;
  // IBAN enrichment fields
  bank_name?: string;
  bic?: string;
  swift_code?: string;
  formatted_iban?: string;
  enrichment_available?: boolean;
  enrichment?: MfBankAccountEnrichment;
  enrichment_error?: string;
}

export interface MfAddress {
  street: string;
  building_number: string;
  apartment_number: string;
  city: string;
  postal_code: string;
  country: string;
}

export interface MfPerson {
  company_name: string;
  first_name: string;
  last_name: string;
  nip: string;
  pesel: string;
}

export interface MfCompanyData {
  found: boolean;
  nip: string;
  date: string;
  name?: string;
  regon?: string;
  krs?: string;
  status_vat?: string;
  registration_legal_date?: string;
  registration_denial_basis?: string;
  registration_denial_date?: string;
  restoration_basis?: string;
  restoration_date?: string;
  removal_basis?: string;
  removal_date?: string;
  address?: MfAddress;
  residence_address?: MfAddress;
  bank_accounts?: MfBankAccount[];
  representatives?: MfPerson[];
  authorized_persons?: MfPerson[];
  partners?: MfPerson[];
  has_virtual_accounts?: boolean;
  request_id?: string;
  fetched_at: string;
  message?: string;
}

// Updated Company interface to match backend response structure
export interface CompanyData {
  nip: string;
  regon?: RegonCompanyData;
  mf?: MfCompanyData;
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
