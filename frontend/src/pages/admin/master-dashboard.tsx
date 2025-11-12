import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/router';
import Layout from '@/components/layout/Layout';
import MasterDashboardOverview from '@/components/admin/MasterDashboardOverview';
import PayoutPoolManager from '@/components/admin/PayoutPoolManager';
import RevenueChart from '@/components/admin/RevenueChart';
import ActivityFeed from '@/components/admin/ActivityFeed';
import EnhancedResearcherTable from '@/components/admin/EnhancedResearcherTable';
import { useAdminDashboard } from '@/hooks/useAdminDashboard';
import { usePayouts } from '@/hooks/usePayouts';
import { canAccessAdmin } from '@/lib/rbac';
import { useAppStore } from '@/stores/useAppStore';
import {
  Activity,
  Users,
  DollarSign,
  TrendingUp,
  BarChart3,
  Settings,
  FileText
} from 'lucide-react';
import toast from 'react-hot-toast';

type TabType = 'overview' | 'researchers' | 'payouts' | 'analytics' | 'activity' | 'financial';

const MasterAdminDashboardPage: React.FC = () => {
  const router = useRouter();
  const { user } = useAppStore();
  const {
    dashboardData,
    researchers,
    payoutHistory,
    loading,
    error,
    fetchDashboard,
    fetchResearchers,
    fetchPayoutHistory,
    distributePayouts
  } = useAdminDashboard();
  const { currentPool, poolHistory, fetchCurrentPool, fetchPoolHistory } = usePayouts();
  const [selectedTab, setSelectedTab] = useState<TabType>('overview');
  const [refreshKey, setRefreshKey] = useState(0);

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
      fetchResearchers({ pageSize: 100 });
      fetchPayoutHistory();
      fetchCurrentPool();
      fetchPoolHistory();
    }
  }, [user, refreshKey]);

  // Handle refresh
  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
    toast.success('Dashboard refreshed');
  };

  // Handle payout distribution
  const handleDistribute = async (poolId: string, dryRun: boolean) => {
    try {
      const result = await distributePayouts(poolId, dryRun);
      if (!dryRun) {
        toast.success('Payouts distributed successfully');
        handleRefresh();
      }
      return result;
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to distribute payouts');
      throw err;
    }
  };

  // Handle researcher actions
  const handleResearcherClick = (researcher: any) => {
    toast.success(`Viewing profile for ${researcher.name}`);
    // TODO: Navigate to researcher detail page
  };

  const handleSuspendAccount = (researcherId: string) => {
    toast.success(`Account suspended: ${researcherId}`);
    // TODO: Implement suspend account API call
  };

  const handleViewActivity = (researcherId: string) => {
    toast.success(`Viewing activity for: ${researcherId}`);
    // TODO: Navigate to researcher activity page
  };

  if (!canAccessAdmin(user)) {
    return null;
  }

  if (loading && !dashboardData) {
    return (
      <Layout title="Master Admin Dashboard">
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-red-600 mx-auto mb-4"></div>
            <p className="text-gray-600 font-medium">Loading dashboard...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout title="Master Admin Dashboard">
        <div className="max-w-7xl mx-auto">
          <div className="p-6 rounded-2xl bg-red-50 border-2 border-red-200">
            <div className="flex items-center gap-3">
              <Activity className="w-6 h-6 text-red-600" />
              <div>
                <h3 className="text-lg font-bold text-red-900">Error Loading Dashboard</h3>
                <p className="text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  const tabs = [
    { id: 'overview' as TabType, label: 'Overview', icon: Activity },
    { id: 'researchers' as TabType, label: 'Researchers', icon: Users },
    { id: 'payouts' as TabType, label: 'Payout Pool', icon: DollarSign },
    { id: 'analytics' as TabType, label: 'Analytics', icon: BarChart3 },
    { id: 'activity' as TabType, label: 'Activity Feed', icon: TrendingUp },
    { id: 'financial' as TabType, label: 'Financial', icon: FileText },
  ];

  return (
    <Layout title="Master Admin Dashboard">
      <div className="max-w-[1600px] mx-auto space-y-8">
        {/* Hero Section */}
        <motion.div
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-red-600 via-red-700 to-orange-700 p-8 md:p-12 text-white"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          {/* Animated background */}
          <motion.div
            className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl"
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
                    <Settings className="w-8 h-8" />
                  </div>
                  <div>
                    <h1 className="text-4xl md:text-5xl font-bold">
                      Master Admin Dashboard
                    </h1>
                    <p className="text-sm text-red-100 font-medium mt-1">
                      Complete Platform Control & Monitoring
                    </p>
                  </div>
                </motion.div>

                <motion.p
                  className="text-lg text-red-100 max-w-3xl leading-relaxed"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  Monitor platform metrics, manage researchers, control payout distributions, and
                  oversee all financial operations from this centralized command center.
                </motion.p>
              </div>

              <motion.button
                className="px-6 py-3 rounded-xl bg-white/20 backdrop-blur-sm hover:bg-white/30 transition-all border-2 border-white/30 font-semibold"
                onClick={handleRefresh}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Refresh Data
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-2xl border-2 border-gray-200 p-2 shadow-soft">
          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
                    selectedTab === tab.id
                      ? 'bg-gradient-to-r from-red-600 to-orange-600 text-white shadow-md'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                  onClick={() => setSelectedTab(tab.id)}
                >
                  <Icon className="w-5 h-5" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Content */}
        <div className="min-h-[600px]">
          {selectedTab === 'overview' && dashboardData && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <MasterDashboardOverview data={dashboardData} />
            </motion.div>
          )}

          {selectedTab === 'researchers' && (
            <motion.div
              key="researchers"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="bg-white rounded-2xl border-2 border-gray-200 p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-3 rounded-xl bg-blue-100 text-blue-600">
                    <Users className="w-6 h-6" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      Researcher Management
                    </h2>
                    <p className="text-sm text-gray-600">
                      {researchers.length} total researchers in the network
                    </p>
                  </div>
                </div>

                <EnhancedResearcherTable
                  researchers={researchers}
                  onResearcherClick={handleResearcherClick}
                  onSuspend={handleSuspendAccount}
                  onViewActivity={handleViewActivity}
                />
              </div>
            </motion.div>
          )}

          {selectedTab === 'payouts' && (
            <motion.div
              key="payouts"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <PayoutPoolManager
                currentPool={currentPool}
                onDistribute={handleDistribute}
                loading={loading}
              />
            </motion.div>
          )}

          {selectedTab === 'analytics' && (
            <motion.div
              key="analytics"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="space-y-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-purple-100 text-purple-600">
                    <BarChart3 className="w-6 h-6" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      Platform Analytics
                    </h2>
                    <p className="text-sm text-gray-600">
                      Revenue trends, user growth, and financial performance
                    </p>
                  </div>
                </div>

                <RevenueChart type="area" />
              </div>
            </motion.div>
          )}

          {selectedTab === 'activity' && (
            <motion.div
              key="activity"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <ActivityFeed
                activities={dashboardData?.recentActivity.map((activity, index) => ({
                  id: `activity-${index}`,
                  timestamp: activity.timestamp,
                  type: activity.type as any,
                  description: activity.description
                }))}
                onRefresh={handleRefresh}
                refreshing={loading}
                autoRefresh={true}
                autoRefreshInterval={30}
              />
            </motion.div>
          )}

          {selectedTab === 'financial' && dashboardData && (
            <motion.div
              key="financial"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="space-y-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-green-100 text-green-600">
                    <FileText className="w-6 h-6" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      Financial Overview
                    </h2>
                    <p className="text-sm text-gray-600">
                      Detailed financial reports and metrics
                    </p>
                  </div>
                </div>

                {/* Financial Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl border-2 border-green-200 p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-3 rounded-xl bg-green-600 text-white">
                        <DollarSign className="w-6 h-6" />
                      </div>
                      <h3 className="text-lg font-bold text-gray-900">Revenue</h3>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <p className="text-sm text-gray-600">Monthly Recurring</p>
                        <p className="text-2xl font-bold text-green-600">
                          ${dashboardData.platformMetrics.monthlyRecurringRevenue.toLocaleString()}
                        </p>
                      </div>
                      <div className="pt-3 border-t border-green-200">
                        <p className="text-sm text-gray-600">Annual Run Rate</p>
                        <p className="text-xl font-bold text-gray-900">
                          ${(dashboardData.platformMetrics.monthlyRecurringRevenue * 12).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-2xl border-2 border-orange-200 p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-3 rounded-xl bg-orange-600 text-white">
                        <TrendingUp className="w-6 h-6" />
                      </div>
                      <h3 className="text-lg font-bold text-gray-900">Payouts</h3>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <p className="text-sm text-gray-600">Monthly Obligations</p>
                        <p className="text-2xl font-bold text-orange-600">
                          ${dashboardData.platformMetrics.monthlyPayoutObligations.toLocaleString()}
                        </p>
                      </div>
                      <div className="pt-3 border-t border-orange-200">
                        <p className="text-sm text-gray-600">Payout Ratio</p>
                        <p className="text-xl font-bold text-gray-900">
                          {((dashboardData.platformMetrics.monthlyPayoutObligations / dashboardData.platformMetrics.monthlyRecurringRevenue) * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl border-2 border-blue-200 p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-3 rounded-xl bg-blue-600 text-white">
                        <BarChart3 className="w-6 h-6" />
                      </div>
                      <h3 className="text-lg font-bold text-gray-900">Profit</h3>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <p className="text-sm text-gray-600">Net Monthly</p>
                        <p className="text-2xl font-bold text-blue-600">
                          ${dashboardData.platformMetrics.netMonthlyProfit.toLocaleString()}
                        </p>
                      </div>
                      <div className="pt-3 border-t border-blue-200">
                        <p className="text-sm text-gray-600">Profit Margin</p>
                        <p className="text-xl font-bold text-gray-900">
                          {((dashboardData.platformMetrics.netMonthlyProfit / dashboardData.platformMetrics.monthlyRecurringRevenue) * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Revenue Chart */}
                <RevenueChart type="bar" />

                {/* Payout History Table */}
                <div className="bg-white rounded-2xl border-2 border-gray-200 p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">
                    Payout History
                  </h3>
                  <div className="overflow-x-auto">
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
                            Reviews
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
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="px-6 py-4 text-sm font-medium text-gray-900">
                              {new Date(item.month).toLocaleDateString('en-US', {
                                month: 'long',
                                year: 'numeric'
                              })}
                            </td>
                            <td className="px-6 py-4 text-sm font-semibold text-blue-600">
                              ${item.totalPool.toFixed(2)}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-700">
                              {item.reviewsApproved}
                            </td>
                            <td className="px-6 py-4 text-sm font-semibold text-green-600">
                              ${item.payoutPerReview.toFixed(2)}
                            </td>
                            <td className="px-6 py-4">
                              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${
                                item.status === 'completed'
                                  ? 'bg-green-100 text-green-700'
                                  : 'bg-gray-100 text-gray-700'
                              }`}>
                                {item.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default MasterAdminDashboardPage;
