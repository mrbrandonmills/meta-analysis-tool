'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Activity,
  Clock,
  CheckCircle2,
  AlertCircle,
  Calendar,
} from 'lucide-react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts'
import { formatNumber, formatDuration } from '@/lib/utils'

interface AnalyticsData {
  projectsByMonth: Array<{ month: string; count: number }>
  projectsByTool: Array<{ tool: string; count: number; percentage: number }>
  projectsByStatus: Array<{ status: string; count: number; percentage: number }>
  studiesScreened: Array<{ date: string; count: number }>
  completionTimes: Array<{ project: string; duration: number }>
  successRate: {
    completed: number
    failed: number
    rate: number
  }
}

interface AnalyticsDashboardProps {
  data?: AnalyticsData
  loading?: boolean
  timeRange?: '7d' | '30d' | '90d' | '1y'
  onTimeRangeChange?: (range: '7d' | '30d' | '90d' | '1y') => void
}

const COLORS = {
  blue: '#2563eb',
  green: '#16a34a',
  purple: '#9333ea',
  yellow: '#ca8a04',
  red: '#dc2626',
  gray: '#6b7280',
}

const TOOL_COLORS = ['#2563eb', '#16a34a', '#9333ea', '#ca8a04']
const STATUS_COLORS = ['#16a34a', '#2563eb', '#ca8a04', '#dc2626', '#6b7280']

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  data,
  loading = false,
  timeRange = '30d',
  onTimeRangeChange,
}) => {
  const [activeChart, setActiveChart] = useState<'overview' | 'trends' | 'performance'>('overview')

  const timeRangeOptions = [
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
    { value: '90d', label: 'Last 90 days' },
    { value: '1y', label: 'Last year' },
  ]

  // Mock data if no data provided
  const mockData: AnalyticsData = {
    projectsByMonth: [
      { month: 'Jan', count: 12 },
      { month: 'Feb', count: 19 },
      { month: 'Mar', count: 15 },
      { month: 'Apr', count: 25 },
      { month: 'May', count: 22 },
      { month: 'Jun', count: 30 },
    ],
    projectsByTool: [
      { tool: 'Meta-Analysis', count: 45, percentage: 45 },
      { tool: 'Reviewer Matcher', count: 30, percentage: 30 },
      { tool: 'Peer Review', count: 15, percentage: 15 },
      { tool: 'Research Direction', count: 10, percentage: 10 },
    ],
    projectsByStatus: [
      { status: 'Completed', count: 68, percentage: 68 },
      { status: 'In Progress', count: 15, percentage: 15 },
      { status: 'Paused', count: 8, percentage: 8 },
      { status: 'Failed', count: 5, percentage: 5 },
      { status: 'Draft', count: 4, percentage: 4 },
    ],
    studiesScreened: [
      { date: '2024-01', count: 120 },
      { date: '2024-02', count: 245 },
      { date: '2024-03', count: 189 },
      { date: '2024-04', count: 340 },
      { date: '2024-05', count: 298 },
      { date: '2024-06', count: 425 },
    ],
    completionTimes: [
      { project: 'Project 1', duration: 3600 },
      { project: 'Project 2', duration: 7200 },
      { project: 'Project 3', duration: 5400 },
      { project: 'Project 4', duration: 4800 },
      { project: 'Project 5', duration: 6600 },
    ],
    successRate: {
      completed: 68,
      failed: 5,
      rate: 93.2,
    },
  }

  const analyticsData = data || mockData

  const stats = [
    {
      title: 'Total Projects',
      value: formatNumber(
        analyticsData.projectsByStatus.reduce((sum, item) => sum + item.count, 0)
      ),
      change: '+12.5%',
      changeType: 'positive' as const,
      icon: BarChart3,
      color: 'blue',
    },
    {
      title: 'Success Rate',
      value: `${analyticsData.successRate.rate.toFixed(1)}%`,
      change: '+2.3%',
      changeType: 'positive' as const,
      icon: CheckCircle2,
      color: 'green',
    },
    {
      title: 'Studies Screened',
      value: formatNumber(
        analyticsData.studiesScreened.reduce((sum, item) => sum + item.count, 0)
      ),
      change: '+18.2%',
      changeType: 'positive' as const,
      icon: Activity,
      color: 'purple',
    },
    {
      title: 'Avg. Completion Time',
      value: formatDuration(
        Math.round(
          analyticsData.completionTimes.reduce((sum, item) => sum + item.duration, 0) /
            analyticsData.completionTimes.length
        )
      ),
      change: '-5.4%',
      changeType: 'positive' as const,
      icon: Clock,
      color: 'yellow',
    },
  ]

  if (loading) {
    return (
      <div className="space-y-6">
        {/* Loading skeleton */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="h-32 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl animate-pulse"
            />
          ))}
        </div>
        <div className="h-96 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl animate-pulse" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
          <p className="text-gray-600 mt-1">Track your research productivity and trends</p>
        </div>

        {/* Time Range Selector */}
        <div className="flex items-center gap-2 p-1 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-xl">
          {timeRangeOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => onTimeRangeChange?.(option.value as any)}
              className={`
                px-4 py-2 rounded-lg text-sm font-medium transition-all
                ${
                  timeRange === option.value
                    ? 'bg-primary-600 text-white shadow-sm'
                    : 'text-gray-600 hover:bg-gray-50'
                }
              `}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`
                relative p-6 rounded-2xl bg-gradient-to-br from-${stat.color}-500/10 to-${stat.color}-600/10
                backdrop-blur-sm border border-${stat.color}-200 shadow-soft hover:shadow-medium
                transition-all duration-300 overflow-hidden group
              `}
            >
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-4">
                  <div className={`
                    inline-flex items-center justify-center w-12 h-12 rounded-xl
                    bg-${stat.color}-100 text-${stat.color}-600 shadow-sm
                  `}>
                    <Icon className="w-6 h-6" />
                  </div>
                  {stat.change && (
                    <div className={`
                      flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-md
                      ${
                        stat.changeType === 'positive'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                      }
                    `}>
                      {stat.changeType === 'positive' ? (
                        <TrendingUp className="w-3 h-3" />
                      ) : (
                        <TrendingDown className="w-3 h-3" />
                      )}
                      {stat.change}
                    </div>
                  )}
                </div>
                <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Chart Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-2">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'trends', label: 'Trends', icon: TrendingUp },
            { id: 'performance', label: 'Performance', icon: Activity },
          ].map((tab) => {
            const TabIcon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveChart(tab.id as any)}
                className={`
                  relative px-6 py-3 font-medium transition-all
                  ${
                    activeChart === tab.id
                      ? 'text-primary-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }
                `}
              >
                <span className="flex items-center gap-2">
                  <TabIcon className="w-4 h-4" />
                  {tab.label}
                </span>
                {activeChart === tab.id && (
                  <motion.div
                    layoutId="activeChartTab"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600"
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Projects by Month */}
        {activeChart === 'overview' && (
          <>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Projects Over Time</h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={analyticsData.projectsByMonth}>
                  <defs>
                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={COLORS.blue} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={COLORS.blue} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="month" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="count"
                    stroke={COLORS.blue}
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorCount)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Projects by Tool */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Projects by Tool</h3>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={analyticsData.projectsByTool}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percentage }) => `${name}: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {analyticsData.projectsByTool.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={TOOL_COLORS[index % TOOL_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                    }}
                  />
                </RechartsPieChart>
              </ResponsiveContainer>
            </motion.div>

            {/* Projects by Status */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl lg:col-span-2"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Projects by Status</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analyticsData.projectsByStatus}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="status" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                    {analyticsData.projectsByStatus.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={STATUS_COLORS[index % STATUS_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </motion.div>
          </>
        )}

        {activeChart === 'trends' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl lg:col-span-2"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Studies Screened Over Time</h3>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={analyticsData.studiesScreened}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="date" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke={COLORS.purple}
                  strokeWidth={3}
                  dot={{ fill: COLORS.purple, r: 5 }}
                  activeDot={{ r: 8 }}
                  name="Studies Screened"
                />
              </LineChart>
            </ResponsiveContainer>
          </motion.div>
        )}

        {activeChart === 'performance' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl lg:col-span-2"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Completion Times</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={analyticsData.completionTimes}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="project" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                  }}
                  formatter={(value: number) => formatDuration(value)}
                />
                <Bar dataKey="duration" fill={COLORS.green} radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        )}
      </div>

      {/* Success Rate Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-8 bg-gradient-to-br from-green-500/10 to-green-600/10 backdrop-blur-sm border border-green-200 rounded-2xl"
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Overall Success Rate</h3>
            <p className="text-gray-600">
              {analyticsData.successRate.completed} completed out of{' '}
              {analyticsData.successRate.completed + analyticsData.successRate.failed} total projects
            </p>
          </div>
          <div className="text-right">
            <div className="text-5xl font-bold text-green-600 mb-2">
              {analyticsData.successRate.rate.toFixed(1)}%
            </div>
            <div className="flex items-center gap-2 text-sm text-green-600 font-medium">
              <TrendingUp className="w-4 h-4" />
              Excellent performance
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default AnalyticsDashboard
