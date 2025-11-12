import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  DollarSign,
  TrendingUp,
  Users,
  CheckCircle2,
  AlertCircle,
  Calendar,
  PlayCircle,
  Eye,
  Loader2,
  XCircle,
  Clock
} from 'lucide-react';
import { PayoutPool } from '@/lib/payment-types';
import { Button } from '../shared/Button';

interface PayoutPoolManagerProps {
  currentPool: PayoutPool | null;
  poolHistory?: PayoutPool[];
  onDistribute: (poolId: string, dryRun: boolean) => Promise<any>;
  onCreatePool?: () => void;
  loading?: boolean;
}

interface DistributionPreview {
  poolId: string;
  totalAmount: number;
  reviewersCount: number;
  payoutPerReview: number;
  distributions: Array<{
    reviewerId: string;
    reviewerName: string;
    reviewsCount: number;
    amount: number;
  }>;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'open':
      return 'bg-blue-100 text-blue-700 border-blue-300';
    case 'calculating':
      return 'bg-yellow-100 text-yellow-700 border-yellow-300';
    case 'distributed':
      return 'bg-green-100 text-green-700 border-green-300';
    case 'closed':
      return 'bg-gray-100 text-gray-700 border-gray-300';
    default:
      return 'bg-gray-100 text-gray-700 border-gray-300';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'open':
      return <Clock className="w-4 h-4" />;
    case 'calculating':
      return <Loader2 className="w-4 h-4 animate-spin" />;
    case 'distributed':
      return <CheckCircle2 className="w-4 h-4" />;
    case 'closed':
      return <XCircle className="w-4 h-4" />;
    default:
      return <AlertCircle className="w-4 h-4" />;
  }
};

