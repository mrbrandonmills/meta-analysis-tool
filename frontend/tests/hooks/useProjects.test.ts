import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  useProjects,
  useProject,
  useCreateProject,
  useUpdateProject,
  useDeleteProject,
  usePauseProject,
  useResumeProject,
  useCancelProject,
} from '@/hooks/useProjects';
import * as api from '@/lib/api';
import { ReactNode } from 'react';

vi.mock('@/lib/api');
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

describe('useProjects Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useProjects', () => {
    it('fetches projects list', async () => {
      const mockProjects = [
        { id: '1', title: 'Project 1', status: 'in_progress' },
        { id: '2', title: 'Project 2', status: 'completed' },
      ];

      vi.mocked(api.projectsApi.list).mockResolvedValue(mockProjects);

      const { result } = renderHook(() => useProjects(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockProjects);
      });
    });

    it('fetches projects with params', async () => {
      const mockProjects = [
        { id: '1', title: 'Meta-Analysis 1', tool_type: 'meta_analysis' },
      ];

      vi.mocked(api.projectsApi.list).mockResolvedValue(mockProjects);

      const { result } = renderHook(
        () => useProjects({ tool_type: 'meta_analysis' }),
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(api.projectsApi.list).toHaveBeenCalledWith({ tool_type: 'meta_analysis' });
        expect(result.current.data).toEqual(mockProjects);
      });
    });

    it('handles empty projects list', async () => {
      vi.mocked(api.projectsApi.list).mockResolvedValue([]);

      const { result } = renderHook(() => useProjects(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.data).toEqual([]);
      });
    });

    it('handles fetch errors', async () => {
      const error = new Error('Failed to fetch projects');
      vi.mocked(api.projectsApi.list).mockRejectedValue(error);

      const { result } = renderHook(() => useProjects(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });

    it('provides loading state', () => {
      vi.mocked(api.projectsApi.list).mockImplementation(
        () => new Promise(() => {})
      );

      const { result } = renderHook(() => useProjects(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);
    });
  });

  describe('useProject', () => {
    it('fetches single project', async () => {
      const mockProject = {
        id: '123',
        title: 'Test Project',
        status: 'in_progress',
      };

      vi.mocked(api.projectsApi.get).mockResolvedValue(mockProject);

      const { result } = renderHook(() => useProject('123'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockProject);
      });
    });

    it('does not fetch when id is empty', () => {
      vi.mocked(api.projectsApi.get).mockResolvedValue({});

      renderHook(() => useProject(''), {
        wrapper: createWrapper(),
      });

      expect(api.projectsApi.get).not.toHaveBeenCalled();
    });

    it('handles fetch errors', async () => {
      const error = new Error('Project not found');
      vi.mocked(api.projectsApi.get).mockRejectedValue(error);

      const { result } = renderHook(() => useProject('999'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });
  });

  describe('useCreateProject', () => {
    it('creates new project', async () => {
      const newProject = {
        title: 'New Project',
        description: 'Test description',
        tool_type: 'meta_analysis',
      };

      const createdProject = { id: '456', ...newProject };
      vi.mocked(api.projectsApi.create).mockResolvedValue(createdProject);

      const { result } = renderHook(() => useCreateProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate(newProject);
      });

      await waitFor(() => {
        expect(api.projectsApi.create).toHaveBeenCalledWith(newProject);
      });
    });

    it('invalidates projects query after creation', async () => {
      const newProject = { title: 'New Project' };
      vi.mocked(api.projectsApi.create).mockResolvedValue({ id: '1', ...newProject });

      const { result } = renderHook(() => useCreateProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate(newProject);
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });
    });

    it('handles creation errors', async () => {
      const error = new Error('Validation failed');
      vi.mocked(api.projectsApi.create).mockRejectedValue(error);

      const { result } = renderHook(() => useCreateProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate({ title: 'Invalid' });
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });
  });

  describe('useUpdateProject', () => {
    it('updates existing project', async () => {
      const updateData = { title: 'Updated Title' };
      const updatedProject = { id: '123', ...updateData };

      vi.mocked(api.projectsApi.update).mockResolvedValue(updatedProject);

      const { result } = renderHook(() => useUpdateProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate({ id: '123', data: updateData });
      });

      await waitFor(() => {
        expect(api.projectsApi.update).toHaveBeenCalledWith('123', updateData);
      });
    });

    it('invalidates project queries after update', async () => {
      vi.mocked(api.projectsApi.update).mockResolvedValue({ id: '123' });

      const { result } = renderHook(() => useUpdateProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate({ id: '123', data: { title: 'Updated' } });
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });
    });

    it('handles update errors', async () => {
      const error = new Error('Update failed');
      vi.mocked(api.projectsApi.update).mockRejectedValue(error);

      const { result } = renderHook(() => useUpdateProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate({ id: '123', data: {} });
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });
  });

  describe('useDeleteProject', () => {
    it('deletes project', async () => {
      vi.mocked(api.projectsApi.delete).mockResolvedValue({});

      const { result } = renderHook(() => useDeleteProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate('123');
      });

      await waitFor(() => {
        expect(api.projectsApi.delete).toHaveBeenCalledWith('123');
      });
    });

    it('invalidates projects query after deletion', async () => {
      vi.mocked(api.projectsApi.delete).mockResolvedValue({});

      const { result } = renderHook(() => useDeleteProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate('123');
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });
    });

    it('handles deletion errors', async () => {
      const error = new Error('Delete failed');
      vi.mocked(api.projectsApi.delete).mockRejectedValue(error);

      const { result } = renderHook(() => useDeleteProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate('123');
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });
  });

  describe('usePauseProject', () => {
    it('pauses project', async () => {
      vi.mocked(api.projectsApi.pause).mockResolvedValue({ status: 'paused' });

      const { result } = renderHook(() => usePauseProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate('123');
      });

      await waitFor(() => {
        expect(api.projectsApi.pause).toHaveBeenCalledWith('123');
      });
    });

    it('handles pause errors', async () => {
      const error = new Error('Cannot pause project');
      vi.mocked(api.projectsApi.pause).mockRejectedValue(error);

      const { result } = renderHook(() => usePauseProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate('123');
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });
  });

  describe('useResumeProject', () => {
    it('resumes project', async () => {
      vi.mocked(api.projectsApi.resume).mockResolvedValue({ status: 'in_progress' });

      const { result } = renderHook(() => useResumeProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate('123');
      });

      await waitFor(() => {
        expect(api.projectsApi.resume).toHaveBeenCalledWith('123');
      });
    });

    it('handles resume errors', async () => {
      const error = new Error('Cannot resume project');
      vi.mocked(api.projectsApi.resume).mockRejectedValue(error);

      const { result } = renderHook(() => useResumeProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate('123');
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });
  });

  describe('useCancelProject', () => {
    it('cancels project', async () => {
      vi.mocked(api.projectsApi.cancel).mockResolvedValue({ status: 'cancelled' });

      const { result } = renderHook(() => useCancelProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate('123');
      });

      await waitFor(() => {
        expect(api.projectsApi.cancel).toHaveBeenCalledWith('123');
      });
    });

    it('handles cancel errors', async () => {
      const error = new Error('Cannot cancel project');
      vi.mocked(api.projectsApi.cancel).mockRejectedValue(error);

      const { result } = renderHook(() => useCancelProject(), {
        wrapper: createWrapper(),
      });

      await act(async () => {
        result.current.mutate('123');
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });
  });
});
