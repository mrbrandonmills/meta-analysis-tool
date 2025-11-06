import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import toast from 'react-hot-toast';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_VERSION = 'v1';

// Token storage keys
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    // Handle 401 Unauthorized - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = getRefreshToken();
        if (refreshToken) {
          const response = await axios.post(
            `${API_BASE_URL}/api/${API_VERSION}/auth/refresh`,
            { refresh_token: refreshToken }
          );

          const { access_token } = response.data;
          setAccessToken(access_token);

          // Retry original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed - clear tokens and redirect to login
        clearTokens();
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    // Handle 429 Rate Limit
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'];
      toast.error(
        `Rate limit exceeded. Please try again in ${retryAfter || 60} seconds.`,
        { duration: 5000 }
      );
    }

    // Handle other errors
    handleApiError(error);
    return Promise.reject(error);
  }
);

// Error handler
function handleApiError(error: AxiosError): void {
  if (error.response) {
    // Server responded with error
    const data = error.response.data as any;
    const message = data?.message || data?.detail || 'An error occurred';

    switch (error.response.status) {
      case 400:
        toast.error(`Bad Request: ${message}`);
        break;
      case 403:
        toast.error('Access denied. You do not have permission.');
        break;
      case 404:
        toast.error('Resource not found.');
        break;
      case 500:
        toast.error('Server error. Please try again later.');
        break;
      default:
        toast.error(message);
    }
  } else if (error.request) {
    // Request made but no response
    toast.error('Network error. Please check your connection.');
  } else {
    // Something else happened
    toast.error('An unexpected error occurred.');
  }
}

// Token management
export function getAccessToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }
  return null;
}

export function getRefreshToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }
  return null;
}

export function setAccessToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(ACCESS_TOKEN_KEY, token);
  }
}

export function setRefreshToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  }
}

export function setTokens(accessToken: string, refreshToken: string): void {
  setAccessToken(accessToken);
  setRefreshToken(refreshToken);
}

export function clearTokens(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

// ==================
// AUTH API
// ==================

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  institution?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
  };
}

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    const { access_token, refresh_token } = response.data;
    setTokens(access_token, refresh_token);

    return response.data;
  },

  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await apiClient.post('/auth/register', data);
    const { access_token, refresh_token } = response.data;
    setTokens(access_token, refresh_token);
    return response.data;
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      clearTokens();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};

// ==================
// PROJECTS API
// ==================

