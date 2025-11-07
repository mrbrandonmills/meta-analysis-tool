/**
 * Dashboard API Service
 * Handles all dashboard-related API calls
 */

import axios from 'axios';
import { Project, DashboardStats, ActivityItem, NotificationMessage, ApiResponse, PaginatedResponse } from '@/lib/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ===========================
// DASHBOARD API
// ===========================

export interface DashboardFilters {
  status?: string[];
  toolType?: string[];
  dateFrom?: Date;
  dateTo?: Date;
  search?: string;
}

export interface ProjectListParams {
  page?: number;
  pageSize?: number;
  sortBy?: 'updatedAt' | 'createdAt' | 'title' | 'status';
  sortOrder?: 'asc' | 'desc';
  filters?: DashboardFilters;
}

/**
 * Get dashboard statistics and overview
 */
export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await api.get<ApiResponse<DashboardStats>>('/dashboard/stats');
  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to fetch dashboard stats');
  }
  return response.data.data!;
};

/**
 * Get paginated list of projects with filters
 */
export const getProjects = async (params: ProjectListParams = {}): Promise<PaginatedResponse<Project>> => {
  const response = await api.get<ApiResponse<PaginatedResponse<Project>>>('/projects', {
    params: {
      page: params.page || 1,
      pageSize: params.pageSize || 10,
      sortBy: params.sortBy || 'updatedAt',
      sortOrder: params.sortOrder || 'desc',
      ...params.filters,
    },
  });
  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to fetch projects');
  }
  return response.data.data!;
};

/**
 * Get single project by ID with full details
 */
export const getProject = async (projectId: string): Promise<Project> => {
  const response = await api.get<ApiResponse<Project>>(`/projects/${projectId}`);
  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to fetch project');
  }
  return response.data.data!;
};

/**
 * Get recent activity for dashboard
 */
export const getRecentActivity = async (limit: number = 10): Promise<ActivityItem[]> => {
  const response = await api.get<ApiResponse<ActivityItem[]>>('/dashboard/activity', {
    params: { limit },
  });
  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to fetch activity');
  }
  return response.data.data!;
};

/**
 * Get notifications for current user
 */
export const getNotifications = async (unreadOnly: boolean = false): Promise<NotificationMessage[]> => {
  const response = await api.get<ApiResponse<NotificationMessage[]>>('/notifications', {
    params: { unreadOnly },
  });
  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to fetch notifications');
  }
  return response.data.data!;
};

/**
 * Mark notification as read
 */
export const markNotificationRead = async (notificationId: string): Promise<void> => {
  const response = await api.patch<ApiResponse>(`/notifications/${notificationId}/read`);
  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to mark notification as read');
  }
};

/**
 * Mark all notifications as read
 */
export const markAllNotificationsRead = async (): Promise<void> => {
  const response = await api.patch<ApiResponse>('/notifications/read-all');
  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to mark notifications as read');
  }
};

/**
 * Delete project
 */
export const deleteProject = async (projectId: string): Promise<void> => {
  const response = await api.delete<ApiResponse>(`/projects/${projectId}`);
  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to delete project');
  }
};

/**
 * Clone project
 */
export const cloneProject = async (projectId: string): Promise<Project> => {
  const response = await api.post<ApiResponse<Project>>(`/projects/${projectId}/clone`);
  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to clone project');
  }
  return response.data.data!;
};

/**
 * Pause project execution
 */
export const pauseProject = async (projectId: string): Promise<Project> => {
  const response = await api.post<ApiResponse<Project>>(`/projects/${projectId}/pause`);
  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to pause project');
  }
  return response.data.data!;
};

/**
 * Resume project execution
 */
export const resumeProject = async (projectId: string): Promise<Project> => {
  const response = await api.post<ApiResponse<Project>>(`/projects/${projectId}/resume`);
  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to resume project');
  }
  return response.data.data!;
};

/**
 * Export project data
 */
export const exportProject = async (projectId: string, format: 'json' | 'csv' | 'pdf'): Promise<Blob> => {
  const response = await api.get(`/projects/${projectId}/export`, {
    params: { format },
    responseType: 'blob',
  });
  return response.data;
};

/**
 * Get analytics data for charts
 */
export interface AnalyticsData {
  projectsByMonth: Array<{ month: string; count: number }>;
  projectsByTool: Array<{ tool: string; count: number; percentage: number }>;
  projectsByStatus: Array<{ status: string; count: number; percentage: number }>;
  studiesScreened: Array<{ date: string; count: number }>;
  completionTimes: Array<{ project: string; duration: number }>;
  successRate: {
    completed: number;
    failed: number;
    rate: number;
  };
}

export const getAnalytics = async (timeRange: '7d' | '30d' | '90d' | '1y' = '30d'): Promise<AnalyticsData> => {
  const response = await api.get<ApiResponse<AnalyticsData>>('/dashboard/analytics', {
    params: { timeRange },
  });
  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to fetch analytics');
  }
  return response.data.data!;
};

export default api;
