import { useState, useCallback } from 'react';
import {
  EarningsSummary,
  PayoutPool,
  PayoutDistribution
} from '@/lib/payment-types';

export interface UsePayoutsReturn {
  earnings: EarningsSummary | null;
  currentPool: PayoutPool | null;
  poolHistory: PayoutPool[];
  distributions: PayoutDistribution[];
  loading: boolean;
  error: string | null;
  fetchEarnings: () => Promise<void>;
  fetchCurrentPool: () => Promise<void>;
  fetchPoolHistory: () => Promise<void>;
  fetchPoolByMonth: (month: string, year: number) => Promise<PayoutPool>;
  fetchDistributions: (poolId: string) => Promise<void>;
}

export function usePayouts(): UsePayoutsReturn {
  const [earnings, setEarnings] = useState<EarningsSummary | null>(null);
  const [currentPool, setCurrentPool] = useState<PayoutPool | null>(null);
  const [poolHistory, setPoolHistory] = useState<PayoutPool[]>([]);
  const [distributions, setDistributions] = useState<PayoutDistribution[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEarnings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/payouts/earnings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch earnings');
      }

      const data = await response.json();
      setEarnings(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchCurrentPool = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const now = new Date();
      const month = now.getMonth() + 1;
      const year = now.getFullYear();
      const poolMonth = `${year}-${String(month).padStart(2, '0')}-01`;

      const response = await fetch(`/api/v1/payouts/pool/${poolMonth}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch current pool');
      }

      const data = await response.json();
      setCurrentPool(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchPoolByMonth = useCallback(async (month: string, year: number): Promise<PayoutPool> => {
    setLoading(true);
    setError(null);
    try {
      const poolMonth = `${year}-${String(month).padStart(2, '0')}-01`;
      const response = await fetch(`/api/v1/payouts/pool/${poolMonth}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch pool');
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchDistributions = useCallback(async (poolId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/v1/payouts/distributions/${poolId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch distributions');
      }

      const data = await response.json();
      setDistributions(data.distributions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchPoolHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/payouts/pool-history', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch pool history');
      }

      const data = await response.json();
      setPoolHistory(data.pools || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    earnings,
    currentPool,
    poolHistory,
    distributions,
    loading,
    error,
    fetchEarnings,
    fetchCurrentPool,
    fetchPoolHistory,
    fetchPoolByMonth,
    fetchDistributions
  };
}
