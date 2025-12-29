/**
 * API Service for communicating with the backend
 */

import { encryptPassword } from '../utils/crypto';

const API_BASE_URL = 'http://127.0.0.1:8000';

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: Record<string, unknown>;
  headers?: Record<string, string>;
}

class ApiService {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  private async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config: RequestInit = {
      method: options.method || 'GET',
      headers,
    };

    if (options.body) {
      config.body = JSON.stringify(options.body);
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, config);

    if (!response.ok) {
      if (response.status === 401) {
        this.setToken(null);
        window.location.href = '/login';
      }
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Auth Service
  public auth = {
    login: async (email: string, password: string, rememberMe: boolean = false) => {
      // Encrypt password before sending to backend
      const encryptedPassword = await encryptPassword(password);
      const data = await this.request<any>('/api/auth/login', {
        method: 'POST',
        body: { email, password: encryptedPassword, remember_me: rememberMe }
      });
      this.setToken(data.access_token);
      return data;
    },
    signup: async (email: string, password: string, username: string, name: string, termsAccepted: boolean, privacyAccepted: boolean) => {
      // Encrypt password before sending to backend
      const encryptedPassword = await encryptPassword(password);
      return this.request<any>('/api/auth/signup', {
        method: 'POST',
        body: { email, password: encryptedPassword, username, name, terms_accepted: termsAccepted, privacy_accepted: privacyAccepted }
      });
    },
    initiateGoogleLogin: async () => {
      return this.request<{ authorization_url: string; state: string }>('/api/auth/login');
    },
    initiateGoogleSignup: async () => {
      return this.request<{ authorization_url: string; state: string; action: string }>('/api/auth/google/signup');
    },
    logout: async () => {
      await this.request('/api/auth/logout', { method: 'POST' });
      this.setToken(null);
    },
    getCurrentUser: async () => {
      return this.request<{ id: number; email: string; name: string }>('/api/auth/me');
    },
    forgotPassword: async (email: string) => {
      return this.request<{ message: string }>('/api/auth/forgot-password', {
        method: 'POST',
        body: { email }
      });
    },
    resetPassword: async (token: string, password: string) => {
      // Encrypt password before sending to backend
      const encryptedPassword = await encryptPassword(password);
      return this.request<{ message: string }>('/api/auth/reset-password', {
        method: 'POST',
        body: { token, password: encryptedPassword }
      });
    },
    validateResetToken: async (token: string) => {
      return this.request<{ valid: boolean; email: string }>('/api/auth/validate-reset-token', {
        method: 'POST',
        body: { token }
      });
    },
    verifyEmail: async (token: string) => {
      return this.request<{ message: string }>('/api/auth/verify-email', {
        method: 'POST',
        body: { token }
      });
    },
    resendVerification: async (email: string) => {
      return this.request<{ message: string }>('/api/auth/resend-verification', {
        method: 'POST',
        body: { email }
      });
    },
    acceptTerms: async () => {
      return this.request<{ message: string }>('/api/auth/accept-terms', {
        method: 'POST'
      });
    },
    checkEmail: async (email: string) => {
      return this.request<{ exists: boolean }>(`/api/auth/check-email?email=${encodeURIComponent(email)}`);
    },
    changePassword: async (currentPassword: string, newPassword: string) => {
      // Encrypt passwords before sending to backend
      const encryptedCurrentPassword = await encryptPassword(currentPassword);
      const encryptedNewPassword = await encryptPassword(newPassword);
      return this.request<{ message: string }>('/api/auth/change-password', {
        method: 'POST',
        body: { current_password: encryptedCurrentPassword, new_password: encryptedNewPassword }
      });
    }
  };



  // Email endpoints
  async syncEmails(daysBack = 30, maxEmails = 100, useAi = false) {
    return this.request<{
      status: string;
      emails_processed: number;
      transactions_found: number;
      message: string;
    }>('/api/email/sync', {
      method: 'POST',
      body: { days_back: daysBack, max_emails: maxEmails, use_ai: useAi },
    });
  }

  async uploadCsv(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const headers: Record<string, string> = {};
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}/api/transactions/upload-csv`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async previewEmails(limit = 10) {
    return this.request<{
      total_emails: number;
      transactions: Array<{
        email_id: string;
        date: string;
        amount: number;
        trans_type: string;
        merchant: string;
        category: string;
        category_confidence: number;
      }>;
    }>(`/api/email/preview?limit=${limit}`);
  }

  async getEmailSyncStatus() {
    return this.request<{
      last_sync: string | null;
      total_emails_synced: number;
      total_transactions: number;
      sync_in_progress: boolean;
    }>('/api/email/status');
  }

  // Transaction endpoints
  async getTransactions(params: {
    page?: number;
    page_size?: number;
    trans_type?: string;
    category_id?: number;
    search?: string;
  } = {}) {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, String(value));
      }
    });

    return this.request<{
      total: number;
      page: number;
      page_size: number;
      transactions: Array<{
        id: number;
        date: string;
        amount: number;
        trans_type: string;
        merchant: string;
        category_name: string | null;
        category_icon: string | null;
        bank_name: string | null;
        description: string | null;
      }>;
    }>(`/api/transactions?${queryParams.toString()}`);
  }

  async getMonthlyStats(monthYear?: string) {
    const params = monthYear ? `?month_year=${monthYear}` : '';
    return this.request<{
      month_year: string;
      total_income: number;
      total_expenses: number;
      net_savings: number;
      savings_rate: number;
      category_breakdown: Array<{
        category_id: number;
        category_name: string;
        category_icon: string;
        category_color: string;
        total_amount: number;
        transaction_count: number;
        percentage: number;
      }>;
    }>(`/api/transactions/stats${params}`);
  }

  async createTransaction(data: {
    date: string;
    amount: number;
    trans_type: string;
    merchant: string;
    category_id?: number;
    description?: string;
  }) {
    return this.request('/api/transactions', {
      method: 'POST',
      body: data,
    });
  }

  async updateTransaction(id: number, data: {
    category_id?: number;
    merchant?: string;
    description?: string;
  }) {
    return this.request(`/api/transactions/${id}`, {
      method: 'PUT',
      body: data,
    });
  }

  async deleteTransaction(id: number) {
    return this.request(`/api/transactions/${id}`, { method: 'DELETE' });
  }

  // Health check
  async healthCheck() {
    return this.request<{
      status: string;
      service: string;
      version: string;
    }>('/health');
  }

  // Leaks
  async detectLeaks() {
    return this.request<{ message: string }>('/api/leaks/detect', { method: 'POST' });
  }

  async getLeaks() {
    return this.request<Array<{
      id: number;
      leak_type: string;
      title: string;
      description: string;
      severity: string;
      detected_amount: number;
      frequency: string;
      created_at: string;
    }>>('/api/leaks');
  }

  async getSubscriptions() {
    return this.request<Array<{
      id: number;
      name: string;
      amount: number;
      interval_days: number;
      next_expected_date: string;
      merchant: string;
      is_active: boolean;
    }>>('/api/leaks/subscriptions');
  }

  async resolveLeak(id: number) {
    return this.request<{ message: string }>(`/api/leaks/leaks/${id}/resolve`, { method: 'PUT' });
  }
}

export const api = new ApiService(API_BASE_URL);
export const authService = api.auth;
export default api;
