export interface ApiResponse<T = unknown> {
  data: T;
  message?: string;
  success: boolean;
}

export interface Company {
  nip: string;
  name: string;
  regon?: string;
  status: 'active' | 'inactive';
  address?: {
    street: string;
    city: string;
    postal_code: string;
    country: string;
  };
  vat_status?: 'active' | 'inactive' | 'exempt';
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
  name: string;
  subscription_tier: 'free' | 'pro' | 'enterprise';
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
  tier: string;
  usage: number;
  limit: number;
}

export interface CheckoutSession {
  checkout_url: string;
}