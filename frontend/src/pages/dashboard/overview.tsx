import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import { useAppStore } from '@/stores/useAppStore'
import { ToolType, ProjectStatus } from '@/lib/types'
import {
  TrendingUp,
  Clock,
  CheckCircle2,
  Zap,
  Plus,
  ArrowRight,
  Sparkles,
  BarChart3,
  Activity,
} from 'lucide-react'
import { useRouter } from 'next/router'
import StatsCard from '@/components/dashboard/StatsCard'
import ProjectsList from '@/components/dashboard/ProjectsList'
import AnalyticsDashboard from '@/components/dashboard/AnalyticsDashboard'
import QuickActions from '@/components/dashboard/QuickActions'
import NotificationCenter from '@/components/dashboard/NotificationCenter'

const DashboardOverview: React.FC = () => {
  const router = useRouter()
  const { projects, user, notifications, markNotificationRead, clearNotifications } = useAppStore()
  const [activeView, setActiveView] = useState<'overview' | 'projects' | 'analytics'>('overview')
  const [refreshing, setRefreshing] = useState(false)

  const stats = {
    total: projects.length,
    active: projects.filter((p) => p.status === ProjectStatus.IN_PROGRESS).length,
    completed: projects.filter((p) => p.status === ProjectStatus.COMPLETED).length,
    thisWeek: projects.filter(
      (p) =>
        new Date(p.createdAt).getTime() >
        Date.now() - 7 * 24 * 60 * 60 * 1000
    ).length,
  }

  const recentProjects = projects
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 6)

  const handleRefresh = async () => {
    setRefreshing(true)
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setRefreshing(false)
  }

  const viewTabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'projects', label: 'All Projects', icon: TrendingUp },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  ]

  return (
    <Layout title="Dashboard">
      <div className="space-y-8">
        {/* Hero Section */}
        <motion.div
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600 p-8 md:p-12 text-white"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          {/* Animated background elements */}
          <motion.div
            className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
          <motion.div
            className="absolute bottom-0 left-0 w-96 h-96 bg-accent-400/20 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.3, 1],
              opacity: [0.2, 0.4, 0.2],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 1,
            }}
          />

          <div className="relative z-10">
            <div className="flex items-start justify-between flex-wrap gap-4">
              <div>
                <motion.div
                  className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/20 backdrop-blur-sm text-sm font-medium mb-4"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                >
                  <Sparkles className="w-4 h-4" />
                  {new Date().toLocaleDateString('en-US', {
                    weekday: 'long',
                    month: 'long',
                    day: 'numeric',
                  })}
                </motion.div>

                <motion.h1
                  className="text-4xl md:text-5xl font-bold mb-3"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                >
                  Welcome back{user?.name ? `, ${user.name}` : ''}
                </motion.h1>

                <motion.p
                  className="text-lg text-blue-100 max-w-2xl"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  Your AI-powered research platform is ready. What will you discover today?
                </motion.p>
              </div>

              <motion.button
                className="group px-6 py-3 bg-white text-primary-600 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.5 }}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/tools/meta-analysis/new')}
              >
                <span className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  New Project
                </span>
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Total Projects"
            value={stats.total}
            change="+12%"
            changeType="positive"
            icon={TrendingUp}
            color="blue"
            index={0}
          />
          <StatsCard
            title="In Progress"
            value={stats.active}
            icon={Clock}
            color="yellow"
            index={1}
          />
          <StatsCard
            title="Completed"
            value={stats.completed}
            change="+5"
            changeType="positive"
            icon={CheckCircle2}
            color="green"
            index={2}
          />
          <StatsCard
            title="This Week"
            value={stats.thisWeek}
            change="+3"
            changeType="positive"
            icon={Zap}
            color="purple"
            index={3}
          />
        </div>

        {/* View Tabs */}
        <div className="border-b border-gray-200">
          <div className="flex gap-2">
            {viewTabs.map((tab) => {
              const TabIcon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveView(tab.id as any)}
                  className={`
                    relative px-6 py-3 font-medium transition-all
                    ${
                      activeView === tab.id
                        ? 'text-primary-600'
                        : 'text-gray-600 hover:text-gray-900'
                    }
                  `}
                >
                  <span className="flex items-center gap-2">
                    <TabIcon className="w-4 h-4" />
                    {tab.label}
                  </span>
                  {activeView === tab.id && (
                    <motion.div
                      layoutId="activeViewTab"
                      className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600"
                      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                    />
                  )}
                </button>
              )
            })}
          </div>
        </div>

        {/* Main Content Area */}
        {activeView === 'overview' && (
          <div className="space-y-8">
            {/* Quick Actions */}
            <QuickActions recentProjectId={recentProjects[0]?.id} />

            {/* Recent Projects Preview */}
            <div>
              <motion.div
                className="flex items-center justify-between mb-6"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.2 }}
              >
                <h2 className="text-2xl font-bold text-gray-900">Recent Projects</h2>
                <button
                  className="group flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
                  onClick={() => setActiveView('projects')}
                >
                  View All
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
              </motion.div>

              <ProjectsList
                projects={recentProjects}
                loading={refreshing}
                onRefresh={handleRefresh}
              />
            </div>
          </div>
        )}

        {activeView === 'projects' && (
          <ProjectsList
            projects={projects}
            loading={refreshing}
            onRefresh={handleRefresh}
          />
        )}

        {activeView === 'analytics' && (
          <AnalyticsDashboard loading={refreshing} />
        )}

        {/* Notifications in Sidebar/Dropdown - shown on all views */}
        <div className="fixed bottom-6 right-6 z-40">
          <NotificationCenter
            notifications={notifications}
            onMarkAsRead={markNotificationRead}
            onMarkAllAsRead={() => {
              notifications.forEach((n) => {
                if (!n.read) markNotificationRead(n.id)
              })
            }}
            onClear={clearNotifications}
            showAsDropdown
          />
        </div>
      </div>
    </Layout>
  )
}

export default DashboardOverview
