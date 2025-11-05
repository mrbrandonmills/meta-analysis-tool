// Tool 1: Meta-Analysis Store
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
  MetaAnalysisProject,
  SearchResults,
  ScreeningResults,
  CredibilityResults,
  DataExtractionResults,
  StatisticalResults,
  PrismaFlow,
  AgentProgress
} from '@/lib/types';

interface MetaAnalysisState {
  // Current Analysis
  currentAnalysis: MetaAnalysisProject | null;

  // Agent Progress
  agentProgress: Record<string, AgentProgress>;

  // Results
  searchResults: SearchResults | null;
  screeningResults: ScreeningResults | null;
  credibilityResults: CredibilityResults | null;
  extractionResults: DataExtractionResults | null;
  statisticalResults: StatisticalResults | null;
  prismaFlow: PrismaFlow | null;

  // UI State
  activeStep: number;
  selectedStudies: Set<string>;

  // Actions
  setCurrentAnalysis: (analysis: MetaAnalysisProject | null) => void;
  updateAgentProgress: (agentName: string, progress: AgentProgress) => void;

  setSearchResults: (results: SearchResults) => void;
  setScreeningResults: (results: ScreeningResults) => void;
  setCredibilityResults: (results: CredibilityResults) => void;
  setExtractionResults: (results: DataExtractionResults) => void;
  setStatisticalResults: (results: StatisticalResults) => void;
  setPrismaFlow: (flow: PrismaFlow) => void;

  setActiveStep: (step: number) => void;
  toggleStudySelection: (studyId: string) => void;
  clearSelectedStudies: () => void;

  reset: () => void;
}

export const useMetaAnalysisStore = create<MetaAnalysisState>()(
  devtools(
    (set) => ({
      // Initial State
      currentAnalysis: null,
      agentProgress: {},
      searchResults: null,
      screeningResults: null,
      credibilityResults: null,
      extractionResults: null,
      statisticalResults: null,
      prismaFlow: null,
      activeStep: 0,
      selectedStudies: new Set(),

      // Actions
      setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),

      updateAgentProgress: (agentName, progress) => set((state) => ({
        agentProgress: {
          ...state.agentProgress,
          [agentName]: progress
        }
      })),

      setSearchResults: (results) => set({ searchResults: results }),
      setScreeningResults: (results) => set({ screeningResults: results }),
      setCredibilityResults: (results) => set({ credibilityResults: results }),
      setExtractionResults: (results) => set({ extractionResults: results }),
      setStatisticalResults: (results) => set({ statisticalResults: results }),
      setPrismaFlow: (flow) => set({ prismaFlow: flow }),

      setActiveStep: (step) => set({ activeStep: step }),

      toggleStudySelection: (studyId) => set((state) => {
        const newSelection = new Set(state.selectedStudies);
        if (newSelection.has(studyId)) {
          newSelection.delete(studyId);
        } else {
          newSelection.add(studyId);
        }
        return { selectedStudies: newSelection };
      }),

      clearSelectedStudies: () => set({ selectedStudies: new Set() }),

      reset: () => set({
        currentAnalysis: null,
        agentProgress: {},
        searchResults: null,
        screeningResults: null,
        credibilityResults: null,
        extractionResults: null,
        statisticalResults: null,
        prismaFlow: null,
        activeStep: 0,
        selectedStudies: new Set()
      })
    }),
    { name: 'MetaAnalysisStore' }
  )
);
