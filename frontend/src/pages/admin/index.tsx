import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/router';
import Layout from '@/components/layout/Layout';
import PayoutPoolCard from '@/components/payment/PayoutPoolCard';
import ReviewerTable from '@/components/payment/ReviewerTable';
import { useAdminDashboard } from '@/hooks/useAdminDashboard';
import { usePayouts } from '@/hooks/usePayouts';
import { canAccessAdmin } from '@/lib/rbac';
import { useAppStore } from '@/stores/useAppStore';
import {
  DollarSign,
  Users,
  TrendingUp,
  FileText,
  Award,
  Activity,
  Calendar,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

const AdminDashboardPage: React.FC = () => {
  const router = useRouter();
  const { user } = useAppStore();
  const { dashboardData, researchers, payoutHistory, loading, error, fetchDashboard, fetchResearchers, fetchPayoutHistory } = useAdminDashboard();
  const { currentPool, fetchCurrentPool } = usePayouts();
  const [selectedTab, setSelectedTab] = useState<'overview' | 'researchers' | 'payouts'>('overview');

  // Check access
  useEffect(() => {
    if (!canAccessAdmin(user)) {
      router.push('/dashboard-new');
    }
  }, [user, router]);

  // Fetch data on mount
  useEffect(() => {
    if (canAccessAdmin(user)) {
      fetchDashboard();
      fetchResearchers({ pageSize: 50 });
      fetchPayoutHistory();
      fetchCurrentPool();
    }
  }, [user]);

  if (!canAccessAdmin(user)) {
    return null;
  }

  if (loading && !dashboardData) {
    return (
      <Layout title="Admin Dashboard">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout title="Admin Dashboard">
        <div className="p-6 rounded-2xl bg-red-50 border border-red-200">
          <p className="text-red-700">{error}</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Admin Dashboard">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Hero Section */}
        <motion.div
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-red-600 via-red-700 to-orange-700 p-8 md:p-12 text-white"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          {/* Animated background */}
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
                    <Activity className="w-8 h-8" />
                  </div>
                  <div>
                    <h1 className="text-4xl md:text-5xl font-bold">
                      Admin Dashboard
                    </h1>
                    <p className="text-sm text-red-100 font-medium mt-1">
                      Platform Overview & Management
                    </p>
                  </div>
                </motion.div>

                <motion.p
                  className="text-lg text-red-100 max-w-2xl leading-relaxed"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  Monitor platform metrics, manage researcher pool, and oversee payout distributions
                </motion.p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Platform Metrics */}
        {dashboardData && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <motion.div
              className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-xl bg-blue-100 text-blue-600">
                  <Users className="w-5 h-5" />
                </div>
                <span className="text-sm text-gray-600">Active Subs</span>
              </div>
              <div className="text-3xl font-bold text-gray-900">
                {dashboardData.platformMetrics.totalActiveSubscriptions}
              </div>
            </motion.div>

            <motion.div
              className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-xl bg-green-100 text-green-600">
                  <DollarSign className="w-5 h-5" />
                </div>
                <span className="text-sm text-gray-600">Monthly MRR</span>
              </div>
              <div className="text-3xl font-bold text-green-600">
                ${dashboardData.platformMetrics.monthlyRecurringRevenue.toLocaleString()}
              </div>
            </motion.div>

            <motion.div
              className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-xl bg-orange-100 text-orange-600">
                  <TrendingUp className="w-5 h-5" />
                </div>
                <span className="text-sm text-gray-600">Payout Pool</span>
              </div>
              <div className="text-3xl font-bold text-orange-600">
                ${dashboardData.platformMetrics.monthlyPayoutObligations.toFixed(0)}
              </div>
            </motion.div>

            <motion.div
              className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-xl bg-purple-100 text-purple-600">
                  <Award className="w-5 h-5" />
                </div>
                <span className="text-sm text-gray-600">Net Profit</span>
              </div>
              <div className="text-3xl font-bold text-purple-600">
                ${dashboardData.platformMetrics.netMonthlyProfit.toLocaleString()}
              </div>
            </motion.div>

            <motion.div
              className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-xl bg-red-100 text-red-600">
                  <Users className="w-5 h-5" />
                </div>
                <span className="text-sm text-gray-600">Researchers</span>
              </div>
              <div className="text-3xl font-bold text-gray-900">
                {dashboardData.researcherPool.totalResearchers}
              </div>
            </motion.div>
          </div>
        )}

        {/* Current Month Pool */}
        {currentPool && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Current Month Payout Pool
            </h2>
            <PayoutPoolCard
              pool={currentPool}
              showActions={true}
              onDistribute={() => {
                // TODO: Implement distribute payouts
                alert('Distribute payouts functionality coming soon!');
              }}
            />
          </motion.div>
        )}

        {/* Tabs */}
        <div>
          <div className="flex gap-2 mb-6 border-b border-gray-200">
            {['overview', 'researchers', 'payouts'].map((tab) => (
              <button
                key={tab}
                className={`px-6 py-3 font-semibold transition-colors border-b-2 ${
                  selectedTab === tab
                    ? 'border-red-600 text-red-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
                onClick={() => setSelectedTab(tab as any)}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {selectedTab === 'overview' && dashboardData && (
            <div className="space-y-6">
              {/* Recent Activity */}
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  Recent Activity
                </h3>
                <div className="space-y-3">
                  {dashboardData.recentActivity.slice(0, 10).map((activity, index) => (
                    <motion.div
                      key={index}
                      className="p-4 rounded-xl bg-white border border-gray-200 flex items-start gap-4"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <div className="p-2 rounded-lg bg-blue-100 text-blue-600">
                        <Activity className="w-4 h-4" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-gray-900">{activity.description}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(activity.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {selectedTab === 'researchers' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900">
                  Researcher Pool ({researchers.length})
                </h3>
              </div>
              <ReviewerTable
                researchers={researchers}
                onResearcherClick={(researcher) => {
                  console.log('View researcher:', researcher);
                }}
              />
            </div>
          )}

          {selectedTab === 'payouts' && (
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                Payout History
              </h3>
              <div className="rounded-2xl border-2 border-gray-200 overflow-hidden bg-white">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b-2 border-gray-200">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                        Month
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                        Pool Size
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                        Reviews Paid
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                        Avg Payout
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {payoutHistory.map((item, index) => (
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
                        <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                          ${item.totalPool.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-700">
                          {item.reviewsApproved}
                        </td>
                        <td className="px-6 py-4 text-sm font-semibold text-green-600">
                          ${item.payoutPerReview.toFixed(2)}
                        </td>
                        <td className="px-6 py-4">
                          <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${
                            item.status === 'completed'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-gray-100 text-gray-700'
                          }`}>
                            {item.status === 'completed' ? (
                              <CheckCircle2 className="w-3 h-3" />
                            ) : (
                              <AlertCircle className="w-3 h-3" />
                            )}
                            {item.status}
                          </div>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default AdminDashboardPage;
