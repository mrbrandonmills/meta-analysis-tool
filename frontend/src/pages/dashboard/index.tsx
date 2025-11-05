import React from 'react'
import { motion } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import StatsCard from '@/components/dashboard/StatsCard'
import ProjectCard from '@/components/dashboard/ProjectCard'
import { useAppStore } from '@/stores/useAppStore'
import { ToolType, ProjectStatus } from '@/lib/types'
import {
  TrendingUp,
  Clock,
  CheckCircle2,
  Zap,
  Microscope,
  Users,
  FileText,
  Lightbulb,
  Plus,
  ArrowRight,
  Sparkles
} from 'lucide-react'
import { useRouter } from 'next/router'

const toolIcons = {
  [ToolType.META_ANALYSIS]: Microscope,
  [ToolType.REVIEWER_MATCHER]: Users,
  [ToolType.PEER_REVIEW]: FileText,
  [ToolType.RESEARCH_DIRECTION]: Lightbulb
}

const toolColors = {
  [ToolType.META_ANALYSIS]: 'blue',
  [ToolType.REVIEWER_MATCHER]: 'green',
  [ToolType.PEER_REVIEW]: 'purple',
  [ToolType.RESEARCH_DIRECTION]: 'yellow'
}

const DashboardNewPage: React.FC = () => {
  const router = useRouter()
  const { projects, user } = useAppStore()

  const stats = {
    total: projects.length,
    active: projects.filter(p => p.status === ProjectStatus.IN_PROGRESS).length,
    completed: projects.filter(p => p.status === ProjectStatus.COMPLETED).length,
    byTool: {
      [ToolType.META_ANALYSIS]: projects.filter(p => p.toolType === ToolType.META_ANALYSIS).length,
      [ToolType.REVIEWER_MATCHER]: projects.filter(p => p.toolType === ToolType.REVIEWER_MATCHER).length,
      [ToolType.PEER_REVIEW]: projects.filter(p => p.toolType === ToolType.PEER_REVIEW).length,
      [ToolType.RESEARCH_DIRECTION]: projects.filter(p => p.toolType === ToolType.RESEARCH_DIRECTION).length
    }
  }

  const recentProjects = projects
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 6)

  const quickActions = [
    {
      title: 'New Meta-Analysis',
      description: 'Start a systematic review',
      icon: Microscope,
      color: 'blue',
      href: '/tools/meta-analysis/new'
    },
    {
      title: 'Find Reviewers',
      description: 'Match expert reviewers',
      icon: Users,
      color: 'green',
      href: '/tools/reviewer-matcher/new'
    },
    {
      title: 'Generate Review',
      description: 'Create peer review',
      icon: FileText,
      color: 'purple',
      href: '/tools/peer-review/new'
    },
    {
      title: 'Discover Gaps',
      description: 'Explore research directions',
      icon: Lightbulb,
      color: 'yellow',
      href: '/tools/research-direction/new'
    }
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
              opacity: [0.3, 0.5, 0.3]
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
          />
          <motion.div
            className="absolute bottom-0 left-0 w-96 h-96 bg-accent-400/20 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.3, 1],
              opacity: [0.2, 0.4, 0.2]
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 1
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
                  {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
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
            value="8"
            change="+3"
            changeType="positive"
            icon={Zap}
            color="purple"
            index={3}
          />
        </div>

        {/* Quick Actions */}
        <div>
          <motion.div
            className="flex items-center justify-between mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.4 }}
          >
            <h2 className="text-2xl font-bold text-gray-900">Quick Actions</h2>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action, index) => (
              <motion.button
                key={action.title}
                className="group relative p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 hover:border-primary-300 shadow-soft hover:shadow-lg transition-all duration-300 text-left overflow-hidden"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.5 + index * 0.1 }}
                whileHover={{ y: -4, scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push(action.href)}
              >
                <div className={`absolute inset-0 bg-gradient-to-br from-${action.color}-500/0 to-${action.color}-600/0 group-hover:from-${action.color}-500/5 group-hover:to-${action.color}-600/10 transition-all duration-300`} />

                <div className="relative z-10">
                  <motion.div
                    className={`inline-flex items-center justify-center w-12 h-12 rounded-xl bg-${action.color}-100 text-${action.color}-600 mb-4`}
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: 'spring', stiffness: 400, damping: 10 }}
                  >
                    <action.icon className="w-6 h-6" />
                  </motion.div>

                  <h3 className="text-base font-semibold text-gray-900 mb-1 group-hover:text-primary-600 transition-colors">
                    {action.title}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {action.description}
                  </p>
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Recent Projects */}
        <div>
          <motion.div
            className="flex items-center justify-between mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.8 }}
          >
            <h2 className="text-2xl font-bold text-gray-900">Recent Projects</h2>
            <button
              className="group flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
              onClick={() => router.push('/projects')}
            >
              View All
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </motion.div>

          {recentProjects.length === 0 ? (
            <motion.div
              className="p-12 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.9 }}
            >
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-100 text-gray-400 mb-4">
                <Microscope className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No projects yet</h3>
              <p className="text-gray-600 mb-6">Get started by creating your first research project</p>
              <motion.button
                className="px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow-primary transition-all duration-300"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/tools/meta-analysis/new')}
              >
                <span className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  Create Your First Project
                </span>
              </motion.button>
            </motion.div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recentProjects.map((project, index) => (
                <ProjectCard
                  key={project.id}
                  id={project.id}
                  title={project.title}
                  description={project.description}
                  status={project.status}
                  toolType={project.toolType}
                  icon={toolIcons[project.toolType as ToolType]}
                  color={toolColors[project.toolType as ToolType]}
                  updatedAt={project.updatedAt.toString()}
                  progress={45}
                  index={index}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default DashboardNewPage
