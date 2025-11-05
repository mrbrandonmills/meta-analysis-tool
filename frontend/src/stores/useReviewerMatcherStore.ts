// Tool 4: Reviewer Matcher Store
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  ReviewerMatchProject,
  ReviewerMatch,
  Manuscript,
  AgentProgress
} from '@/lib/types';

interface ReviewerMatcherState {
  // Current Project
  currentProject: ReviewerMatchProject | null;
  manuscript: Manuscript | null;

  // Matches
  matches: ReviewerMatch[];
  selectedReviewers: Set<string>;
  invitedReviewers: Set<string>;

  // Agent Progress
  agentProgress: Record<string, AgentProgress>;

  // Filters & Sorting
  expertiseFilter: string[];
  availabilityFilter: 'all' | 'high' | 'medium' | 'low';
  sortBy: 'overall' | 'expertise' | 'availability' | 'conflict';

  // Actions
  setCurrentProject: (project: ReviewerMatchProject | null) => void;
  setManuscript: (manuscript: Manuscript | null) => void;

  setMatches: (matches: ReviewerMatch[]) => void;
  addMatch: (match: ReviewerMatch) => void;

  toggleReviewerSelection: (reviewerId: string) => void;
  clearSelectedReviewers: () => void;
  inviteReviewer: (reviewerId: string) => void;

  updateAgentProgress: (agentName: string, progress: AgentProgress) => void;

  setExpertiseFilter: (filter: string[]) => void;
  setAvailabilityFilter: (filter: 'all' | 'high' | 'medium' | 'low') => void;
  setSortBy: (sortBy: 'overall' | 'expertise' | 'availability' | 'conflict') => void;

  reset: () => void;
}

export const useReviewerMatcherStore = create<ReviewerMatcherState>()(
  devtools(
    (set) => ({
      // Initial State
      currentProject: null,
      manuscript: null,
      matches: [],
      selectedReviewers: new Set(),
      invitedReviewers: new Set(),
      agentProgress: {},
      expertiseFilter: [],
      availabilityFilter: 'all',
      sortBy: 'overall',

      // Actions
      setCurrentProject: (project) => set({ currentProject: project }),
      setManuscript: (manuscript) => set({ manuscript }),

      setMatches: (matches) => set({ matches }),
      addMatch: (match) => set((state) => ({
        matches: [...state.matches, match]
      })),

      toggleReviewerSelection: (reviewerId) => set((state) => {
        const newSelection = new Set(state.selectedReviewers);
        if (newSelection.has(reviewerId)) {
          newSelection.delete(reviewerId);
        } else {
          newSelection.add(reviewerId);
        }
        return { selectedReviewers: newSelection };
      }),

      clearSelectedReviewers: () => set({ selectedReviewers: new Set() }),

      inviteReviewer: (reviewerId) => set((state) => ({
        invitedReviewers: new Set(state.invitedReviewers).add(reviewerId)
      })),

      updateAgentProgress: (agentName, progress) => set((state) => ({
        agentProgress: {
          ...state.agentProgress,
          [agentName]: progress
        }
      })),

      setExpertiseFilter: (filter) => set({ expertiseFilter: filter }),
      setAvailabilityFilter: (filter) => set({ availabilityFilter: filter }),
      setSortBy: (sortBy) => set({ sortBy }),

      reset: () => set({
        currentProject: null,
        manuscript: null,
        matches: [],
        selectedReviewers: new Set(),
        invitedReviewers: new Set(),
        agentProgress: {},
        expertiseFilter: [],
        availabilityFilter: 'all',
        sortBy: 'overall'
      })
    }),
    { name: 'ReviewerMatcherStore' }
  )
);
