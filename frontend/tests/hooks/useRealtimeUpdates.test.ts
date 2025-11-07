import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { useRealtimeUpdates, useProjectProgress } from '@/hooks/useRealtimeUpdates'
import * as dashboardApi from '@/lib/api/dashboard'
import { ProjectStatus } from '@/lib/types'

// Mock the API
vi.mock('@/lib/api/dashboard')

// Mock the store
vi.mock('@/stores/useAppStore', () => ({
  useAppStore: () => ({
    setProjects: vi.fn(),
    updateProject: vi.fn(),
    addNotification: vi.fn(),
    notifications: [],
  }),
}))

describe('useRealtimeUpdates', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('initializes with default values', () => {
    const { result } = renderHook(() => useRealtimeUpdates({ enabled: false }))

    expect(result.current.isPolling).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.lastUpdate).toBeInstanceOf(Date)
  })

  it('starts polling when enabled', async () => {
    const mockGetProjects = vi.mocked(dashboardApi.getProjects)
    mockGetProjects.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      pageSize: 100,
      totalPages: 1,
    })

    const mockGetNotifications = vi.mocked(dashboardApi.getNotifications)
    mockGetNotifications.mockResolvedValue([])

    renderHook(() => useRealtimeUpdates({ enabled: true, pollingInterval: 1000 }))

    // Wait for initial fetch
    await waitFor(() => {
      expect(mockGetProjects).toHaveBeenCalledTimes(1)
      expect(mockGetNotifications).toHaveBeenCalledTimes(1)
    })

    // Advance timer to trigger polling
    act(() => {
      vi.advanceTimersByTime(1000)
    })

    await waitFor(() => {
      expect(mockGetProjects).toHaveBeenCalledTimes(2)
      expect(mockGetNotifications).toHaveBeenCalledTimes(2)
    })
  })

  it('does not poll when disabled', async () => {
    const mockGetProjects = vi.mocked(dashboardApi.getProjects)

    renderHook(() => useRealtimeUpdates({ enabled: false }))

    act(() => {
      vi.advanceTimersByTime(10000)
    })

    expect(mockGetProjects).not.toHaveBeenCalled()
  })

  it('polls specific project when projectId provided', async () => {
    const mockGetProject = vi.mocked(dashboardApi.getProject)
    mockGetProject.mockResolvedValue({
      id: '1',
      userId: 'user1',
      toolType: 'meta_analysis',
      title: 'Test Project',
      status: ProjectStatus.IN_PROGRESS,
      workflows: [],
      auditTrail: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    } as any)

    const mockGetNotifications = vi.mocked(dashboardApi.getNotifications)
    mockGetNotifications.mockResolvedValue([])

    renderHook(() =>
      useRealtimeUpdates({
        enabled: true,
        projectId: '1',
        pollingInterval: 1000,
      })
    )

    await waitFor(() => {
      expect(mockGetProject).toHaveBeenCalledWith('1')
    })
  })

  it('calls onProjectUpdate callback when project updates', async () => {
    const mockGetProject = vi.mocked(dashboardApi.getProject)
    const mockProject = {
      id: '1',
      userId: 'user1',
      toolType: 'meta_analysis',
      title: 'Test Project',
      status: ProjectStatus.IN_PROGRESS,
      workflows: [],
      auditTrail: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    mockGetProject.mockResolvedValue(mockProject as any)

    const mockGetNotifications = vi.mocked(dashboardApi.getNotifications)
    mockGetNotifications.mockResolvedValue([])

    const onProjectUpdate = vi.fn()

    renderHook(() =>
      useRealtimeUpdates({
        enabled: true,
        projectId: '1',
        pollingInterval: 1000,
        onProjectUpdate,
      })
    )

    await waitFor(() => {
      expect(onProjectUpdate).toHaveBeenCalledWith(mockProject)
    })
  })

  it('calls onNewNotification callback for new notifications', async () => {
    const mockGetProjects = vi.mocked(dashboardApi.getProjects)
    mockGetProjects.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      pageSize: 100,
      totalPages: 1,
    })

    const newNotification = {
      id: 'new1',
      type: 'success' as const,
      title: 'New Notification',
      message: 'Test message',
      timestamp: new Date(),
      read: false,
    }

    const mockGetNotifications = vi.mocked(dashboardApi.getNotifications)
    mockGetNotifications.mockResolvedValue([newNotification])

    const onNewNotification = vi.fn()

    renderHook(() =>
      useRealtimeUpdates({
        enabled: true,
        pollingInterval: 1000,
        onNewNotification,
      })
    )

    await waitFor(() => {
      expect(onNewNotification).toHaveBeenCalledWith(newNotification)
    })
  })

  it('handles API errors gracefully', async () => {
    const mockGetProjects = vi.mocked(dashboardApi.getProjects)
    mockGetProjects.mockRejectedValue(new Error('API Error'))

    const { result } = renderHook(() =>
      useRealtimeUpdates({ enabled: true, pollingInterval: 1000 })
    )

    await waitFor(() => {
      expect(result.current.error).toBe('API Error')
    })
  })

  it('manual refresh triggers immediate update', async () => {
    const mockGetProjects = vi.mocked(dashboardApi.getProjects)
    mockGetProjects.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      pageSize: 100,
      totalPages: 1,
    })

    const mockGetNotifications = vi.mocked(dashboardApi.getNotifications)
    mockGetNotifications.mockResolvedValue([])

    const { result } = renderHook(() =>
      useRealtimeUpdates({ enabled: false })
    )

    await act(async () => {
      await result.current.refresh()
    })

    expect(mockGetProjects).toHaveBeenCalled()
    expect(mockGetNotifications).toHaveBeenCalled()
  })

  it('stops polling when component unmounts', async () => {
    const mockGetProjects = vi.mocked(dashboardApi.getProjects)
    mockGetProjects.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      pageSize: 100,
      totalPages: 1,
    })

    const mockGetNotifications = vi.mocked(dashboardApi.getNotifications)
    mockGetNotifications.mockResolvedValue([])

    const { unmount } = renderHook(() =>
      useRealtimeUpdates({ enabled: true, pollingInterval: 1000 })
    )

    await waitFor(() => {
      expect(mockGetProjects).toHaveBeenCalled()
    })

    unmount()

    const callCount = mockGetProjects.mock.calls.length

    act(() => {
      vi.advanceTimersByTime(5000)
    })

    // Should not have made additional calls after unmount
    expect(mockGetProjects).toHaveBeenCalledTimes(callCount)
  })

  it('pauses polling when document is hidden', async () => {
    const mockGetProjects = vi.mocked(dashboardApi.getProjects)
    mockGetProjects.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      pageSize: 100,
      totalPages: 1,
    })

    const mockGetNotifications = vi.mocked(dashboardApi.getNotifications)
    mockGetNotifications.mockResolvedValue([])

    renderHook(() =>
      useRealtimeUpdates({ enabled: true, pollingInterval: 1000 })
    )

    await waitFor(() => {
      expect(mockGetProjects).toHaveBeenCalled()
    })

    // Simulate document becoming hidden
    Object.defineProperty(document, 'hidden', {
      configurable: true,
      get: () => true,
    })

    const event = new Event('visibilitychange')
    document.dispatchEvent(event)

    const callCount = mockGetProjects.mock.calls.length

    act(() => {
      vi.advanceTimersByTime(5000)
    })

    // Should not poll while hidden
    expect(mockGetProjects).toHaveBeenCalledTimes(callCount)
  })
})