export const PayoutPoolManager: React.FC<PayoutPoolManagerProps> = ({
  currentPool,
  poolHistory = [],
  onDistribute,
  onCreatePool,
  loading = false
}) => {
  const [showPreview, setShowPreview] = useState(false);
  const [preview, setPreview] = useState<DistributionPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [distributingPool, setDistributingPool] = useState<string | null>(null);

  const handlePreview = async (poolId: string) => {
    setPreviewLoading(true);
    try {
      const result = await onDistribute(poolId, true); // dry run
      setPreview(result);
      setShowPreview(true);
    } catch (error) {
      console.error('Failed to preview distribution:', error);
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleDistribute = async (poolId: string) => {
    setDistributingPool(poolId);
    try {
      await onDistribute(poolId, false);
      setShowConfirmation(false);
      setShowPreview(false);
      setPreview(null);
    } catch (error) {
      console.error('Failed to distribute payouts:', error);
    } finally {
      setDistributingPool(null);
    }
  };

  const completionRate = currentPool
    ? (currentPool.totalReviewsCompleted / Math.max(currentPool.totalReviewsAssigned, 1)) * 100
    : 0;

  const approvalRate = currentPool
    ? (currentPool.totalReviewsApproved / Math.max(currentPool.totalReviewsCompleted, 1)) * 100
    : 0;

  return (
    <div className="space-y-6">
      {/* Current Pool Status */}
      {currentPool && (
        <motion.div
          className="rounded-2xl bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 border-2 border-blue-200 p-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-start justify-between mb-6">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-3 rounded-xl bg-blue-600 text-white">
                  <DollarSign className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    Current Payout Pool
                  </h2>
                  <p className="text-sm text-gray-600">
                    {new Date(currentPool.poolMonth).toLocaleDateString('en-US', {
                      month: 'long',
                      year: 'numeric'
                    })}
                  </p>
                </div>
              </div>
            </div>
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border-2 font-semibold ${getStatusColor(currentPool.status)}`}>
              {getStatusIcon(currentPool.status)}
              {currentPool.status.toUpperCase()}
            </div>
          </div>

          {/* Pool Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-xl p-4 border-2 border-blue-200">
              <p className="text-xs text-gray-600 mb-1">Total Contributions</p>
              <p className="text-2xl font-bold text-blue-600">
                ${currentPool.totalContributions.toLocaleString()}
              </p>
            </div>
            <div className="bg-white rounded-xl p-4 border-2 border-green-200">
              <p className="text-xs text-gray-600 mb-1">Distributed</p>
              <p className="text-2xl font-bold text-green-600">
                ${currentPool.totalDistributed.toLocaleString()}
              </p>
            </div>
            <div className="bg-white rounded-xl p-4 border-2 border-purple-200">
              <p className="text-xs text-gray-600 mb-1">Remaining</p>
              <p className="text-2xl font-bold text-purple-600">
                ${currentPool.remaining.toLocaleString()}
              </p>
            </div>
            <div className="bg-white rounded-xl p-4 border-2 border-orange-200">
              <p className="text-xs text-gray-600 mb-1">Per Review</p>
              <p className="text-2xl font-bold text-orange-600">
                ${currentPool.payoutPerReview?.toFixed(2) || '0.00'}
              </p>
            </div>
          </div>

          {/* Progress Bars */}
          <div className="space-y-4 mb-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Review Completion
                </span>
                <span className="text-sm font-semibold text-gray-900">
                  {currentPool.totalReviewsCompleted} / {currentPool.totalReviewsAssigned}
                </span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                  initial={{ width: 0 }}
                  animate={{ width: `${completionRate}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                />
              </div>
              <p className="text-xs text-gray-600 mt-1">{completionRate.toFixed(1)}% complete</p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Review Approval
                </span>
                <span className="text-sm font-semibold text-gray-900">
                  {currentPool.totalReviewsApproved} / {currentPool.totalReviewsCompleted}
                </span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-green-500 to-green-600"
                  initial={{ width: 0 }}
                  animate={{ width: `${approvalRate}%` }}
                  transition={{ duration: 1, ease: 'easeOut', delay: 0.2 }}
                />
              </div>
              <p className="text-xs text-gray-600 mt-1">{approvalRate.toFixed(1)}% approved</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              variant="outline"
              icon={<Eye className="w-4 h-4" />}
              onClick={() => handlePreview(currentPool.id)}
              loading={previewLoading}
              disabled={currentPool.status !== 'open' || loading}
            >
              Preview Distribution
            </Button>
            <Button
              variant="primary"
              icon={<PlayCircle className="w-4 h-4" />}
              onClick={() => setShowConfirmation(true)}
              disabled={currentPool.status !== 'open' || loading || currentPool.totalReviewsApproved === 0}
            >
              Distribute Payouts
            </Button>
            {onCreatePool && (
              <Button
                variant="secondary"
                icon={<Calendar className="w-4 h-4" />}
                onClick={onCreatePool}
                disabled={loading}
              >
                Create New Pool
              </Button>
            )}
          </div>
        </motion.div>
      )}

      {/* Pool History */}
      {poolHistory.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            Pool History
          </h3>
          <div className="rounded-2xl border-2 border-gray-200 overflow-hidden bg-white">
            <table className="w-full">
              <thead className="bg-gray-50 border-b-2 border-gray-200">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                    Month
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                    Contributions
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                    Distributed
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                    Reviews
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                    Per Review
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {poolHistory.map((pool, index) => (
                  <motion.tr
                    key={pool.id}
                    className="hover:bg-gray-50 transition-colors"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {new Date(pool.poolMonth).toLocaleDateString('en-US', {
                        month: 'long',
                        year: 'numeric'
                      })}
                    </td>
                    <td className="px-6 py-4 text-sm font-semibold text-blue-600">
                      ${pool.totalContributions.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-sm font-semibold text-green-600">
                      ${pool.totalDistributed.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      {pool.totalReviewsApproved}
                    </td>
                    <td className="px-6 py-4 text-sm font-semibold text-orange-600">
                      ${pool.payoutPerReview?.toFixed(2) || '0.00'}
                    </td>
                    <td className="px-6 py-4">
                      <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(pool.status)}`}>
                        {getStatusIcon(pool.status)}
                        {pool.status}
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Distribution Preview Modal */}
      <AnimatePresence>
        {showPreview && preview && (
          <motion.div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowPreview(false)}
          >
            <motion.div
              className="bg-white rounded-2xl p-6 max-w-4xl w-full max-h-[80vh] overflow-auto"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Distribution Preview
              </h3>

              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                  <p className="text-sm text-gray-600 mb-1">Total Amount</p>
                  <p className="text-2xl font-bold text-blue-600">
                    ${preview.totalAmount.toLocaleString()}
                  </p>
                </div>
                <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
                  <p className="text-sm text-gray-600 mb-1">Reviewers</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {preview.reviewersCount}
                  </p>
                </div>
                <div className="bg-orange-50 rounded-xl p-4 border border-orange-200">
                  <p className="text-sm text-gray-600 mb-1">Per Review</p>
                  <p className="text-2xl font-bold text-orange-600">
                    ${preview.payoutPerReview.toFixed(2)}
                  </p>
                </div>
              </div>

              <div className="max-h-96 overflow-y-auto mb-6">
                <table className="w-full">
                  <thead className="bg-gray-50 sticky top-0">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">
                        Reviewer
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">
                        Reviews
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">
                        Amount
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {preview.distributions.map((dist) => (
                      <tr key={dist.reviewerId}>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {dist.reviewerName}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-700">
                          {dist.reviewsCount}
                        </td>
                        <td className="px-4 py-3 text-sm font-semibold text-green-600">
                          ${dist.amount.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setShowPreview(false)}>
                  Close
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Confirmation Modal */}
      <AnimatePresence>
        {showConfirmation && currentPool && (
          <motion.div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowConfirmation(false)}
          >
            <motion.div
              className="bg-white rounded-2xl p-6 max-w-md w-full"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 rounded-xl bg-orange-100 text-orange-600">
                  <AlertCircle className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold text-gray-900">
                  Confirm Distribution
                </h3>
              </div>

              <p className="text-gray-700 mb-6">
                Are you sure you want to distribute payouts for {new Date(currentPool.poolMonth).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}?
                This will process ${currentPool.remaining.toFixed(2)} to {currentPool.totalReviewsApproved} approved reviews.
              </p>

              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6">
                <p className="text-sm text-yellow-800">
                  <strong>Warning:</strong> This action cannot be undone. Payments will be initiated immediately.
                </p>
              </div>

              <div className="flex justify-end gap-3">
                <Button
                  variant="outline"
                  onClick={() => setShowConfirmation(false)}
                  disabled={distributingPool !== null}
                >
                  Cancel
                </Button>
                <Button
                  variant="danger"
                  onClick={() => handleDistribute(currentPool.id)}
                  loading={distributingPool === currentPool.id}
                  icon={<PlayCircle className="w-4 h-4" />}
                >
                  Confirm Distribution
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PayoutPoolManager;
