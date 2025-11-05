import { useQuery, useQueryClient } from '@tanstack/react-query';
import { workflowsApi } from '@/lib/api';
import { queryKeys } from '@/lib/queryClient';
import { useEffect, useRef } from 'react';

export function useWorkflows(projectId: string) {
  return useQuery({
    queryKey: queryKeys.workflows(projectId),
    queryFn: () => workflowsApi.list(projectId),
    enabled: !!projectId,
  });
}

export function useWorkflow(workflowId: string) {
  return useQuery({
    queryKey: queryKeys.workflow(workflowId),
    queryFn: () => workflowsApi.get(workflowId),
    enabled: !!workflowId,
  });
}

export function useWorkflowProgress(workflowId: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.workflowProgress(workflowId),
    queryFn: () => workflowsApi.getProgress(workflowId),
    enabled: !!workflowId && (options?.enabled !== false),
    refetchInterval: 2000, // Poll every 2 seconds for progress updates
  });
}

// Custom hook for real-time workflow progress with polling
export function useWorkflowProgressPolling(
  workflowId: string,
  options?: {
    enabled?: boolean;
    onComplete?: () => void;
    onError?: () => void;
  }
) {
  const queryClient = useQueryClient();
  const onCompleteRef = useRef(options?.onComplete);
  const onErrorRef = useRef(options?.onError);

  // Update refs
  useEffect(() => {
    onCompleteRef.current = options?.onComplete;
    onErrorRef.current = options?.onError;
  }, [options?.onComplete, options?.onError]);

  const { data: progress, isLoading } = useQuery({
    queryKey: queryKeys.workflowProgress(workflowId),
    queryFn: () => workflowsApi.getProgress(workflowId),
    enabled: !!workflowId && (options?.enabled !== false),
    refetchInterval: (query) => {
      // Stop polling if workflow is complete or errored
      const data = query.state.data;
      if (data?.status === 'COMPLETED' || data?.status === 'FAILED') {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
  });

  // Handle completion/error callbacks
  useEffect(() => {
    if (progress) {
      if (progress.status === 'COMPLETED' && onCompleteRef.current) {
        onCompleteRef.current();
      } else if (progress.status === 'FAILED' && onErrorRef.current) {
        onErrorRef.current();
      }
    }
  }, [progress]);

  return {
    progress,
    isLoading,
    isComplete: progress?.status === 'COMPLETED',
    isFailed: progress?.status === 'FAILED',
    isInProgress: progress?.status === 'IN_PROGRESS',
  };
}