describe('useProjectProgress', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('calculates progress from workflows', async () => {
    const mockGetProject = vi.mocked(dashboardApi.getProject)
    mockGetProject.mockResolvedValue({
      id: '1',
      userId: 'user1',
      toolType: 'meta_analysis',
      title: 'Test Project',
      status: ProjectStatus.IN_PROGRESS,
      workflows: [
        { progress: 50 } as any,
        { progress: 75 } as any,
        { progress: 100 } as any,
      ],
      auditTrail: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    } as any)

    const mockGetNotifications = vi.mocked(dashboardApi.getNotifications)
    mockGetNotifications.mockResolvedValue([])

    const { result } = renderHook(() => useProjectProgress('1'))

    await waitFor(() => {
      expect(result.current.progress).toBe(75) // Average of 50, 75, 100
    })
  })

  it('detects when project is complete', async () => {
    const mockGetProject = vi.mocked(dashboardApi.getProject)
    mockGetProject.mockResolvedValue({
      id: '1',
      userId: 'user1',
      toolType: 'meta_analysis',
      title: 'Test Project',
      status: ProjectStatus.COMPLETED,
      workflows: [],
      auditTrail: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    } as any)

    const mockGetNotifications = vi.mocked(dashboardApi.getNotifications)
    mockGetNotifications.mockResolvedValue([])

    const { result } = renderHook(() => useProjectProgress('1'))

    await waitFor(() => {
      expect(result.current.isComplete).toBe(true)
    })
  })

  it('does not poll when projectId is undefined', async () => {
    const mockGetProject = vi.mocked(dashboardApi.getProject)

    renderHook(() => useProjectProgress(undefined))

    act(() => {
      vi.advanceTimersByTime(10000)
    })

    expect(mockGetProject).not.toHaveBeenCalled()
  })
})
