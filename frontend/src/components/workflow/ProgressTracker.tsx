/**
 * Progress Tracker Component
 * Beautiful glassmorphism progress tracker with animations
 */

import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Loader,
  CheckCircle2,
  AlertCircle,
  Clock,
  TrendingUp,
  Zap,
} from 'lucide-react'
import { useProgressTracking } from '@/hooks/useProgressTracking'

interface ProgressTrackerProps {
  taskId: string | null
  taskType: 'meta-analysis' | 'peer-review' | 'reviewer-matcher'
  title?: string
  onComplete?: () => void
  className?: string
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  taskId,
  taskType,
  title = 'Running Analysis',
  onComplete,
  className = '',
}) => {
  const {
    progress,
    status,
    currentStep,
    stepsCompleted,
    stepsRemaining,
    formatTimeRemaining,
    getCompletionPercentage,
    isComplete,
    isRunning,
    hasError,
    error,
  } = useProgressTracking({
    taskId,
    taskType,
    enabled: !!taskId,
    onComplete,
  })

  // Don't render if no task
  if (!taskId) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
      className={`relative overflow-hidden rounded-2xl bg-white/60 backdrop-blur-md border border-gray-200 shadow-lg ${className}`}
    >
      {/* Animated Background Gradient */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10"
        animate={{
          backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: 'linear',
        }}
        style={{
          backgroundSize: '200% 100%',
        }}
      />

      {/* Content */}
      <div className="relative z-10 p-6 space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            {isRunning && (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className="p-2 rounded-xl bg-blue-100 text-blue-600"
              >
                <Loader className="w-5 h-5" />
              </motion.div>
            )}
            {isComplete && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                className="p-2 rounded-xl bg-green-100 text-green-600"
              >
                <CheckCircle2 className="w-5 h-5" />
              </motion.div>
            )}
            {hasError && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                className="p-2 rounded-xl bg-red-100 text-red-600"
              >
                <AlertCircle className="w-5 h-5" />
              </motion.div>
            )}
            <div>
              <h3 className="text-lg font-bold text-gray-900">{title}</h3>
              <p className="text-sm text-gray-600">
                {isComplete
                  ? 'Analysis complete!'
                  : hasError
                  ? 'Analysis failed'
                  : 'Processing your request...'}
              </p>
            </div>
          </div>

          {/* Status Badge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className={`px-3 py-1 rounded-full text-xs font-semibold ${
              isRunning
                ? 'bg-blue-100 text-blue-700'
                : isComplete
                ? 'bg-green-100 text-green-700'
                : hasError
                ? 'bg-red-100 text-red-700'
                : 'bg-gray-100 text-gray-700'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </motion.div>
        </div>

        {/* Time Estimation */}
        {isRunning && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-6 p-4 rounded-xl bg-white/50 border border-gray-200"
          >
            <div className="flex items-center gap-2 flex-1">
              <Clock className="w-4 h-4 text-gray-500" />
              <div>
                <p className="text-xs text-gray-500 font-medium">
                  Estimated Time Remaining
                </p>
                <p className="text-sm font-bold text-gray-900">
                  {formatTimeRemaining()}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-1">
              <TrendingUp className="w-4 h-4 text-gray-500" />
              <div>
                <p className="text-xs text-gray-500 font-medium">Progress</p>
                <p className="text-sm font-bold text-gray-900">
                  {getCompletionPercentage()} complete
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-gray-700">
              {getCompletionPercentage()}
            </span>
            <span className="text-gray-500">
              {stepsCompleted.length} of{' '}
              {stepsCompleted.length + stepsRemaining.length} steps
            </span>
          </div>

          {/* Animated Progress Bar */}
          <div className="relative h-3 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            >
              {/* Shimmer Effect */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                animate={{
                  x: ['-100%', '200%'],
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: 'linear',
                }}
              />
            </motion.div>
          </div>
        </div>

        {/* Current Step */}
        {currentStep && isRunning && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="p-4 rounded-xl bg-blue-50 border border-blue-200"
          >
            <div className="flex items-center gap-3">
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Zap className="w-5 h-5 text-blue-600" />
              </motion.div>
              <div>
                <p className="text-xs font-semibold text-blue-700 uppercase tracking-wider">
                  Current Step
                </p>
                <p className="text-sm font-medium text-blue-900">{currentStep}</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Steps List */}
        <div className="space-y-2">
          {/* Completed Steps */}
          <AnimatePresence>
            {stepsCompleted.map((step, index) => (
              <motion.div
                key={`completed-${index}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="flex items-center gap-3 p-3 rounded-lg bg-green-50 border border-green-200"
              >
                <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                <span className="text-sm text-green-900 font-medium">{step}</span>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Running Step */}
          {currentStep && isRunning && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3 p-3 rounded-lg bg-blue-50 border border-blue-200"
            >
              <Loader className="w-4 h-4 text-blue-600 flex-shrink-0 animate-spin" />
              <span className="text-sm text-blue-900 font-medium">
                {currentStep}
              </span>
            </motion.div>
          )}

          {/* Remaining Steps */}
          {stepsRemaining.map((step, index) => (
            <motion.div
              key={`remaining-${index}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className="flex items-center gap-3 p-3 rounded-lg bg-gray-50 border border-gray-200"
            >
              <div className="w-4 h-4 rounded-full border-2 border-gray-300 flex-shrink-0" />
              <span className="text-sm text-gray-500">{step}</span>
            </motion.div>
          ))}
        </div>

        {/* Error Message */}
        {hasError && error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 rounded-xl bg-red-50 border border-red-200"
          >
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-red-900">Error</p>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Completion Animation Overlay */}
      <AnimatePresence>
        {isComplete && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-green-500/10 backdrop-blur-sm flex items-center justify-center"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, damping: 20 }}
              className="text-center"
            >
              <motion.div
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ duration: 0.5 }}
                className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-500 text-white mb-4"
              >
                <CheckCircle2 className="w-10 h-10" />
              </motion.div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default ProgressTracker
