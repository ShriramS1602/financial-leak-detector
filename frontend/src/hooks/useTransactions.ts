import { useState, useEffect, useCallback } from 'react';
import api, { authService } from '../services/api';
import type { MonthlyStats } from '../types';

interface UseTransactionsOptions {
  page?: number;
  pageSize?: number;
  transType?: string;
  categoryId?: number;
  search?: string;
}

export function useTransactions(options: UseTransactionsOptions = {}) {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getTransactions({
        page: options.page,
        page_size: options.pageSize,
        trans_type: options.transType,
        category_id: options.categoryId,
        search: options.search,
      });
      setTransactions(response.transactions);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch transactions'));
    } finally {
      setLoading(false);
    }
  }, [options.page, options.pageSize, options.transType, options.categoryId, options.search]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  return { transactions, total, loading, error, refetch: fetchTransactions };
}

export function useMonthlyStats(monthYear?: string) {
  const [stats, setStats] = useState<MonthlyStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getMonthlyStats(monthYear);
      setStats(response);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch stats'));
    } finally {
      setLoading(false);
    }
  }, [monthYear]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return { stats, loading, error, refetch: fetchStats };
}

export function useAuth() {
  const [user, setUser] = useState<{ email: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchUser = useCallback(async () => {
    setLoading(true);
    try {
      const response = await authService.getCurrentUser();
      setUser(response);
    } catch (err) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async () => {
    try {
      const { authorization_url } = await authService.initiateGoogleLogin();
      window.location.href = authorization_url;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to initiate login'));
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
      api.setToken(null);
      setUser(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to logout'));
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  return { user, loading, error, login, logout, refetch: fetchUser };
}

export function useEmailSync() {
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [result, setResult] = useState<{
    status: string;
    emails_processed: number;
    transactions_found: number;
    message: string;
  } | null>(null);

  const syncEmails = useCallback(async (daysBack = 30, maxEmails = 100) => {
    setSyncing(true);
    setError(null);
    try {
      const response = await api.syncEmails(daysBack, maxEmails);
      setResult(response);
      return response;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to sync emails'));
      throw err;
    } finally {
      setSyncing(false);
    }
  }, []);

  return { syncing, error, result, syncEmails };
}
