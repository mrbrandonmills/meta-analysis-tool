import { useState, useCallback } from 'react';
import {
  PendingReview,
  ReviewApprovalRequest,
  ReviewApprovalResponse
} from '@/lib/payment-types';

interface UseReviewApprovalReturn {
  pendingReviews: PendingReview[];
  loading: boolean;
  error: string | null;
  fetchPendingReviews: () => Promise<void>;
  approveReview: (reviewId: string, request: ReviewApprovalRequest) => Promise<ReviewApprovalResponse>;
  rejectReview: (reviewId: string, reason: string) => Promise<void>;
}

export function useReviewApproval(): UseReviewApprovalReturn {
  const [pendingReviews, setPendingReviews] = useState<PendingReview[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPendingReviews = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/peer-reviews/pending-approval', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('Access denied: Editor role required');
        }
        throw new Error('Failed to fetch pending reviews');
      }

      const data = await response.json();
      setPendingReviews(data.pendingReviews || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  const approveReview = useCallback(
    async (reviewId: string, request: ReviewApprovalRequest): Promise<ReviewApprovalResponse> => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/v1/peer-reviews/${reviewId}/approve`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(request)
        });

        if (!response.ok) {
          throw new Error('Failed to approve review');
        }

        const data = await response.json();

        // Remove the approved review from pending list
        setPendingReviews(prev => prev.filter(r => r.reviewId !== reviewId));

        return data;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const rejectReview = useCallback(
    async (reviewId: string, reason: string) => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/v1/peer-reviews/${reviewId}/reject`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            approved: false,
            eligibleForPayout: false,
            approvalNotes: reason
          })
        });

        if (!response.ok) {
          throw new Error('Failed to reject review');
        }

        // Remove the rejected review from pending list
        setPendingReviews(prev => prev.filter(r => r.reviewId !== reviewId));
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    pendingReviews,
    loading,
    error,
    fetchPendingReviews,
    approveReview,
    rejectReview
  };
}
