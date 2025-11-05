'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { Shield, ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react'

export enum CredibilityLevel {
  VERY_LOW = 'VERY_LOW',
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH'
}

interface CredibilityBadgeProps {
  level: CredibilityLevel
  score?: number
  showScore?: boolean
  size?: 'sm' | 'md' | 'lg'
  animated?: boolean
}

const levelConfig = {
  [CredibilityLevel.VERY_LOW]: {
    label: 'Very Low',
    icon: ShieldX,
    color: 'red',
    bgColor: 'bg-red-100',
    textColor: 'text-red-700',
    borderColor: 'border-red-300',
    gradient: 'from-red-500 to-red-600'
  },
  [CredibilityLevel.LOW]: {
    label: 'Low',
    icon: ShieldAlert,
    color: 'orange',
    bgColor: 'bg-orange-100',
    textColor: 'text-orange-700',
    borderColor: 'border-orange-300',
    gradient: 'from-orange-500 to-orange-600'
  },
  [CredibilityLevel.MEDIUM]: {
    label: 'Medium',
    icon: Shield,
    color: 'yellow',
    bgColor: 'bg-yellow-100',
    textColor: 'text-yellow-700',
    borderColor: 'border-yellow-300',
    gradient: 'from-yellow-500 to-yellow-600'
  },
  [CredibilityLevel.HIGH]: {
    label: 'High',
    icon: ShieldCheck,
    color: 'green',
    bgColor: 'bg-green-100',
    textColor: 'text-green-700',
    borderColor: 'border-green-300',
    gradient: 'from-green-500 to-green-600'
  }
}

const sizeConfig = {
  sm: {
    padding: 'px-2 py-1',
    text: 'text-xs',
    icon: 'w-3 h-3'
  },
  md: {
    padding: 'px-3 py-1.5',
    text: 'text-sm',
    icon: 'w-4 h-4'
  },
  lg: {
    padding: 'px-4 py-2',
    text: 'text-base',
    icon: 'w-5 h-5'
  }
}

const CredibilityBadge: React.FC<CredibilityBadgeProps> = ({
  level,
  score,
  showScore = true,
  size = 'md',
  animated = true
}) => {
  const config = levelConfig[level]
  const sizeStyles = sizeConfig[size]
  const Icon = config.icon

  const badge = (
    <div
      className={`inline-flex items-center gap-1.5 ${sizeStyles.padding} rounded-lg ${config.bgColor} ${config.textColor} border ${config.borderColor} font-medium ${sizeStyles.text}`}
    >
      <Icon className={sizeStyles.icon} />
      <span>{config.label}</span>
      {showScore && score !== undefined && (
        <span className="ml-1 opacity-75">({score}/100)</span>
      )}
    </div>
  )

  if (!animated) {
    return badge
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
    >
      {badge}
    </motion.div>
  )
}

export default CredibilityBadge
