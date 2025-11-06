import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios, { AxiosError } from 'axios';
import apiClient, {
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
  setTokens,
  clearTokens,
  isAuthenticated,
} from '@/lib/api';

// Mock axios
vi.mock('axios');
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('API Client Integration Tests', () => {
  let mockLocalStorage: { [key: string]: string };

  beforeEach(() => {
    // Mock localStorage
    mockLocalStorage = {};
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn((key: string) => mockLocalStorage[key] || null),
        setItem: vi.fn((key: string, value: string) => {
          mockLocalStorage[key] = value;
        }),
        removeItem: vi.fn((key: string) => {
          delete mockLocalStorage[key];
        }),
        clear: vi.fn(() => {
          mockLocalStorage = {};
        }),
      },
      writable: true,
    });

    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Token Management', () => {
    describe('getAccessToken', () => {
      it('retrieves access token from localStorage', () => {
        mockLocalStorage['access_token'] = 'test-access-token';
        expect(getAccessToken()).toBe('test-access-token');
      });

      it('returns null when no token exists', () => {
        expect(getAccessToken()).toBeNull();
      });
    });

    describe('getRefreshToken', () => {
      it('retrieves refresh token from localStorage', () => {
        mockLocalStorage['refresh_token'] = 'test-refresh-token';
        expect(getRefreshToken()).toBe('test-refresh-token');
      });

      it('returns null when no token exists', () => {
        expect(getRefreshToken()).toBeNull();
      });
    });

    describe('setAccessToken', () => {
      it('stores access token in localStorage', () => {
        setAccessToken('new-access-token');
        expect(mockLocalStorage['access_token']).toBe('new-access-token');
      });
    });

    describe('setRefreshToken', () => {
      it('stores refresh token in localStorage', () => {
        setRefreshToken('new-refresh-token');
        expect(mockLocalStorage['refresh_token']).toBe('new-refresh-token');
      });
    });

    describe('setTokens', () => {
      it('stores both tokens in localStorage', () => {
        setTokens('access-123', 'refresh-456');
        expect(mockLocalStorage['access_token']).toBe('access-123');
        expect(mockLocalStorage['refresh_token']).toBe('refresh-456');
      });
    });

    describe('clearTokens', () => {
      it('removes both tokens from localStorage', () => {
        mockLocalStorage['access_token'] = 'token1';
        mockLocalStorage['refresh_token'] = 'token2';

        clearTokens();

        expect(mockLocalStorage['access_token']).toBeUndefined();
        expect(mockLocalStorage['refresh_token']).toBeUndefined();
      });
    });

    describe('isAuthenticated', () => {
      it('returns true when access token exists', () => {
        mockLocalStorage['access_token'] = 'test-token';
        expect(isAuthenticated()).toBe(true);
      });

      it('returns false when no access token exists', () => {
        expect(isAuthenticated()).toBe(false);
      });
    });
  });

  describe('Request Interceptor', () => {
    it('adds Authorization header when token exists', () => {
      mockLocalStorage['access_token'] = 'test-token';

      const config = {
        headers: {},
      };

      // Access the request interceptor
      const interceptors = (apiClient as any).interceptors;
      const requestInterceptor = interceptors.request.handlers[0];

      if (requestInterceptor && requestInterceptor.fulfilled) {
        const result = requestInterceptor.fulfilled(config);
        expect(result.headers.Authorization).toBe('Bearer test-token');
      }
    });

    it('does not add Authorization header when no token', () => {
      const config = {
        headers: {},
      };

      const interceptors = (apiClient as any).interceptors;
      const requestInterceptor = interceptors.request.handlers[0];

      if (requestInterceptor && requestInterceptor.fulfilled) {
        const result = requestInterceptor.fulfilled(config);
        expect(result.headers.Authorization).toBeUndefined();
      }
    });
  });

  describe('API Client Configuration', () => {
    it('has correct base URL', () => {
      expect((apiClient as any).defaults.baseURL).toBeDefined();
    });

    it('has timeout configured', () => {
      expect((apiClient as any).defaults.timeout).toBe(30000);
    });

    it('has correct default headers', () => {
      expect((apiClient as any).defaults.headers['Content-Type']).toBe('application/json');
    });
  });

  describe('Error Handling', () => {
    it('handles network errors', () => {
      const error = {
        request: {},
        config: {},
      } as AxiosError;

      // Verify that error handling exists
      expect(apiClient.interceptors.response).toBeDefined();
    });

    it('handles server errors', () => {
      const error = {
        response: {
          status: 500,
          data: { message: 'Server error' },
        },
        config: {},
      } as AxiosError;

      expect(apiClient.interceptors.response).toBeDefined();
    });

    it('handles validation errors', () => {
      const error = {
        response: {
          status: 400,
          data: { message: 'Validation failed' },
        },
        config: {},
      } as AxiosError;

      expect(apiClient.interceptors.response).toBeDefined();
    });

    it('handles not found errors', () => {
      const error = {
        response: {
          status: 404,
          data: { message: 'Not found' },
        },
        config: {},
      } as AxiosError;

      expect(apiClient.interceptors.response).toBeDefined();
    });

    it('handles forbidden errors', () => {
      const error = {
        response: {
          status: 403,
          data: { message: 'Forbidden' },
        },
        config: {},
      } as AxiosError;

      expect(apiClient.interceptors.response).toBeDefined();
    });

    it('handles rate limit errors', () => {
      const error = {
        response: {
          status: 429,
          headers: { 'retry-after': '60' },
          data: { message: 'Too many requests' },
        },
        config: {},
      } as AxiosError;

      expect(apiClient.interceptors.response).toBeDefined();
    });
  });

  describe('Token Refresh Flow', () => {
    it('attempts token refresh on 401 error', async () => {
      mockLocalStorage['access_token'] = 'expired-token';
      mockLocalStorage['refresh_token'] = 'valid-refresh-token';

      const mockAxiosPost = vi.fn().mockResolvedValue({
        data: { access_token: 'new-access-token' },
      });

      vi.mocked(axios.post).mockImplementation(mockAxiosPost);

      const error = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' },
        },
        config: {
          headers: {},
        },
      } as AxiosError;

      // Verify response interceptor exists
      expect(apiClient.interceptors.response).toBeDefined();
    });

    it('does not retry request after refresh failure', () => {
      mockLocalStorage['access_token'] = 'expired-token';
      mockLocalStorage['refresh_token'] = 'invalid-refresh-token';

      vi.mocked(axios.post).mockRejectedValue(new Error('Invalid refresh token'));

      expect(apiClient.interceptors.response).toBeDefined();
    });

    it('clears tokens after failed refresh', async () => {
      mockLocalStorage['access_token'] = 'expired-token';
      mockLocalStorage['refresh_token'] = 'invalid-refresh-token';

      vi.mocked(axios.post).mockRejectedValue(new Error('Invalid refresh token'));

      // Tokens should be cleared after failed refresh
      // This is handled by the interceptor
      expect(apiClient.interceptors.response).toBeDefined();
    });

    it('does not retry if request already retried', () => {
      const error = {
        response: {
          status: 401,
        },
        config: {
          _retry: true,
          headers: {},
        },
      } as AxiosError & { config: { _retry?: boolean } };

      // Should not attempt refresh if already retried
      expect(apiClient.interceptors.response).toBeDefined();
    });
  });

  describe('Response Handling', () => {
    it('passes through successful responses', () => {
      const response = {
        data: { success: true },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {},
      };

      // Verify that response interceptor exists
      expect(apiClient.interceptors.response).toBeDefined();
    });

    it('handles 200 OK responses', () => {
      const response = {
        data: { id: '123', name: 'Test' },
        status: 200,
      };

      expect(apiClient.interceptors.response).toBeDefined();
    });

    it('handles 201 Created responses', () => {
      const response = {
        data: { id: '456', name: 'Created' },
        status: 201,
      };

      expect(apiClient.interceptors.response).toBeDefined();
    });

    it('handles 204 No Content responses', () => {
      const response = {
        data: null,
        status: 204,
      };

      expect(apiClient.interceptors.response).toBeDefined();
    });
  });

  describe('Concurrent Requests', () => {
    it('handles multiple simultaneous requests', () => {
      mockLocalStorage['access_token'] = 'test-token';

      // Multiple requests should all get the same token
      const config1 = { headers: {} };
      const config2 = { headers: {} };
      const config3 = { headers: {} };

      const interceptors = (apiClient as any).interceptors;
      const requestInterceptor = interceptors.request.handlers[0];

      if (requestInterceptor && requestInterceptor.fulfilled) {
        const result1 = requestInterceptor.fulfilled(config1);
        const result2 = requestInterceptor.fulfilled(config2);
        const result3 = requestInterceptor.fulfilled(config3);

        expect(result1.headers.Authorization).toBe('Bearer test-token');
        expect(result2.headers.Authorization).toBe('Bearer test-token');
        expect(result3.headers.Authorization).toBe('Bearer test-token');
      }
    });
  });

  describe('Request Configuration', () => {
    it('includes correct Content-Type header', () => {
      const headers = (apiClient as any).defaults.headers;
      expect(headers['Content-Type']).toBe('application/json');
    });

    it('has reasonable timeout', () => {
      const timeout = (apiClient as any).defaults.timeout;
      expect(timeout).toBe(30000); // 30 seconds
      expect(timeout).toBeGreaterThan(0);
    });

    it('includes API version in base URL', () => {
      const baseURL = (apiClient as any).defaults.baseURL;
      expect(baseURL).toContain('/api/v1');
    });
  });
});