export const projectsApi = {
  list: async (params?: { tool_type?: string; status?: string }) => {
    const response = await apiClient.get('/projects', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await apiClient.get(`/projects/${id}`);
    return response.data;
  },

  create: async (data: any) => {
    const response = await apiClient.post('/projects', data);
    return response.data;
  },

  update: async (id: string, data: any) => {
    const response = await apiClient.put(`/projects/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    const response = await apiClient.delete(`/projects/${id}`);
    return response.data;
  },

  pause: async (id: string) => {
    const response = await apiClient.post(`/projects/${id}/pause`);
    return response.data;
  },

  resume: async (id: string) => {
    const response = await apiClient.post(`/projects/${id}/resume`);
    return response.data;
  },

  cancel: async (id: string) => {
    const response = await apiClient.post(`/projects/${id}/cancel`);
    return response.data;
  },
};

// ==================
// META-ANALYSIS API
// ==================

export const metaAnalysisApi = {
  search: async (projectId: string, searchParams: any) => {
    const response = await apiClient.post(
      `/meta-analysis/${projectId}/search`,
      searchParams
    );
    return response.data;
  },

  screen: async (projectId: string) => {
    const response = await apiClient.post(
      `/meta-analysis/${projectId}/screen`
    );
    return response.data;
  },

  assessCredibility: async (projectId: string) => {
    const response = await apiClient.post(
      `/meta-analysis/${projectId}/credibility`
    );
    return response.data;
  },

  extractData: async (projectId: string) => {
    const response = await apiClient.post(
      `/meta-analysis/${projectId}/extract`
    );
    return response.data;
  },

  analyze: async (projectId: string) => {
    const response = await apiClient.post(
      `/meta-analysis/${projectId}/analyze`
    );
    return response.data;
  },

  getPrismaFlow: async (projectId: string) => {
    const response = await apiClient.get(
      `/meta-analysis/${projectId}/prisma`
    );
    return response.data;
  },
};

// ==================
// REVIEWER MATCHER API
// ==================

export const reviewerMatcherApi = {
  uploadManuscript: async (projectId: string, file: File, metadata: any) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));

    const response = await apiClient.post(
      `/reviewer-matcher/${projectId}/upload`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  },

  findMatches: async (projectId: string, options?: any) => {
    const response = await apiClient.post(
      `/reviewer-matcher/${projectId}/match`,
      options
    );
    return response.data;
  },

  getMatches: async (projectId: string) => {
    const response = await apiClient.get(
      `/reviewer-matcher/${projectId}/matches`
    );
    return response.data;
  },

  inviteReviewer: async (projectId: string, reviewerId: string) => {
    const response = await apiClient.post(
      `/reviewer-matcher/${projectId}/invite/${reviewerId}`
    );
    return response.data;
  },
};

// ==================
// PEER REVIEW API
// ==================

export const peerReviewApi = {
  screenQuality: async (projectId: string) => {
    const response = await apiClient.post(
      `/peer-review/${projectId}/screen`
    );
    return response.data;
  },

  generateReview: async (projectId: string, options?: any) => {
    const response = await apiClient.post(
      `/peer-review/${projectId}/review`,
      options
    );
    return response.data;
  },

  getReviews: async (projectId: string) => {
    const response = await apiClient.get(
      `/peer-review/${projectId}/reviews`
    );
    return response.data;
  },

  generateEditorSummary: async (projectId: string) => {
    const response = await apiClient.post(
      `/peer-review/${projectId}/summary`
    );
    return response.data;
  },
};

// ==================
// RESEARCH DIRECTION API
// ==================

export const researchDirectionApi = {
  importPublications: async (projectId: string, orcid: string) => {
    const response = await apiClient.post(
      `/research-direction/${projectId}/import`,
      { orcid }
    );
    return response.data;
  },

  analyzeGaps: async (projectId: string) => {
    const response = await apiClient.post(
      `/research-direction/${projectId}/gaps`
    );
    return response.data;
  },

  identifyTrends: async (projectId: string) => {
    const response = await apiClient.post(
      `/research-direction/${projectId}/trends`
    );
    return response.data;
  },

  suggestInnovations: async (projectId: string) => {
    const response = await apiClient.post(
      `/research-direction/${projectId}/innovations`
    );
    return response.data;
  },

  generateProposal: async (projectId: string, gapId: string, format: string) => {
    const response = await apiClient.post(
      `/research-direction/${projectId}/proposal`,
      { gap_id: gapId, format }
    );
    return response.data;
  },
};

// ==================
// WORKFLOWS API
// ==================

export const workflowsApi = {
  get: async (workflowId: string) => {
    const response = await apiClient.get(`/workflows/${workflowId}`);
    return response.data;
  },

  list: async (projectId: string) => {
    const response = await apiClient.get(`/workflows`, {
      params: { project_id: projectId },
    });
    return response.data;
  },

  getProgress: async (workflowId: string) => {
    const response = await apiClient.get(`/workflows/${workflowId}/progress`);
    return response.data;
  },

  cancel: async (workflowId: string) => {
    const response = await apiClient.post(`/workflows/${workflowId}/cancel`);
    return response.data;
  },
};

// ==================
// HEALTH API
// ==================

export const healthApi = {
  check: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  detailed: async () => {
    const response = await apiClient.get('/health/detailed');
    return response.data;
  },
};

// Export the axios instance for custom requests
export default apiClient;
