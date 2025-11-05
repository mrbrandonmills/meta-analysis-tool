import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '@/lib/api';
import { queryKeys } from '@/lib/queryClient';
import toast from 'react-hot-toast';

export function useProjects(params?: { tool_type?: string; status?: string }) {
  return useQuery({
    queryKey: queryKeys.projects(params),
    queryFn: () => projectsApi.list(params),
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: queryKeys.project(id),
    queryFn: () => projectsApi.get(id),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast.success('Project created successfully');
    },
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      projectsApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.project(variables.id) });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast.success('Project updated successfully');
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast.success('Project deleted successfully');
    },
  });
}

export function usePauseProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectsApi.pause,
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.project(projectId) });
      toast.success('Project paused');
    },
  });
}

export function useResumeProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectsApi.resume,
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.project(projectId) });
      toast.success('Project resumed');
    },
  });
}

export function useCancelProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: projectsApi.cancel,
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.project(projectId) });
      toast.success('Project cancelled');
    },
  });
}
