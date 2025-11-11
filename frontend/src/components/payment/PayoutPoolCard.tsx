import React from 'react';
import { motion } from 'framer-motion';
import { DollarSign, TrendingUp, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { PayoutPool } from '@/lib/payment-types';

interface PayoutPoolCardProps {
  pool: PayoutPool;
  showActions?: boolean;
  onDistribute?: () => void;
}

export const PayoutPoolCard: React.FC<PayoutPoolCardProps> = ({
  pool,
  showActions = false,
  onDistribute
}) => {
  const completionRate = pool.totalReviewsAssigned > 0
    ? (pool.totalReviewsCompleted / pool.totalReviewsAssigned) * 100
    : 0;

  const approvalRate = pool.totalReviewsCompleted > 0
    ? (pool.totalReviewsApproved / pool.totalReviewsCompleted) * 100
    : 0;

  const statusColors = {
    open: 'bg-green-100 text-green-700 border-green-200',
    calculating: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    distributed: 'bg-blue-100 text-blue-700 border-blue-200',
    closed: 'bg-gray-100 text-gray-700 border-gray-200'
  };

  const statusIcons = {
    open: Clock,
    calculating: TrendingUp,
    distributed: CheckCircle2,
    closed: AlertCircle
  };

  const StatusIcon = statusIcons[pool.status];

  return (
    <motion.div
      className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2.5 rounded-xl bg-green-100 text-green-600">
              <DollarSign className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {new Date(pool.poolMonth).toLocaleDateString('en-US', {
                  month: 'long',
                  year: 'numeric'
                })} Pool
              </h3>
              <p className="text-sm text-gray-500">Payout Pool</p>
            </div>
          </div>
        </div>
        <div className={`px-3 py-1.5 rounded-full text-xs font-medium border ${statusColors[pool.status]}`}>
          <div className="flex items-center gap-1.5">
            <StatusIcon className="w-3.5 h-3.5" />
            {pool.status.replace('_', ' ').toUpperCase()}
          </div>
        </div>
      </div>

      {/* Pool Amount */}
      <div className="mb-6">
        <div className="text-3xl font-bold text-gray-900 mb-1">
          ${pool.totalContributions.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
        <p className="text-sm text-gray-600">Total Pool Amount</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="p-3 rounded-xl bg-gray-50">
          <div className="text-2xl font-bold text-gray-900">
            {pool.totalReviewsAssigned}
          </div>
          <p className="text-xs text-gray-600">Reviews Assigned</p>
        </div>
        <div className="p-3 rounded-xl bg-gray-50">
          <div className="text-2xl font-bold text-gray-900">
            {pool.totalReviewsCompleted}
          </div>
          <p className="text-xs text-gray-600">Completed</p>
        </div>
        <div className="p-3 rounded-xl bg-gray-50">
          <div className="text-2xl font-bold text-green-600">
            {pool.totalReviewsApproved}
          </div>
          <p className="text-xs text-gray-600">Approved</p>
        </div>
        <div className="p-3 rounded-xl bg-gray-50">
          <div className="text-2xl font-bold text-blue-600">
            {pool.payoutPerReview
              ? `$${pool.payoutPerReview.toFixed(2)}`
              : '--'}
          </div>
          <p className="text-xs text-gray-600">Per Review</p>
        </div>
      </div>

      {/* Progress Bars */}
      <div className="space-y-4 mb-6">
        <div>
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-gray-600">Completion Rate</span>
            <span className="font-semibold text-gray-900">
              {completionRate.toFixed(1)}%
            </span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
              initial={{ width: 0 }}
              animate={{ width: `${completionRate}%` }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
            />
          </div>
        </div>
        <div>
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-gray-600">Approval Rate</span>
            <span className="font-semibold text-gray-900">
              {approvalRate.toFixed(1)}%
            </span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-green-500 to-green-600"
              initial={{ width: 0 }}
              animate={{ width: `${approvalRate}%` }}
              transition={{ duration: 0.6, ease: 'easeOut', delay: 0.1 }}
            />
          </div>
        </div>
      </div>

      {/* Estimated Payout */}
      {pool.status === 'open' && pool.totalReviewsApproved > 0 && (
        <div className="p-4 rounded-xl bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 mb-4">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-4 h-4 text-green-600" />
            <span className="text-sm font-medium text-green-900">
              Projected Payout per Review
            </span>
          </div>
          <div className="text-2xl font-bold text-green-600">
            ${(pool.totalContributions / pool.totalReviewsApproved).toFixed(2)}
          </div>
          <p className="text-xs text-green-700 mt-1">
            Based on {pool.totalReviewsApproved} approved reviews
          </p>
        </div>
      )}

      {/* Action Button */}
      {showActions && pool.status === 'open' && pool.totalReviewsApproved > 0 && (
        <motion.button
          className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-green-600 to-emerald-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
          onClick={onDistribute}
        >
          Close Pool & Distribute Payouts
        </motion.button>
      )}

      {pool.status === 'distributed' && pool.distributedAt && (
        <div className="text-sm text-gray-600 text-center">
          Distributed on {new Date(pool.distributedAt).toLocaleDateString('en-US', {
            month: 'long',
            day: 'numeric',
            year: 'numeric'
          })}
        </div>
      )}
    </motion.div>
  );
};

export default PayoutPoolCard;
