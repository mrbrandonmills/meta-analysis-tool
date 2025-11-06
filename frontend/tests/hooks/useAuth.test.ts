import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import * as api from '@/lib/api';
import { ReactNode } from 'react';

// Mock dependencies
vi.mock('@/lib/api');
vi.mock('next/router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    pathname: '/',
    query: {},
    asPath: '/',
  }),
}));
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useAuth Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn(),
      },
      writable: true,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Initial State', () => {
    it('starts with unauthenticated state', () => {
      vi.mocked(api.authApi.getCurrentUser).mockRejectedValue(new Error('Unauthorized'));

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeUndefined();
    });

    it('starts with loading state', () => {
      vi.mocked(api.authApi.getCurrentUser).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);
    });
  });

  describe('Login', () => {
    it('successfully logs in user', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'researcher' as const,
      };

      const mockAuthResponse = {
        access_token: 'access-token',
        refresh_token: 'refresh-token',
        token_type: 'Bearer',
        user: mockUser,
      };

      vi.mocked(api.authApi.login).mockResolvedValue(mockAuthResponse);
      vi.mocked(api.authApi.getCurrentUser).mockResolvedValue(mockUser);

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.login({
          username: 'test@example.com',
          password: 'password123',
        });
      });

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true);
      });
    });

    it('sets isLoggingIn to true during login', async () => {
      vi.mocked(api.authApi.login).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.login({
          username: 'test@example.com',
          password: 'password',
        });
      });

      expect(result.current.isLoggingIn).toBe(true);
    });

    it('handles login errors', async () => {
      const error = new Error('Invalid credentials');
      vi.mocked(api.authApi.login).mockRejectedValue(error);

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.login({
          username: 'wrong@example.com',
          password: 'wrongpassword',
        });
      });

      await waitFor(() => {
        expect(result.current.isLoggingIn).toBe(false);
      });
    });

    it('calls login API with correct credentials', async () => {
      const mockAuthResponse = {
        access_token: 'token',
        refresh_token: 'refresh',
        token_type: 'Bearer',
        user: {
          id: '1',
          email: 'test@example.com',
          name: 'Test',
          role: 'researcher' as const,
        },
      };

      vi.mocked(api.authApi.login).mockResolvedValue(mockAuthResponse);

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      const credentials = {
        username: 'test@example.com',
        password: 'password123',
      };

      await act(async () => {
        result.current.login(credentials);
      });

      await waitFor(() => {
        expect(api.authApi.login).toHaveBeenCalledWith(credentials);
      });
    });
  });

  describe('Register', () => {
    it('successfully registers user', async () => {
      const mockUser = {
        id: '1',
        email: 'new@example.com',
        name: 'New User',
        role: 'researcher' as const,
      };

      const mockAuthResponse = {
        access_token: 'access-token',
        refresh_token: 'refresh-token',
        token_type: 'Bearer',
        user: mockUser,
      };

      vi.mocked(api.authApi.register).mockResolvedValue(mockAuthResponse);
      vi.mocked(api.authApi.getCurrentUser).mockResolvedValue(mockUser);

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.register({
          email: 'new@example.com',
          password: 'password123',
          name: 'New User',
        });
      });

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true);
      });
    });

    it('sets isRegistering to true during registration', async () => {
      vi.mocked(api.authApi.register).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.register({
          email: 'new@example.com',
          password: 'password',
          name: 'New User',
        });
      });

      expect(result.current.isRegistering).toBe(true);
    });

    it('handles registration errors', async () => {
      const error = new Error('Email already exists');
      vi.mocked(api.authApi.register).mockRejectedValue(error);

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.register({
          email: 'existing@example.com',
          password: 'password',
          name: 'User',
        });
      });

      await waitFor(() => {
        expect(result.current.isRegistering).toBe(false);
      });
    });
  });

  describe('Logout', () => {
    it('successfully logs out user', async () => {
      vi.mocked(api.authApi.logout).mockResolvedValue();

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.logout();
      });

      await waitFor(() => {
        expect(api.authApi.logout).toHaveBeenCalled();
      });
    });

    it('sets isLoggingOut to true during logout', async () => {
      vi.mocked(api.authApi.logout).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.logout();
      });

      expect(result.current.isLoggingOut).toBe(true);
    });

    it('handles logout errors gracefully', async () => {
      const error = new Error('Network error');
      vi.mocked(api.authApi.logout).mockRejectedValue(error);

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.logout();
      });

      await waitFor(() => {
        expect(result.current.isLoggingOut).toBe(false);
      });
    });
  });

  describe('Authentication State', () => {
    it('returns true for isAuthenticated when user exists', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'researcher' as const,
      };

      vi.mocked(api.authApi.getCurrentUser).mockResolvedValue(mockUser);

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true);
        expect(result.current.user).toEqual(mockUser);
      });
    });

    it('returns false for isAuthenticated when no user', async () => {
      vi.mocked(api.authApi.getCurrentUser).mockRejectedValue(new Error('Unauthorized'));

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(false);
        expect(result.current.user).toBeUndefined();
      });
    });
  });

  describe('Loading States', () => {
    it('provides isLoading state', () => {
      vi.mocked(api.authApi.getCurrentUser).mockImplementation(
        () => new Promise(() => {})
      );

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);
      expect(result.current.isLoggingIn).toBe(false);
      expect(result.current.isRegistering).toBe(false);
      expect(result.current.isLoggingOut).toBe(false);
    });
  });

  describe('User Data', () => {
    it('returns user data after successful login', async () => {
      const mockUser = {
        id: '123',
        email: 'john@example.com',
        name: 'John Doe',
        role: 'researcher' as const,
      };

      const mockAuthResponse = {
        access_token: 'token',
        refresh_token: 'refresh',
        token_type: 'Bearer',
        user: mockUser,
      };

      vi.mocked(api.authApi.login).mockResolvedValue(mockAuthResponse);
      vi.mocked(api.authApi.getCurrentUser).mockResolvedValue(mockUser);

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.login({
          username: 'john@example.com',
          password: 'password',
        });
      });

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser);
      });
    });
  });
});
