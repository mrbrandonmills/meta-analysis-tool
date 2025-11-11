/**
 * Progress Tracking Hook
 * Provides real-time progress updates with time estimation for long-running tasks
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { apiClient } from '@/lib/api'

export interface ProgressStep {
  name: string
  status: 'pending' | 'running' | 'completed' | 'error'
  message?: string
}

export interface ProgressData {
  progress: number // 0-100
  status: 'pending' | 'running' | 'completed' | 'error'
  estimated_time_remaining: number // seconds
  current_step: string
  steps_completed: string[]
  steps_remaining: string[]
  started_at: string | null
  estimated_completion: string | null
  message?: string
}

interface UseProgressTrackingOptions {
  taskId: string | null
  taskType: 'meta-analysis' | 'peer-review' | 'reviewer-matcher'
  pollingInterval?: number // milliseconds
  enabled?: boolean
  onComplete?: (data: ProgressData) => void
  onError?: (error: string) => void
  onProgressUpdate?: (data: ProgressData) => void
}

export function useProgressTracking(options: UseProgressTrackingOptions) {
  const {
    taskId,
    taskType,
    pollingInterval = 2000,
    enabled = true,
    onComplete,
    onError,
    onProgressUpdate,
  } = options

  const [progress, setProgress] = useState<number>(0)
  const [status, setStatus] = useState<ProgressData['status']>('pending')
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState<number>(0)
  const [currentStep, setCurrentStep] = useState<string>('')
  const [stepsCompleted, setStepsCompleted] = useState<string[]>([])
  const [stepsRemaining, setStepsRemaining] = useState<string[]>([])
  const [startedAt, setStartedAt] = useState<string | null>(null)
  const [estimatedCompletion, setEstimatedCompletion] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isPolling, setIsPolling] = useState<boolean>(false)

  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const completedRef = useRef<boolean>(false)

  /**
   * Fetch progress from backend
   */
  const fetchProgress = useCallback(async () => {
    if (!taskId || !enabled || completedRef.current) return

    try {
      setIsPolling(true)
      const response = await apiClient.get<ProgressData>(
        `/tasks/${taskId}/progress?type=${taskType}`
      )

      const data = response.data

      // Update state
      setProgress(data.progress)
      setStatus(data.status)
      setEstimatedTimeRemaining(data.estimated_time_remaining)
      setCurrentStep(data.current_step)
      setStepsCompleted(data.steps_completed)
      setStepsRemaining(data.steps_remaining)
      setStartedAt(data.started_at)
      setEstimatedCompletion(data.estimated_completion)
      setError(null)

      // Call progress update callback
      onProgressUpdate?.(data)

      // Handle completion
      if (data.status === 'completed') {
        completedRef.current = true
        stopPolling()
        onComplete?.(data)
      }

      // Handle error
      if (data.status === 'error') {
        completedRef.current = true
        stopPolling()
        setError(data.message || 'Task failed')
        onError?.(data.message || 'Task failed')
      }
    } catch (err: any) {
      console.error('Failed to fetch progress:', err)
      setError(err.response?.data?.detail || 'Failed to fetch progress')
    } finally {
      setIsPolling(false)
    }
  }, [taskId, taskType, enabled, onComplete, onError, onProgressUpdate])

  /**
   * Start polling for progress
   */
  const startPolling = useCallback(() => {
    if (!taskId || !enabled) return

    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }

    // Reset completion flag
    completedRef.current = false

    // Initial fetch
    fetchProgress()

    // Set up polling interval
    intervalRef.current = setInterval(() => {
      fetchProgress()
    }, pollingInterval)
  }, [taskId, enabled, fetchProgress, pollingInterval])

  /**
   * Stop polling
   */
  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    setIsPolling(false)
  }, [])

  /**
   * Refresh progress manually
   */
  const refresh = useCallback(() => {
    fetchProgress()
  }, [fetchProgress])

  /**
   * Reset state
   */
  const reset = useCallback(() => {
    stopPolling()
    setProgress(0)
    setStatus('pending')
    setEstimatedTimeRemaining(0)
    setCurrentStep('')
    setStepsCompleted([])
    setStepsRemaining([])
    setStartedAt(null)
    setEstimatedCompletion(null)
    setError(null)
    completedRef.current = false
  }, [stopPolling])

  /**
   * Format time remaining
   */
  const formatTimeRemaining = useCallback((): string => {
    if (estimatedTimeRemaining <= 0) return '0 seconds'

    const hours = Math.floor(estimatedTimeRemaining / 3600)
    const minutes = Math.floor((estimatedTimeRemaining % 3600) / 60)
    const seconds = estimatedTimeRemaining % 60

    const parts: string[] = []
    if (hours > 0) parts.push(`${hours} hour${hours !== 1 ? 's' : ''}`)
    if (minutes > 0) parts.push(`${minutes} minute${minutes !== 1 ? 's' : ''}`)
    if (seconds > 0 && hours === 0) parts.push(`${seconds} second${seconds !== 1 ? 's' : ''}`)

    return parts.join(' ')
  }, [estimatedTimeRemaining])

  /**
   * Get completion percentage
   */
  const getCompletionPercentage = useCallback((): string => {
    return `${Math.round(progress)}%`
  }, [progress])

  // Auto-start polling when taskId is set and enabled
  useEffect(() => {
    if (taskId && enabled) {
      startPolling()
    } else {
      stopPolling()
    }

    return () => {
      stopPolling()
    }
  }, [taskId, enabled, startPolling, stopPolling])

  // Handle visibility change (pause when tab not visible)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        stopPolling()
      } else if (taskId && enabled && !completedRef.current) {
        startPolling()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [taskId, enabled, startPolling, stopPolling])

  return {
    // State
    progress,
    status,
    estimatedTimeRemaining,
    currentStep,
    stepsCompleted,
    stepsRemaining,
    startedAt,
    estimatedCompletion,
    error,
    isPolling,

    // Methods
    startPolling,
    stopPolling,
    refresh,
    reset,

    // Computed
    formatTimeRemaining,
    getCompletionPercentage,
    isComplete: status === 'completed',
    isRunning: status === 'running',
    hasError: status === 'error',
  }
}

export default useProgressTracking
