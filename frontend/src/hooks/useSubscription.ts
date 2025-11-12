import { useState, useCallback } from 'react';
import {
  Subscription,
  SubscriptionCreateRequest,
  SubscriptionResponse
} from '@/lib/payment-types';

export interface UseSubscriptionReturn {
  subscription: Subscription | null;
  loading: boolean;
  error: string | null;
  fetchSubscription: () => Promise<void>;
  createSubscription: (data: SubscriptionCreateRequest) => Promise<SubscriptionResponse>;
  cancelSubscription: (reason: string) => Promise<void>;
  updatePaymentMethod: (paymentMethodId: string) => Promise<void>;
}

export function useSubscription(): UseSubscriptionReturn {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSubscription = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/subscriptions/me', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch subscription');
      }

      const data = await response.json();
      setSubscription(data.subscription);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  const createSubscription = useCallback(
    async (data: SubscriptionCreateRequest): Promise<SubscriptionResponse> => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/v1/subscriptions/create', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(data)
        });

        if (!response.ok) {
          throw new Error('Failed to create subscription');
        }

        const result = await response.json();
        await fetchSubscription(); // Refresh subscription data
        return result;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [fetchSubscription]
  );

  const cancelSubscription = useCallback(
    async (reason: string) => {
      if (!subscription) return;

      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/v1/subscriptions/${subscription.id}/cancel`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({ cancellationReason: reason, immediate: false })
        });

        if (!response.ok) {
          throw new Error('Failed to cancel subscription');
        }

        await fetchSubscription(); // Refresh subscription data
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [subscription, fetchSubscription]
  );

  const updatePaymentMethod = useCallback(
    async (paymentMethodId: string) => {
      if (!subscription) return;

      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/v1/subscriptions/${subscription.id}/update-payment`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({ paymentMethodId })
        });

        if (!response.ok) {
          throw new Error('Failed to update payment method');
        }

        await fetchSubscription(); // Refresh subscription data
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [subscription, fetchSubscription]
  );

  return {
    subscription,
    loading,
    error,
    fetchSubscription,
    createSubscription,
    cancelSubscription,
    updatePaymentMethod
  };
}
