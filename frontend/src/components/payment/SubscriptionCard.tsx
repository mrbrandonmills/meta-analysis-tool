import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  CreditCard,
  Calendar,
  DollarSign,
  CheckCircle2,
  AlertCircle,
  X,
  ExternalLink
} from 'lucide-react';
import { Subscription } from '@/lib/payment-types';

interface SubscriptionCardProps {
  subscription: Subscription;
  onCancel?: (reason: string) => void;
  onUpdatePayment?: () => void;
}

export const SubscriptionCard: React.FC<SubscriptionCardProps> = ({
  subscription,
  onCancel,
  onUpdatePayment
}) => {
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCancelSubmit = async () => {
    if (!cancelReason.trim() || !onCancel) return;
    setIsSubmitting(true);
    try {
      await onCancel(cancelReason);
      setShowCancelModal(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const statusColors = {
    active: 'bg-green-100 text-green-700 border-green-200',
    past_due: 'bg-red-100 text-red-700 border-red-200',
    canceled: 'bg-gray-100 text-gray-700 border-gray-200',
    unpaid: 'bg-orange-100 text-orange-700 border-orange-200'
  };

  const statusIcons = {
    active: CheckCircle2,
    past_due: AlertCircle,
    canceled: X,
    unpaid: AlertCircle
  };

  const StatusIcon = statusIcons[subscription.status];

  return (
    <>
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
              <div className="p-2.5 rounded-xl bg-blue-100 text-blue-600">
                <CreditCard className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Subscription
                </h3>
                <p className="text-sm text-gray-500">{subscription.planType}</p>
              </div>
            </div>
          </div>
          <div className={`px-3 py-1.5 rounded-full text-xs font-medium border ${statusColors[subscription.status]}`}>
            <div className="flex items-center gap-1.5">
              <StatusIcon className="w-3.5 h-3.5" />
              {subscription.status.replace('_', ' ').toUpperCase()}
            </div>
          </div>
        </div>

        {/* Subscription Details */}
        <div className="space-y-4 mb-6">
          {/* Monthly Amount */}
          <div className="flex items-center justify-between p-4 rounded-xl bg-gray-50">
            <div className="flex items-center gap-3">
              <DollarSign className="w-5 h-5 text-gray-600" />
              <div>
                <p className="text-sm text-gray-600">Monthly Amount</p>
                <p className="text-lg font-bold text-gray-900">
                  ${subscription.monthlyAmount.toFixed(2)}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">Platform Fee</p>
              <p className="text-sm font-semibold text-gray-700">
                ${(subscription.monthlyAmount - subscription.payoutContribution).toFixed(2)}
              </p>
            </div>
          </div>

          {/* Payout Contribution */}
          <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-100 text-green-600">
                <DollarSign className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm text-green-700 font-medium">
                  Payout Pool Contribution
                </p>
                <p className="text-lg font-bold text-green-600">
                  ${subscription.payoutContribution.toFixed(2)}
                </p>
              </div>
            </div>
            <div className="text-xs text-green-600 max-w-[120px] text-right">
              Shared among reviewers
            </div>
          </div>

          {/* Billing Cycle */}
          <div className="flex items-center justify-between p-4 rounded-xl bg-gray-50">
            <div className="flex items-center gap-3">
              <Calendar className="w-5 h-5 text-gray-600" />
              <div>
                <p className="text-sm text-gray-600">Next Billing Date</p>
                <p className="text-base font-semibold text-gray-900">
                  {new Date(subscription.currentPeriodEnd).toLocaleDateString('en-US', {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric'
                  })}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Cancel Warning */}
        {subscription.cancelAtPeriodEnd && (
          <div className="p-4 rounded-xl bg-orange-50 border border-orange-200 mb-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-orange-900">
                  Subscription will cancel
                </p>
                <p className="text-xs text-orange-700 mt-1">
                  Your subscription will end on{' '}
                  {new Date(subscription.currentPeriodEnd).toLocaleDateString('en-US', {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric'
                  })}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          {onUpdatePayment && subscription.status === 'active' && (
            <motion.button
              className="flex-1 py-2.5 px-4 rounded-xl bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-colors duration-200"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onUpdatePayment}
            >
              <span className="flex items-center justify-center gap-2">
                <CreditCard className="w-4 h-4" />
                Update Payment
              </span>
            </motion.button>
          )}
          {onCancel && subscription.status === 'active' && !subscription.cancelAtPeriodEnd && (
            <motion.button
              className="flex-1 py-2.5 px-4 rounded-xl bg-red-100 text-red-700 font-medium hover:bg-red-200 transition-colors duration-200"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowCancelModal(true)}
            >
              Cancel Subscription
            </motion.button>
          )}
        </div>

        {/* Stripe Portal Link */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <a
            href={`https://billing.stripe.com/p/login/${subscription.stripeCustomerId}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 text-sm text-blue-600 hover:text-blue-700 transition-colors"
          >
            <span>Manage via Stripe</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </motion.div>

      {/* Cancel Modal */}
      {showCancelModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6"
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 rounded-xl bg-red-100 text-red-600">
                <AlertCircle className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-1">
                  Cancel Subscription?
                </h3>
                <p className="text-sm text-gray-600">
                  Your subscription will remain active until the end of your billing period.
                </p>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Please tell us why you're canceling (optional)
              </label>
              <textarea
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all resize-none"
                rows={4}
                placeholder="Your feedback helps us improve..."
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
              />
            </div>

            <div className="flex gap-3">
              <button
                className="flex-1 py-2.5 px-4 rounded-xl bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-colors disabled:opacity-50"
                onClick={() => setShowCancelModal(false)}
                disabled={isSubmitting}
              >
                Keep Subscription
              </button>
              <button
                className="flex-1 py-2.5 px-4 rounded-xl bg-red-600 text-white font-medium hover:bg-red-700 transition-colors disabled:opacity-50"
                onClick={handleCancelSubmit}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Canceling...' : 'Confirm Cancel'}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </>
  );
};

export default SubscriptionCard;
