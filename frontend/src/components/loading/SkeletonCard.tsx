'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface SkeletonCardProps {
  variant?: 'project' | 'stats' | 'tool'
  className?: string
}

const SkeletonCard: React.FC<SkeletonCardProps> = ({ variant = 'project', className = '' }) => {
  return (
    <div className={`p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200 ${className}`}>
      <div className="animate-pulse">
        {variant === 'project' && (
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-12 h-12 bg-gray-200 rounded-xl" />
              <div className="flex-1 space-y-2">
                <div className="h-5 bg-gray-200 rounded w-3/4" />
                <div className="h-3 bg-gray-200 rounded w-1/2" />
              </div>
            </div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded" />
              <div className="h-4 bg-gray-200 rounded w-5/6" />
            </div>
            <div className="flex items-center justify-between">
              <div className="h-6 bg-gray-200 rounded-full w-24" />
              <div className="h-3 bg-gray-200 rounded w-16" />
            </div>
          </div>
        )}

        {variant === 'stats' && (
          <div className="space-y-4">
            <div className="flex items-start justify-between">
              <div className="w-12 h-12 bg-gray-200 rounded-xl" />
              <div className="h-5 bg-gray-200 rounded-full w-12" />
            </div>
            <div className="h-4 bg-gray-200 rounded w-1/2" />
            <div className="h-8 bg-gray-200 rounded w-3/4" />
          </div>
        )}

        {variant === 'tool' && (
          <div className="space-y-4">
            <div className="w-12 h-12 bg-gray-200 rounded-xl" />
            <div className="space-y-2">
              <div className="h-6 bg-gray-200 rounded w-3/4" />
              <div className="h-4 bg-gray-200 rounded" />
              <div className="h-4 bg-gray-200 rounded w-5/6" />
            </div>
            <div className="h-10 bg-gray-200 rounded-xl" />
          </div>
        )}
      </div>

      {/* Shimmer effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/50 to-transparent"
        animate={{
          x: ['-100%', '100%']
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'linear'
        }}
        style={{
          backgroundSize: '200% 100%'
        }}
      />
    </div>
  )
}

export default SkeletonCard
