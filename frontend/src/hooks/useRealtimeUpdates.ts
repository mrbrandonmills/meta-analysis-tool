/**
 * Real-time Updates Hook
 * Provides polling-based real-time updates for projects and notifications
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { useAppStore } from '@/stores/useAppStore'
import { getProjects, getNotifications, getProject } from '@/lib/api/dashboard'
import { Project, NotificationMessage } from '@/lib/types'

interface UseRealtimeUpdatesOptions {
  enabled?: boolean
  projectId?: string // If provided, polls specific project
  pollingInterval?: number // milliseconds
  onProjectUpdate?: (project: Project) => void
  onNewNotification?: (notification: NotificationMessage) => void
}

export const useRealtimeUpdates = (options: UseRealtimeUpdatesOptions = {}) => {
  const {
    enabled = true,
    projectId,
    pollingInterval = 5000, // 5 seconds default
    onProjectUpdate,
    onNewNotification,
  } = options

  const { setProjects, updateProject, addNotification, notifications } = useAppStore()
  const [isPolling, setIsPolling] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const previousNotificationIds = useRef<Set<string>>(
    new Set(notifications.map((n) => n.id))
  )

  /**
   * Poll for project updates
   */
  const pollProjects = useCallback(async () => {
    if (!enabled) return

    try {
      setIsPolling(true)
      setError(null)

      if (projectId) {
        // Poll specific project
        const project = await getProject(projectId)
        updateProject(projectId, project)
        onProjectUpdate?.(project)
      } else {
        // Poll all projects
        const response = await getProjects({ pageSize: 100 })
        setProjects(response.items)
      }

      setLastUpdate(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch updates')
      console.error('Polling error:', err)
    } finally {
      setIsPolling(false)
    }
  }, [enabled, projectId, updateProject, setProjects, onProjectUpdate])

  /**
   * Poll for new notifications
   */
  const pollNotifications = useCallback(async () => {
    if (!enabled) return

    try {
      const newNotifications = await getNotifications(true) // unread only

      // Check for new notifications
      newNotifications.forEach((notification) => {
        if (!previousNotificationIds.current.has(notification.id)) {
          addNotification({
            type: notification.type,
            title: notification.title,
            message: notification.message,
            actionUrl: notification.actionUrl,
          })
          onNewNotification?.(notification)
          previousNotificationIds.current.add(notification.id)
        }
      })
    } catch (err) {
      console.error('Notification polling error:', err)
    }
  }, [enabled, addNotification, onNewNotification])

  /**
   * Start polling
   */
  const startPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }

    // Initial fetch
    pollProjects()
    pollNotifications()

    // Set up interval
    intervalRef.current = setInterval(() => {
      pollProjects()
      pollNotifications()
    }, pollingInterval)
  }, [pollProjects, pollNotifications, pollingInterval])

  /**
   * Stop polling
   */
  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  /**
   * Manual refresh
   */
  const refresh = useCallback(async () => {
    await pollProjects()
    await pollNotifications()
  }, [pollProjects, pollNotifications])

  // Auto-start/stop polling based on enabled flag
  useEffect(() => {
    if (enabled) {
      startPolling()
    } else {
      stopPolling()
    }

    return () => {
      stopPolling()
    }
  }, [enabled, startPolling, stopPolling])

  // Handle visibility change (pause when tab not visible)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        stopPolling()
      } else if (enabled) {
        startPolling()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [enabled, startPolling, stopPolling])

  return {
    isPolling,
    error,
    lastUpdate,
    refresh,
    startPolling,
    stopPolling,
  }
}

/**
 * Hook for monitoring specific project progress
 */
export const useProjectProgress = (projectId: string | undefined) => {
  const [project, setProject] = useState<Project | null>(null)
  const [progress, setProgress] = useState(0)
  const [isComplete, setIsComplete] = useState(false)

  const { isPolling, error, refresh } = useRealtimeUpdates({
    enabled: !!projectId,
    projectId,
    pollingInterval: 3000, // Poll more frequently for progress
    onProjectUpdate: (updatedProject) => {
      setProject(updatedProject)

      // Calculate overall progress
      const workflows = updatedProject.workflows || []
      if (workflows.length > 0) {
        const totalProgress = workflows.reduce((sum, w) => sum + (w.progress || 0), 0)
        const avgProgress = totalProgress / workflows.length
        setProgress(avgProgress)
      }

      // Check if complete
      setIsComplete(updatedProject.status === 'completed')
    },
  })

  return {
    project,
    progress,
    isComplete,
    isPolling,
    error,
    refresh,
  }
}

/**
 * Hook for real-time analytics updates
 */
export const useAnalyticsUpdates = (timeRange: '7d' | '30d' | '90d' | '1y' = '30d') => {
  const [analyticsData, setAnalyticsData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const { isPolling, error, refresh } = useRealtimeUpdates({
    enabled: true,
    pollingInterval: 30000, // Poll every 30 seconds for analytics
  })

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true)
        // Fetch analytics data
        // const data = await getAnalytics(timeRange)
        // setAnalyticsData(data)
      } catch (err) {
        console.error('Failed to fetch analytics:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [timeRange])

  return {
    analyticsData,
    loading: loading || isPolling,
    error,
    refresh,
  }
}

export default useRealtimeUpdates
