import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/router';
import Layout from '@/components/layout/Layout';
import SubscriptionCard from '@/components/payment/SubscriptionCard';
import { useSubscription } from '@/hooks/useSubscription';
import { usePayouts } from '@/hooks/usePayouts';
import { useAppStore } from '@/stores/useAppStore';
import {
  DollarSign,
  TrendingUp,
  Calendar,
  CheckCircle2,
  Clock,
  Award,
  CreditCard,
  Download,
  ExternalLink,
  Sparkles
} from 'lucide-react';

const EarningsPage: React.FC = () => {
  const router = useRouter();
  const { user } = useAppStore();
  const { subscription, loading: subLoading, fetchSubscription, cancelSubscription } = useSubscription();
  const { earnings, loading: earningsLoading, fetchEarnings } = usePayouts();

  // Fetch data on mount
  useEffect(() => {
    if (user) {
      fetchSubscription();
      fetchEarnings();
    }
  }, [user]);

  const loading = subLoading || earningsLoading;

  if (loading && !earnings) {
    return (
      <Layout title="My Earnings">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="My Earnings">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Hero Section */}
        <motion.div
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-green-600 via-green-700 to-emerald-800 p-8 md:p-12 text-white"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          <motion.div
            className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3]
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
          />

          <div className="relative z-10">
            <div className="flex items-start justify-between flex-wrap gap-6">
              <div className="flex-1 min-w-0">
                <motion.div
                  className="inline-flex items-center gap-3 mb-4"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                >
                  <div className="p-3 rounded-2xl bg-white/20 backdrop-blur-sm">
                    <DollarSign className="w-8 h-8" />
                  </div>
                  <div>
                    <h1 className="text-4xl md:text-5xl font-bold">
                      My Earnings
                    </h1>
                    <div className="flex items-center gap-2 mt-1">
                      <Sparkles className="w-4 h-4 text-green-200" />
                      <span className="text-sm text-green-100 font-medium">
                        Review Payouts & Subscription
                      </span>
                    </div>
                  </div>
                </motion.div>

                <motion.p
                  className="text-lg text-green-100 max-w-2xl leading-relaxed"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  Track your review earnings, manage your subscription, and view payout history
                </motion.p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Earnings Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <motion.div
            className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-xl bg-green-100 text-green-600">
                <DollarSign className="w-5 h-5" />
              </div>
              <span className="text-sm text-gray-600">Lifetime Earnings</span>
            </div>
            <div className="text-3xl font-bold text-green-600">
              ${earnings?.lifetimeEarnings.toFixed(2) || '0.00'}
            </div>
          </motion.div>

          <motion.div
            className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-xl bg-blue-100 text-blue-600">
                <TrendingUp className="w-5 h-5" />
              </div>
              <span className="text-sm text-gray-600">This Month</span>
            </div>
            <div className="text-3xl font-bold text-blue-600">
              ${earnings?.currentMonthPending.toFixed(2) || '0.00'}
            </div>
            <p className="text-xs text-gray-500 mt-1">Pending approval</p>
          </motion.div>

          <motion.div
            className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-xl bg-purple-100 text-purple-600">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <span className="text-sm text-gray-600">Reviews Approved</span>
            </div>
            <div className="text-3xl font-bold text-purple-600">
              {earnings?.currentMonthReviews.approved || 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              ${earnings?.currentMonthReviews.estimatedPayout.toFixed(2) || '0.00'} estimated
            </p>
          </motion.div>

          <motion.div
            className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-xl bg-yellow-100 text-yellow-600">
                <Clock className="w-5 h-5" />
              </div>
              <span className="text-sm text-gray-600">Next Payout</span>
            </div>
            <div className="text-lg font-bold text-gray-900">
              {new Date(new Date().getFullYear(), new Date().getMonth() + 1, 1).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric'
              })}
            </div>
            <p className="text-xs text-gray-500 mt-1">1st of next month</p>
          </motion.div>
        </div>

        {/* Current Month Activity */}
        {earnings && (
          <motion.div
            className="p-6 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              Current Month Activity
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-white/60 backdrop-blur-sm">
                <div className="text-2xl font-bold text-blue-600">
                  {earnings.currentMonthReviews.assigned}
                </div>
                <p className="text-sm text-gray-600">Assigned</p>
              </div>
              <div className="p-4 rounded-xl bg-white/60 backdrop-blur-sm">
                <div className="text-2xl font-bold text-purple-600">
                  {earnings.currentMonthReviews.completed}
                </div>
                <p className="text-sm text-gray-600">Completed</p>
              </div>
              <div className="p-4 rounded-xl bg-white/60 backdrop-blur-sm">
                <div className="text-2xl font-bold text-green-600">
                  {earnings.currentMonthReviews.approved}
                </div>
                <p className="text-sm text-gray-600">Approved</p>
              </div>
              <div className="p-4 rounded-xl bg-white/60 backdrop-blur-sm">
                <div className="text-2xl font-bold text-orange-600">
                  {earnings.currentMonthReviews.pendingApproval}
                </div>
                <p className="text-sm text-gray-600">Pending</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Subscription Card */}
        {subscription && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              Subscription
            </h3>
            <SubscriptionCard
              subscription={subscription}
              onCancel={cancelSubscription}
              onUpdatePayment={() => {
                // TODO: Implement Stripe payment update flow
                alert('Payment update coming soon!');
              }}
            />
          </motion.div>
        )}

        {/* Payout History */}
        {earnings && earnings.earningsHistory.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900">
                Payout History
              </h3>
              <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-colors">
                <Download className="w-4 h-4" />
                Export CSV
              </button>
            </div>
            <div className="rounded-2xl border-2 border-gray-200 overflow-hidden bg-white">
              <table className="w-full">
                <thead className="bg-gray-50 border-b-2 border-gray-200">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        Month
                      </div>
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                      Reviews
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                      Amount
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {earnings.earningsHistory.map((item, index) => (
                    <motion.tr
                      key={index}
                      className="hover:bg-gray-50 transition-colors"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">
                        {new Date(item.month).toLocaleDateString('en-US', {
                          month: 'long',
                          year: 'numeric'
                        })}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700">
                        {item.reviewsApproved} approved
                      </td>
                      <td className="px-6 py-4 text-sm font-bold text-green-600">
                        ${item.payoutAmount.toFixed(2)}
                      </td>
                      <td className="px-6 py-4">
                        <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${
                          item.status === 'completed'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {item.status === 'completed' ? (
                            <CheckCircle2 className="w-3 h-3" />
                          ) : (
                            <Clock className="w-3 h-3" />
                          )}
                          {item.status}
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {/* Stripe Connect Setup (if not connected) */}
        {!subscription && (
          <motion.div
            className="p-8 rounded-2xl bg-gradient-to-br from-orange-50 to-red-50 border-2 border-orange-200 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-orange-100 text-orange-600 mb-4">
              <CreditCard className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Connect Bank Account
            </h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Set up your bank account to receive review payouts via Stripe Connect
            </p>
            <motion.button
              className="px-6 py-3 bg-orange-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => {
                // TODO: Implement Stripe Connect onboarding
                alert('Stripe Connect setup coming soon!');
              }}
            >
              <span className="flex items-center gap-2">
                <ExternalLink className="w-5 h-5" />
                Connect with Stripe
              </span>
            </motion.button>
          </motion.div>
        )}
      </div>
    </Layout>
  );
};

export default EarningsPage;
