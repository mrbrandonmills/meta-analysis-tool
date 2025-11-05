'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/router'
import { LucideIcon, ArrowRight, Clock, CheckCircle2, AlertCircle, Pause } from 'lucide-react'
import { ProjectStatus } from '@/lib/types'
import { formatRelativeTime } from '@/lib/utils'

interface ProjectCardProps {
  id: string
  title: string
  description?: string
  status: ProjectStatus
  toolType: string
  icon: LucideIcon
  color: string
  updatedAt: string
  progress?: number
  index?: number
}

const statusConfig: Record<ProjectStatus, { icon: LucideIcon; color: string; label: string }> = {
  [ProjectStatus.DRAFT]: {
    icon: Clock,
    color: 'gray',
    label: 'Draft'
  },
  [ProjectStatus.IN_PROGRESS]: {
    icon: Clock,
    color: 'blue',
    label: 'In Progress'
  },
  [ProjectStatus.COMPLETED]: {
    icon: CheckCircle2,
    color: 'green',
    label: 'Completed'
  },
  [ProjectStatus.FAILED]: {
    icon: AlertCircle,
    color: 'red',
    label: 'Failed'
  },
  [ProjectStatus.PAUSED]: {
    icon: Pause,
    color: 'yellow',
    label: 'Paused'
  },
  [ProjectStatus.CANCELLED]: {
    icon: AlertCircle,
    color: 'gray',
    label: 'Cancelled'
  }
}

const ProjectCard: React.FC<ProjectCardProps> = ({
  id,
  title,
  description,
  status,
  icon: Icon,
  color,
  updatedAt,
  progress = 0,
  index = 0
}) => {
  const router = useRouter()
  const statusInfo = statusConfig[status]
  const StatusIcon = statusInfo.icon

  return (
    <motion.div
      className="group relative cursor-pointer"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -4 }}
      onClick={() => router.push(`/projects/${id}`)}
    >
      <div className="relative p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 group-hover:border-primary-300 shadow-soft group-hover:shadow-lg transition-all duration-300 overflow-hidden">
        {/* Gradient overlay on hover */}
        <div className={`absolute inset-0 bg-gradient-to-br from-${color}-500/0 to-${color}-600/0 group-hover:from-${color}-500/5 group-hover:to-${color}-600/10 transition-all duration-300`} />

        <div className="relative z-10">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-start gap-3 flex-1 min-w-0">
              <motion.div
                className={`inline-flex items-center justify-center w-12 h-12 rounded-xl bg-${color}-100 text-${color}-600 shadow-sm flex-shrink-0`}
                whileHover={{ scale: 1.1, rotate: 5 }}
                transition={{ type: 'spring', stiffness: 400, damping: 10 }}
              >
                <Icon className="w-6 h-6" />
              </motion.div>

              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-gray-900 truncate group-hover:text-primary-600 transition-colors">
                  {title}
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  Updated {formatRelativeTime(updatedAt)}
                </p>
              </div>
            </div>

            <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 group-hover:translate-x-1 transition-all flex-shrink-0 ml-2" />
          </div>

          {/* Description */}
          {description && (
            <p className="text-sm text-gray-600 line-clamp-2 mb-4 leading-relaxed">
              {description}
            </p>
          )}

          {/* Status and Progress */}
          <div className="space-y-3">
            {/* Status Badge */}
            <div className="flex items-center justify-between">
              <div className={`
                inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium
                ${statusInfo.color === 'gray' ? 'bg-gray-100 text-gray-700' : ''}
                ${statusInfo.color === 'blue' ? 'bg-blue-100 text-blue-700' : ''}
                ${statusInfo.color === 'green' ? 'bg-green-100 text-green-700' : ''}
                ${statusInfo.color === 'yellow' ? 'bg-yellow-100 text-yellow-700' : ''}
                ${statusInfo.color === 'red' ? 'bg-red-100 text-red-700' : ''}
              `}>
                <StatusIcon className="w-3.5 h-3.5" />
                {statusInfo.label}
              </div>

              {status === ProjectStatus.IN_PROGRESS && (
                <span className="text-xs font-medium text-gray-600">
                  {progress}%
                </span>
              )}
            </div>

            {/* Progress Bar */}
            {status === ProjectStatus.IN_PROGRESS && (
              <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <motion.div
                  className={`h-full bg-gradient-to-r from-${color}-500 to-${color}-600 rounded-full`}
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default ProjectCard
