'use client'

import React, { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, CheckCircle2, AlertCircle, Info, AlertTriangle } from 'lucide-react'

export enum ToastType {
  SUCCESS = 'success',
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info'
}

export interface ToastProps {
  id: string
  type: ToastType
  title: string
  message?: string
  duration?: number
  onClose: (id: string) => void
}

const typeConfig = {
  [ToastType.SUCCESS]: {
    icon: CheckCircle2,
    color: 'green',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    iconColor: 'text-green-600',
    titleColor: 'text-green-900',
    messageColor: 'text-green-700'
  },
  [ToastType.ERROR]: {
    icon: AlertCircle,
    color: 'red',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    iconColor: 'text-red-600',
    titleColor: 'text-red-900',
    messageColor: 'text-red-700'
  },
  [ToastType.WARNING]: {
    icon: AlertTriangle,
    color: 'yellow',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    iconColor: 'text-yellow-600',
    titleColor: 'text-yellow-900',
    messageColor: 'text-yellow-700'
  },
  [ToastType.INFO]: {
    icon: Info,
    color: 'blue',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    iconColor: 'text-blue-600',
    titleColor: 'text-blue-900',
    messageColor: 'text-blue-700'
  }
}

const Toast: React.FC<ToastProps> = ({
  id,
  type,
  title,
  message,
  duration = 5000,
  onClose
}) => {
  const config = typeConfig[type]
  const Icon = config.icon

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose(id)
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [id, duration, onClose])

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
      className={`relative flex items-start gap-3 p-4 rounded-xl ${config.bgColor} border ${config.borderColor} shadow-lg backdrop-blur-sm max-w-md w-full`}
    >
      {/* Icon */}
      <div className={`flex-shrink-0 ${config.iconColor}`}>
        <Icon className="w-5 h-5" />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-semibold ${config.titleColor}`}>
          {title}
        </p>
        {message && (
          <p className={`text-sm ${config.messageColor} mt-1`}>
            {message}
          </p>
        )}
      </div>

      {/* Close button */}
      <motion.button
        className={`flex-shrink-0 ${config.iconColor} hover:opacity-70 transition-opacity`}
        onClick={() => onClose(id)}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        <X className="w-4 h-4" />
      </motion.button>

      {/* Progress bar */}
      {duration > 0 && (
        <motion.div
          className={`absolute bottom-0 left-0 right-0 h-1 bg-${config.color}-500 rounded-b-xl`}
          initial={{ scaleX: 1 }}
          animate={{ scaleX: 0 }}
          transition={{ duration: duration / 1000, ease: 'linear' }}
          style={{ transformOrigin: 'left' }}
        />
      )}
    </motion.div>
  )
}

// Toast container component
export const ToastContainer: React.FC<{ toasts: ToastProps[] }> = ({ toasts }) => {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-3">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <Toast key={toast.id} {...toast} />
        ))}
      </AnimatePresence>
    </div>
  )
}

export default Toast
