import axios, { HttpStatusCode, AxiosInstance } from 'axios';
import {
  ApiResponse,
  User,
  ApiKey,
  Webhook,
  AuthResponse,
  SearchCompaniesResponse,
  SubscriptionInfo,
  CheckoutSession,
  SubscriptionTier,
  CompanyResponse,
  LoginCredentials,
  RegisterRequest,
  OAuthCallbackRequest,
} from '@/types/api';

class ApiClient {
  private client: AxiosInstance;
  private authToken: string | null = null;

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (!this.authToken) {
          this.loadAuthFromStorage();
        }
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === HttpStatusCode.Unauthorized) {
          // Don't redirect if this is a login/register request (expected 401)
          const isAuthRequest = error.config?.url?.includes('/auth/login') ||
                               error.config?.url?.includes('/auth/register');

          if (!isAuthRequest) {
            this.clearAuth();
            window.location.href = '/login?reason=session-expired';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  setAuth(token: string) {
    this.authToken = token;
    localStorage.setItem('auth_token', token);
  }

  clearAuth() {
    this.authToken = null;
    localStorage.removeItem('auth_token');
  }

  loadAuthFromStorage() {
    const token = localStorage.getItem('auth_token');
    if (token) {
      this.authToken = token;
    }
  }

  // Authentication endpoints
  async login(email: string, password: string, recaptchaToken?: string | null): Promise<ApiResponse<AuthResponse>> {
    const data: LoginCredentials = { email, password };
    if (recaptchaToken) {
      data.recaptcha_token = recaptchaToken;
    }
    const response = await this.client.post('/api/v1/auth/login', data);
    return response.data;
  }

  async register(email: string, password: string, name: string, recaptchaToken?: string | null): Promise<ApiResponse<AuthResponse>> {
    const data: RegisterRequest = { email, password, name };
    if (recaptchaToken) {
      data.recaptcha_token = recaptchaToken;
    }
    const response = await this.client.post('/api/v1/auth/register', data);
    return response.data;
  }

  async forgotPassword(email: string): Promise<ApiResponse> {
    const response = await this.client.post('/api/v1/auth/forgot-password', { email });
    return response.data;
  }

  async resetPassword(token: string, password: string): Promise<ApiResponse> {
    const response = await this.client.post('/api/v1/auth/reset-password', { token, password });
    return response.data;
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<ApiResponse> {
    const response = await this.client.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response.data;
  }

  // OAuth endpoints
  async getOAuthAuthUrl(provider: string): Promise<ApiResponse<{ auth_url: string; state: string }>> {
    const response = await this.client.post('/api/v1/auth/oauth/auth-url', { provider });
    return response.data;
  }

  async oauthCallback(provider: string, code: string, state: string, recaptchaToken?: string | null): Promise<ApiResponse<AuthResponse>> {
    const data: OAuthCallbackRequest = { code, state };
    if (recaptchaToken) {
      data.recaptcha_token = recaptchaToken;
    }
    const response = await this.client.post(`/api/v1/auth/oauth/${provider}/callback`, data);
    return response.data;
  }

  // Company endpoints
  async getCompany(nip: string, refresh: boolean = false): Promise<ApiResponse<CompanyResponse>> {
    const params = refresh ? { refresh: 'true' } : {};
    const response = await this.client.get(`/api/v1/companies/${nip}`, { params });
    return response.data;
  }

  async searchCompanies(query: string, page: number = 1, limit: number = 20): Promise<ApiResponse<SearchCompaniesResponse>> {
    const response = await this.client.get('/api/v1/companies/search', {
      params: { q: query, page, limit }
    });
    return response.data;
  }

  // User endpoints
  async getProfile(): Promise<ApiResponse<User>> {
    const response = await this.client.get('/api/v1/auth/me');
    return response.data;
  }

  async updateProfile(data: Partial<User>): Promise<ApiResponse<User>> {
    const response = await this.client.put('/api/v1/user/profile', data);
    return response.data;
  }

  // API Keys endpoints
  async getApiKeys(): Promise<ApiResponse<ApiKey[]>> {
    const response = await this.client.get('/api/v1/user/api-keys');
    return response.data;
  }

  async createApiKey(name: string): Promise<ApiResponse<ApiKey>> {
    const response = await this.client.post('/api/v1/user/api-keys', { name });
    return response.data;
  }

  async deleteApiKey(id: string): Promise<ApiResponse> {
    const response = await this.client.delete(`/api/v1/user/api-keys/${id}`);
    return response.data;
  }

  // Webhooks endpoints
  async getWebhooks(): Promise<ApiResponse<Webhook[]>> {
    const response = await this.client.get('/api/v1/user/webhooks');
    return response.data;
  }

  async createWebhook(url: string, events: string[]): Promise<ApiResponse<Webhook>> {
    const response = await this.client.post('/api/v1/user/webhooks', { url, events });
    return response.data;
  }

  async updateWebhook(id: string, data: Partial<Webhook>): Promise<ApiResponse<Webhook>> {
    const response = await this.client.put(`/api/v1/user/webhooks/${id}`, data);
    return response.data;
  }

  async deleteWebhook(id: string): Promise<ApiResponse> {
    const response = await this.client.delete(`/api/v1/user/webhooks/${id}`);
    return response.data;
  }

  // Subscription endpoints
  async getSubscription(): Promise<ApiResponse<SubscriptionInfo>> {
    const response = await this.client.get('/api/v1/user/subscription');
    return response.data;
  }

  async createCheckoutSession(tier: Exclude<SubscriptionTier, 'free'>): Promise<ApiResponse<CheckoutSession>> {
    const response = await this.client.post('/api/v1/billing/checkout', { tier });
    return response.data;
  }
}

export const apiClient = new ApiClient();
