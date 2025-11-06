import { QueryClient, QueryClientConfig } from '@tanstack/react-query';
import toast from 'react-hot-toast';

// Query client configuration
const queryConfig: QueryClientConfig = {
  defaultOptions: {
    queries: {
      // Global query defaults
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: 1,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
      refetchOnMount: true,
    },
    mutations: {
      // Global mutation defaults
      retry: 0,
      onError: (error: any) => {
        const message =
          error?.response?.data?.message ||
          error?.message ||
          'An error occurred';
        toast.error(message);
      },
    },
  },
};

// Create query client instance
export const queryClient = new QueryClient(queryConfig);

// Query keys for consistent cache management
export const queryKeys = {
  // Auth
  currentUser: ['auth', 'currentUser'] as const,

  // Projects
  projects: (params?: any) => ['projects', params] as const,
  project: (id: string) => ['projects', id] as const,

  // Meta-Analysis
  metaAnalysis: (projectId: string) => ['meta-analysis', projectId] as const,
  metaAnalysisSearch: (projectId: string) =>
    ['meta-analysis', projectId, 'search'] as const,
  metaAnalysisPrisma: (projectId: string) =>
    ['meta-analysis', projectId, 'prisma'] as const,

  // Reviewer Matcher
  reviewerMatches: (projectId: string) =>
    ['reviewer-matcher', projectId, 'matches'] as const,

  // Peer Review
  peerReviews: (projectId: string) =>
    ['peer-review', projectId, 'reviews'] as const,

  // Research Direction
  researchGaps: (projectId: string) =>
    ['research-direction', projectId, 'gaps'] as const,
  researchTrends: (projectId: string) =>
    ['research-direction', projectId, 'trends'] as const,
  researchInnovations: (projectId: string) =>
    ['research-direction', projectId, 'innovations'] as const,

  // Workflows
  workflows: (projectId: string) => ['workflows', projectId] as const,
  workflow: (workflowId: string) => ['workflows', workflowId] as const,
  workflowProgress: (workflowId: string) =>
    ['workflows', workflowId, 'progress'] as const,

  // Health
  health: ['health'] as const,
  healthDetailed: ['health', 'detailed'] as const,
};

// Prefetch helpers
export const prefetchHelpers = {
  prefetchProjects: async () => {
    // Implement prefetch logic as needed
  },
};

export default queryClient;
