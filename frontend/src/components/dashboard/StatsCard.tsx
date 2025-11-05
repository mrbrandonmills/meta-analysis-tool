'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: string | number
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
  icon: LucideIcon
  color: 'blue' | 'green' | 'purple' | 'yellow' | 'red'
  index?: number
}

const colorClasses = {
  blue: {
    bg: 'from-blue-500/10 to-blue-600/10',
    icon: 'bg-blue-100 text-blue-600',
    text: 'text-blue-600',
    border: 'border-blue-200 hover:border-blue-300'
  },
  green: {
    bg: 'from-green-500/10 to-green-600/10',
    icon: 'bg-green-100 text-green-600',
    text: 'text-green-600',
    border: 'border-green-200 hover:border-green-300'
  },
  purple: {
    bg: 'from-purple-500/10 to-purple-600/10',
    icon: 'bg-purple-100 text-purple-600',
    text: 'text-purple-600',
    border: 'border-purple-200 hover:border-purple-300'
  },
  yellow: {
    bg: 'from-yellow-500/10 to-yellow-600/10',
    icon: 'bg-yellow-100 text-yellow-600',
    text: 'text-yellow-600',
    border: 'border-yellow-200 hover:border-yellow-300'
  },
  red: {
    bg: 'from-red-500/10 to-red-600/10',
    icon: 'bg-red-100 text-red-600',
    text: 'text-red-600',
    border: 'border-red-200 hover:border-red-300'
  }
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon: Icon,
  color,
  index = 0
}) => {
  const colors = colorClasses[color]

  return (
    <motion.div
      className={`relative group p-6 rounded-2xl bg-gradient-to-br ${colors.bg} backdrop-blur-sm border ${colors.border} shadow-soft hover:shadow-medium transition-all duration-300 overflow-hidden`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -4, scale: 1.02 }}
    >
      {/* Hover glow effect */}
      <div className={`absolute inset-0 bg-gradient-to-br ${colors.bg} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />

      <div className="relative z-10">
        {/* Icon and Change */}
        <div className="flex items-start justify-between mb-4">
          <motion.div
            className={`inline-flex items-center justify-center w-12 h-12 rounded-xl ${colors.icon} shadow-sm`}
            whileHover={{ scale: 1.1, rotate: 5 }}
            transition={{ type: 'spring', stiffness: 400, damping: 10 }}
          >
            <Icon className="w-6 h-6" />
          </motion.div>

          {change && (
            <div className={`
              text-xs font-medium px-2 py-1 rounded-md
              ${changeType === 'positive' ? 'bg-green-100 text-green-700' : ''}
              ${changeType === 'negative' ? 'bg-red-100 text-red-700' : ''}
              ${changeType === 'neutral' ? 'bg-gray-100 text-gray-700' : ''}
            `}>
              {change}
            </div>
          )}
        </div>

        {/* Title */}
        <p className="text-sm font-medium text-gray-600 mb-1">
          {title}
        </p>

        {/* Value */}
        <p className="text-3xl font-bold text-gray-900">
          {value}
        </p>
      </div>
    </motion.div>
  )
}

export default StatsCard
