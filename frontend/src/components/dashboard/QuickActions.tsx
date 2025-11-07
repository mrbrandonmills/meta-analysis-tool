'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/router'
import {
  Plus,
  Microscope,
  Users,
  FileText,
  Lightbulb,
  Play,
  Copy,
  ArrowRight,
} from 'lucide-react'
import { ToolType } from '@/lib/types'

interface QuickAction {
  id: string
  title: string
  description: string
  icon: React.ElementType
  color: 'blue' | 'green' | 'purple' | 'yellow'
  href: string
  badge?: string
}

interface QuickActionsProps {
  onActionClick?: (actionId: string) => void
  recentProjectId?: string
}

const QuickActions: React.FC<QuickActionsProps> = ({
  onActionClick,
  recentProjectId,
}) => {
  const router = useRouter()

  const primaryActions: QuickAction[] = [
    {
      id: 'new-meta-analysis',
      title: 'New Meta-Analysis',
      description: 'Start a comprehensive systematic review',
      icon: Microscope,
      color: 'blue',
      href: '/tools/meta-analysis/new',
      badge: 'Most Popular',
    },
    {
      id: 'find-reviewers',
      title: 'Find Reviewers',
      description: 'Match expert reviewers for your paper',
      icon: Users,
      color: 'green',
      href: '/tools/reviewer-matcher/new',
    },
    {
      id: 'generate-review',
      title: 'Generate Review',
      description: 'Create detailed peer review feedback',
      icon: FileText,
      color: 'purple',
      href: '/tools/peer-review/new',
    },
    {
      id: 'discover-gaps',
      title: 'Discover Research Gaps',
      description: 'Explore new research directions',
      icon: Lightbulb,
      color: 'yellow',
      href: '/tools/research-direction/new',
    },
  ]

  const secondaryActions = [
    {
      id: 'resume-project',
      title: 'Resume Recent Project',
      description: 'Continue where you left off',
      icon: Play,
      color: 'blue' as const,
      disabled: !recentProjectId,
    },
    {
      id: 'clone-project',
      title: 'Clone Project',
      description: 'Duplicate an existing project',
      icon: Copy,
      color: 'purple' as const,
      disabled: !recentProjectId,
    },
  ]

  const handleActionClick = (action: QuickAction) => {
    onActionClick?.(action.id)
    router.push(action.href)
  }

  const handleSecondaryAction = (actionId: string) => {
    if (actionId === 'resume-project' && recentProjectId) {
      router.push(`/projects/${recentProjectId}`)
    } else if (actionId === 'clone-project' && recentProjectId) {
      // Handle clone action
      onActionClick?.(actionId)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Quick Actions</h2>
        <p className="text-gray-600 mt-1">Start a new project or continue working</p>
      </div>

      {/* Primary Actions Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {primaryActions.map((action, index) => {
          const Icon = action.icon
          return (
            <motion.button
              key={action.id}
              onClick={() => handleActionClick(action)}
              className="group relative p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 hover:border-primary-300 shadow-soft hover:shadow-lg transition-all duration-300 text-left overflow-hidden"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              whileHover={{ y: -4, scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {/* Gradient overlay on hover */}
              <div className={`absolute inset-0 bg-gradient-to-br from-${action.color}-500/0 to-${action.color}-600/0 group-hover:from-${action.color}-500/5 group-hover:to-${action.color}-600/10 transition-all duration-300`} />

              <div className="relative z-10">
                {/* Badge */}
                {action.badge && (
                  <div className="absolute -top-2 -right-2">
                    <span className="px-3 py-1 bg-accent-500 text-white text-xs font-bold rounded-full shadow-lg">
                      {action.badge}
                    </span>
                  </div>
                )}

                {/* Icon */}
                <motion.div
                  className={`inline-flex items-center justify-center w-14 h-14 rounded-xl bg-${action.color}-100 text-${action.color}-600 mb-4 shadow-sm`}
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  transition={{ type: 'spring', stiffness: 400, damping: 10 }}
                >
                  <Icon className="w-7 h-7" />
                </motion.div>

                {/* Content */}
                <h3 className="text-base font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                  {action.title}
                </h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {action.description}
                </p>

                {/* Arrow indicator */}
                <div className="mt-4 flex items-center text-sm font-medium text-primary-600 opacity-0 group-hover:opacity-100 transition-opacity">
                  Get started
                  <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </motion.button>
          )
        })}
      </div>

      {/* Secondary Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {secondaryActions.map((action, index) => {
          const Icon = action.icon
          return (
            <motion.button
              key={action.id}
              onClick={() => handleSecondaryAction(action.id)}
              disabled={action.disabled}
              className={`
                group p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200
                shadow-soft text-left transition-all duration-300
                ${
                  action.disabled
                    ? 'opacity-50 cursor-not-allowed'
                    : 'hover:border-primary-300 hover:shadow-md cursor-pointer'
                }
              `}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.4 + index * 0.1 }}
              whileHover={action.disabled ? {} : { y: -2 }}
              whileTap={action.disabled ? {} : { scale: 0.98 }}
            >
              <div className="flex items-center gap-4">
                <div className={`
                  inline-flex items-center justify-center w-12 h-12 rounded-xl
                  bg-${action.color}-100 text-${action.color}-600 shadow-sm flex-shrink-0
                `}>
                  <Icon className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <h3 className={`
                    text-base font-semibold text-gray-900 mb-1
                    ${!action.disabled && 'group-hover:text-primary-600'} transition-colors
                  `}>
                    {action.title}
                  </h3>
                  <p className="text-sm text-gray-600">{action.description}</p>
                </div>
                {!action.disabled && (
                  <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 group-hover:translate-x-1 transition-all flex-shrink-0" />
                )}
              </div>
            </motion.button>
          )
        })}
      </div>

      {/* CTA Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="relative overflow-hidden p-8 rounded-2xl bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600 text-white shadow-lg"
      >
        {/* Animated background */}
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

        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold mb-2">Need help getting started?</h3>
              <p className="text-blue-100 mb-4">
                Check out our documentation or watch tutorial videos
              </p>
              <div className="flex gap-3">
                <button className="px-6 py-2 bg-white text-primary-600 rounded-xl font-semibold hover:bg-blue-50 transition-all">
                  View Docs
                </button>
                <button className="px-6 py-2 bg-white/10 backdrop-blur-sm text-white rounded-xl font-semibold hover:bg-white/20 transition-all">
                  Watch Tutorials
                </button>
              </div>
            </div>
            <div className="hidden lg:block">
              <Lightbulb className="w-24 h-24 text-white/20" />
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default QuickActions
