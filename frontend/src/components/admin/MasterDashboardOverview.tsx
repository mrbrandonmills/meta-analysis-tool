import React from 'react';
import { motion } from 'framer-motion';
import {
  DollarSign,
  Users,
  TrendingUp,
  TrendingDown,
  Activity,
  CreditCard,
  Wallet,
  BarChart3
} from 'lucide-react';
import { AdminDashboardData } from '@/lib/payment-types';

interface MasterDashboardOverviewProps {
  data: AdminDashboardData;
}

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  index: number;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon,
  color,
  trend,
  index
}) => {
  return (
    <motion.div
      className="relative overflow-hidden rounded-2xl bg-white border-2 border-gray-200 p-6 shadow-soft hover:shadow-medium transition-all duration-300"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      whileHover={{ y: -4 }}
    >
      {/* Background gradient */}
      <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${color} opacity-10 rounded-full blur-2xl`} />

      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 rounded-xl ${color} bg-opacity-10`}>
            {icon}
          </div>
          {trend && (
            <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${
              trend.isPositive
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            }`}>
              {trend.isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              {trend.value}
            </div>
          )}
        </div>

        <p className="text-sm font-medium text-gray-600 mb-1">
          {title}
        </p>

        <p className="text-3xl font-bold text-gray-900">
          {value}
        </p>
      </div>
    </motion.div>
  );
};

export const MasterDashboardOverview: React.FC<MasterDashboardOverviewProps> = ({ data }) => {
  const metrics = [
    {
      title: 'Active Subscriptions',
      value: data.platformMetrics.totalActiveSubscriptions,
      icon: <Users className="w-6 h-6 text-blue-600" />,
      color: 'from-blue-500 to-blue-600',
    },
    {
      title: 'Paying Members',
      value: data.platformMetrics.totalPayingMembers,
      icon: <CreditCard className="w-6 h-6 text-purple-600" />,
      color: 'from-purple-500 to-purple-600',
    },
    {
      title: 'Monthly Recurring Revenue',
      value: `$${data.platformMetrics.monthlyRecurringRevenue.toLocaleString()}`,
      icon: <DollarSign className="w-6 h-6 text-green-600" />,
      color: 'from-green-500 to-green-600',
      trend: {
        value: '+12.5%',
        isPositive: true
      }
    },
    {
      title: 'Payout Obligations',
      value: `$${data.platformMetrics.monthlyPayoutObligations.toLocaleString()}`,
      icon: <Wallet className="w-6 h-6 text-orange-600" />,
      color: 'from-orange-500 to-orange-600',
    },
    {
      title: 'Net Monthly Profit',
      value: `$${data.platformMetrics.netMonthlyProfit.toLocaleString()}`,
      icon: <BarChart3 className="w-6 h-6 text-emerald-600" />,
      color: 'from-emerald-500 to-emerald-600',
      trend: {
        value: '+8.3%',
        isPositive: true
      }
    },
  ];

  const poolMetrics = [
    {
      label: 'Current Pool',
      value: `$${data.currentMonthPool.poolAmount.toFixed(2)}`,
      color: 'text-blue-600'
    },
    {
      label: 'Papers Submitted',
      value: data.currentMonthPool.papersSubmitted,
      color: 'text-purple-600'
    },
    {
      label: 'Reviews Assigned',
      value: data.currentMonthPool.reviewsAssigned,
      color: 'text-indigo-600'
    },
    {
      label: 'Reviews Completed',
      value: data.currentMonthPool.reviewsCompleted,
      color: 'text-green-600'
    },
    {
      label: 'Reviews Approved',
      value: data.currentMonthPool.reviewsApproved,
      color: 'text-emerald-600'
    },
    {
      label: 'Est. Payout/Review',
      value: `$${data.currentMonthPool.estimatedPayoutPerReview.toFixed(2)}`,
      color: 'text-orange-600'
    },
  ];

  const researcherMetrics = [
    {
      label: 'Total Researchers',
      value: data.researcherPool.totalResearchers,
      color: 'text-blue-600'
    },
    {
      label: 'Active Reviewers',
      value: data.researcherPool.activeReviewers,
      color: 'text-green-600'
    },
    {
      label: 'Avg H-Index',
      value: data.researcherPool.averageHIndex.toFixed(1),
      color: 'text-purple-600'
    },
    {
      label: 'Avg Reviews/Month',
      value: data.researcherPool.averageReviewsPerMonth.toFixed(1),
      color: 'text-orange-600'
    },
  ];

  return (
    <div className="space-y-8">
      {/* Main Platform Metrics */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Platform Overview
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {metrics.map((metric, index) => (
            <MetricCard key={metric.title} {...metric} index={index} />
          ))}
        </div>
      </div>

      {/* Current Month Pool Stats */}
      <motion.div
        className="rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.5 }}
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-xl bg-blue-600 text-white">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">
              Current Month Activity
            </h3>
            <p className="text-sm text-gray-600">
              Real-time pool and review statistics
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {poolMetrics.map((metric, index) => (
            <motion.div
              key={metric.label}
              className="bg-white rounded-xl p-4 border border-blue-200"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 0.6 + index * 0.05 }}
            >
              <p className="text-xs text-gray-600 mb-1">{metric.label}</p>
              <p className={`text-2xl font-bold ${metric.color}`}>
                {metric.value}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Researcher Pool Stats */}
      <motion.div
        className="rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200 p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.7 }}
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-xl bg-purple-600 text-white">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">
              Researcher Pool
            </h3>
            <p className="text-sm text-gray-600">
              Network composition and activity
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {researcherMetrics.map((metric, index) => (
            <motion.div
              key={metric.label}
              className="bg-white rounded-xl p-4 border border-purple-200"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 0.8 + index * 0.05 }}
            >
              <p className="text-xs text-gray-600 mb-1">{metric.label}</p>
              <p className={`text-2xl font-bold ${metric.color}`}>
                {metric.value}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default MasterDashboardOverview;
