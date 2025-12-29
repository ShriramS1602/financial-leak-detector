/**
 * Transaction Types
 */

export type TransactionType = 'credit' | 'debit';

export interface Transaction {
  id: number;
  date: string;
  amount: number;
  trans_type: TransactionType;
  merchant: string;
  category_id?: number;
  category_name?: string;
  category_icon?: string;
  description?: string;
  bank_name?: string;
  email_id?: string;
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  icon: string;
  color: string;
  is_income: boolean;
  description?: string;
}

export interface MonthlyStats {
  month_year: string;
  total_income: number;
  total_expenses: number;
  net_savings: number;
  savings_rate: number;
  category_breakdown: CategoryBreakdown[];
}

export interface CategoryBreakdown {
  category_id: number;
  category_name: string;
  category_icon: string;
  category_color: string;
  total_amount: number;
  transaction_count: number;
  percentage: number;
}

export type SpendingHealth = 'excellent' | 'good' | 'moderate' | 'poor';

export interface Insight {
  type: 'positive' | 'warning' | 'info';
  message: string;
}

export interface User {
  id: number;
  email: string;
  name?: string;
  last_email_sync?: string;
  created_at: string;
}

export interface EmailSyncStatus {
  last_sync: string | null;
  total_emails_synced: number;
  total_transactions: number;
  sync_in_progress: boolean;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}
