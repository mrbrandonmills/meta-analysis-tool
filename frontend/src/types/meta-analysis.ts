/**
 * Type definitions for meta-analysis data structures
 */

export type EffectMeasure = 'OR' | 'RR' | 'MD' | 'SMD' | 'HR';

export interface Study {
  id: string;
  author: string;
  year: number;
  sampleSize: number;
  studyDesign: string;
  effectSize: number;
  standardError: number;
  lowerCI: number;
  upperCI: number;
  weight: number;
  qualityScore?: number;
  subgroup?: string;
}

export interface HeterogeneityStats {
  Q: number;
  df: number;
  pValue: number;
  I2: number;
  tau2: number;
  H2?: number;
}

export interface OverallEffect {
  effectSize: number;
  standardError: number;
  lowerCI: number;
  upperCI: number;
  zValue: number;
  pValue: number;
}

export interface PublicationBias {
  eggersTest?: {
    intercept: number;
    pValue: number;
  };
  beggTest?: {
    tau: number;
    pValue: number;
  };
  trimAndFill?: {
    adjustedEffectSize: number;
    missingStudies: number;
  };
}

export interface SubgroupAnalysis {
  subgroupName: string;
  studies: Study[];
  effectSize: number;
  lowerCI: number;
  upperCI: number;
  heterogeneity: HeterogeneityStats;
  pValue: number;
}

export interface SensitivityAnalysis {
  name: string;
  description: string;
  effectSize: number;
  lowerCI: number;
  upperCI: number;
  studiesRemoved?: string[];
}

export interface MetaAnalysisResults {
  studies: Study[];
  overallEffect: OverallEffect;
  heterogeneity: HeterogeneityStats;
  publicationBias?: PublicationBias;
  subgroupAnalyses?: SubgroupAnalysis[];
  sensitivityAnalyses?: SensitivityAnalysis[];
  effectMeasure: EffectMeasure;
  model: 'fixed' | 'random';
}

export interface PRISMAFlowData {
  identification: {
    databasesSearched: number;
    recordsIdentified: number;
    duplicatesRemoved: number;
    recordsScreened: number;
  };
  screening: {
    recordsExcluded: number;
    exclusionReasons?: Record<string, number>;
  };
  eligibility: {
    fullTextAssessed: number;
    fullTextExcluded: number;
    exclusionReasons?: Record<string, number>;
  };
  included: {
    studiesIncluded: number;
    studiesInMetaAnalysis?: number;
  };
}

export interface ForestPlotProps {
  results: MetaAnalysisResults;
  title?: string;
  showWeights?: boolean;
  showHeterogeneity?: boolean;
  height?: number;
  className?: string;
}

export interface FunnelPlotProps {
  studies: Study[];
  overallEffect: OverallEffect;
  publicationBias?: PublicationBias;
  showEggersLine?: boolean;
  showContours?: boolean;
  height?: number;
  className?: string;
}

export interface PRISMAFlowProps {
  data: PRISMAFlowData;
  interactive?: boolean;
  showAnimations?: boolean;
  className?: string;
}

export interface StatisticsPanelProps {
  results: MetaAnalysisResults;
  showSubgroups?: boolean;
  showSensitivity?: boolean;
  className?: string;
}

export interface StudyCharacteristicsTableProps {
  studies: Study[];
  effectMeasure: EffectMeasure;
  showQualityScores?: boolean;
  sortable?: boolean;
  filterable?: boolean;
  className?: string;
}
