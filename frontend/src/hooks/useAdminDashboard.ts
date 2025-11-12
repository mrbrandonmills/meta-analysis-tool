import { useState, useCallback } from 'react';
import {
  AdminDashboardData,
  ResearcherListItem,
  PayoutHistoryItem
} from '@/lib/payment-types';

export interface UseAdminDashboardReturn {
  dashboardData: AdminDashboardData | null;
  researchers: ResearcherListItem[];
  payoutHistory: PayoutHistoryItem[];
  loading: boolean;
  error: string | null;
  fetchDashboard: () => Promise<void>;
  fetchResearchers: (filters?: ResearcherFilters) => Promise<void>;
  fetchPayoutHistory: (startMonth?: string, endMonth?: string) => Promise<void>;
  distributePayouts: (poolMonth: string, dryRun?: boolean) => Promise<any>;
}

interface ResearcherFilters {
  page?: number;
  pageSize?: number;
  isPayingMember?: boolean;
  minHIndex?: number;
  sortBy?: 'h_index' | 'earnings' | 'reviews_count';
}

export function useAdminDashboard(): UseAdminDashboardReturn {
  const [dashboardData, setDashboardData] = useState<AdminDashboardData | null>(null);
  const [researchers, setResearchers] = useState<ResearcherListItem[]>([]);
  const [payoutHistory, setPayoutHistory] = useState<PayoutHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/admin/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('Access denied: Admin role required');
        }
        throw new Error('Failed to fetch dashboard data');
      }

      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchResearchers = useCallback(async (filters: ResearcherFilters = {}) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filters.page) params.append('page', String(filters.page));
      if (filters.pageSize) params.append('page_size', String(filters.pageSize));
      if (filters.isPayingMember !== undefined) {
        params.append('is_paying_member', String(filters.isPayingMember));
      }
      if (filters.minHIndex) params.append('min_h_index', String(filters.minHIndex));
      if (filters.sortBy) params.append('sort_by', filters.sortBy);

      const response = await fetch(`/api/v1/admin/researchers?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch researchers');
      }

      const data = await response.json();
      setResearchers(data.researchers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchPayoutHistory = useCallback(
    async (startMonth?: string, endMonth?: string) => {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        if (startMonth) params.append('start_month', startMonth);
        if (endMonth) params.append('end_month', endMonth);

        const response = await fetch(`/api/v1/admin/payouts/history?${params}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch payout history');
        }

        const data = await response.json();
        setPayoutHistory(data.payoutHistory);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const distributePayouts = useCallback(
    async (poolMonth: string, dryRun: boolean = false) => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/v1/payouts/calculate-monthly', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({ poolMonth, dryRun })
        });

        if (!response.ok) {
          throw new Error('Failed to distribute payouts');
        }

        const data = await response.json();

        // Refresh dashboard data after distribution
        if (!dryRun) {
          await fetchDashboard();
          await fetchPayoutHistory();
        }

        return data;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [fetchDashboard, fetchPayoutHistory]
  );

  return {
    dashboardData,
    researchers,
    payoutHistory,
    loading,
    error,
    fetchDashboard,
    fetchResearchers,
    fetchPayoutHistory,
    distributePayouts
  };
}
