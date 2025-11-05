'use client'

import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  Filter,
  CheckCircle2,
  BarChart3,
  FileText,
  Brain,
  Loader2,
  Check,
  AlertCircle,
  Clock
} from 'lucide-react'

export enum AgentState {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  ERROR = 'error'
}

export interface AgentStep {
  id: string
  name: string
  description: string
  icon: React.ComponentType<any>
  state: AgentState
  progress?: number
  eta?: number
  message?: string
}

interface AgentPipelineProps {
  steps: AgentStep[]
  currentStep?: number
}

const stateConfig = {
  [AgentState.PENDING]: {
    icon: Clock,
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-600',
    borderColor: 'border-gray-300'
  },
  [AgentState.RUNNING]: {
    icon: Loader2,
    color: 'blue',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-600',
    borderColor: 'border-blue-400'
  },
  [AgentState.COMPLETED]: {
    icon: Check,
    color: 'green',
    bgColor: 'bg-green-100',
    textColor: 'text-green-600',
    borderColor: 'border-green-400'
  },
  [AgentState.ERROR]: {
    icon: AlertCircle,
    color: 'red',
    bgColor: 'bg-red-100',
    textColor: 'text-red-600',
    borderColor: 'border-red-400'
  }
}

const AgentPipeline: React.FC<AgentPipelineProps> = ({ steps, currentStep = 0 }) => {
  return (
    <div className="space-y-4">
      {steps.map((step, index) => {
        const config = stateConfig[step.state]
        const StepIcon = step.icon
        const StateIcon = config.icon
        const isActive = index === currentStep

        return (
          <motion.div
            key={step.id}
            className="relative"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1, ease: [0.22, 1, 0.36, 1] }}
          >
            {/* Connector line */}
            {index < steps.length - 1 && (
              <div className="absolute left-6 top-16 bottom-0 w-0.5 -translate-x-1/2">
                <div className="h-full bg-gray-200" />
                {step.state === AgentState.COMPLETED && (
                  <motion.div
                    className="absolute top-0 w-full bg-gradient-to-b from-green-500 to-blue-500"
                    initial={{ height: '0%' }}
                    animate={{ height: '100%' }}
                    transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                  />
                )}
              </div>
            )}

            {/* Agent Card */}
            <motion.div
              className={`relative p-6 rounded-2xl bg-white/80 backdrop-blur-sm border-2 ${
                isActive ? config.borderColor : 'border-gray-200'
              } shadow-soft hover:shadow-medium transition-all duration-300 overflow-hidden`}
              whileHover={{ y: -2 }}
              animate={
                step.state === AgentState.RUNNING
                  ? {
                      boxShadow: [
                        '0 2px 15px rgba(0, 0, 0, 0.08)',
                        '0 4px 20px rgba(37, 99, 235, 0.15)',
                        '0 2px 15px rgba(0, 0, 0, 0.08)'
                      ]
                    }
                  : {}
              }
              transition={{
                boxShadow: {
                  duration: 2,
                  repeat: Infinity,
                  ease: 'easeInOut'
                }
              }}
            >
              {/* Animated gradient background for active step */}
              {step.state === AgentState.RUNNING && (
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-blue-500/5"
                  animate={{
                    backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: 'linear'
                  }}
                  style={{
                    backgroundSize: '200% 100%'
                  }}
                />
              )}

              <div className="relative z-10 flex items-start gap-4">
                {/* Step Icon */}
                <motion.div
                  className={`flex-shrink-0 w-12 h-12 rounded-xl ${config.bgColor} flex items-center justify-center`}
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  transition={{ type: 'spring', stiffness: 400, damping: 10 }}
                >
                  <StepIcon className={`w-6 h-6 ${config.textColor}`} />
                </motion.div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {step.name}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {step.description}
                      </p>
                    </div>

                    {/* State indicator */}
                    <motion.div
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg ${config.bgColor} ${config.textColor} text-xs font-medium whitespace-nowrap`}
                      initial={{ scale: 0.9, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ duration: 0.3 }}
                    >
                      <StateIcon
                        className={`w-3.5 h-3.5 ${
                          step.state === AgentState.RUNNING ? 'animate-spin' : ''
                        }`}
                      />
                      {step.state.charAt(0).toUpperCase() + step.state.slice(1)}
                    </motion.div>
                  </div>

                  {/* Progress bar */}
                  {step.state === AgentState.RUNNING && step.progress !== undefined && (
                    <div className="mt-4">
                      <div className="flex items-center justify-between text-xs text-gray-600 mb-2">
                        <span>{step.message || 'Processing...'}</span>
                        <span className="font-medium">{step.progress}%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${step.progress}%` }}
                          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                        />
                      </div>
                      {step.eta !== undefined && step.eta > 0 && (
                        <p className="text-xs text-gray-500 mt-2">
                          Estimated time: {Math.ceil(step.eta / 60)} min
                        </p>
                      )}
                    </div>
                  )}

                  {/* Completed message */}
                  {step.state === AgentState.COMPLETED && step.message && (
                    <motion.div
                      className="mt-4 p-3 rounded-lg bg-green-50 border border-green-200 text-sm text-green-800"
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      {step.message}
                    </motion.div>
                  )}

                  {/* Error message */}
                  {step.state === AgentState.ERROR && step.message && (
                    <motion.div
                      className="mt-4 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-800"
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      {step.message}
                    </motion.div>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )
      })}
    </div>
  )
}

export default AgentPipeline

// Example usage export
export const exampleSteps: AgentStep[] = [
  {
    id: 'search',
    name: 'Search Agent',
    description: 'Searching academic databases for relevant papers',
    icon: Search,
    state: AgentState.COMPLETED,
    message: 'Found 234 papers across 4 databases'
  },
  {
    id: 'screening',
    name: 'Screening Agent',
    description: 'Filtering papers based on inclusion/exclusion criteria',
    icon: Filter,
    state: AgentState.RUNNING,
    progress: 67,
    eta: 180,
    message: 'Screening papers (157/234)'
  },
  {
    id: 'quality',
    name: 'Quality Assessment Agent',
    description: 'Evaluating study quality and credibility',
    icon: CheckCircle2,
    state: AgentState.PENDING
  },
  {
    id: 'extraction',
    name: 'Data Extraction Agent',
    description: 'Extracting key data points from included studies',
    icon: Brain,
    state: AgentState.PENDING
  },
  {
    id: 'analysis',
    name: 'Statistical Analysis Agent',
    description: 'Performing meta-analysis and generating visualizations',
    icon: BarChart3,
    state: AgentState.PENDING
  },
  {
    id: 'report',
    name: 'Report Generation Agent',
    description: 'Creating comprehensive PRISMA-compliant report',
    icon: FileText,
    state: AgentState.PENDING
  }
]
