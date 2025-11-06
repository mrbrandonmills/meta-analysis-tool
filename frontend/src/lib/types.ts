// ===========================
// MULTI-TOOL PLATFORM TYPES
// ===========================

// Core Platform Types
export enum ToolType {
  META_ANALYSIS = 'meta_analysis',
  RESEARCH_DIRECTION = 'research_direction',
  PEER_REVIEW = 'peer_review',
  REVIEWER_MATCHER = 'reviewer_matcher'
}

export enum ProjectStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum WorkflowStatus {
  CREATED = 'created',
  QUEUED = 'queued',
  IN_PROGRESS = 'in_progress',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum AgentStatus {
  IDLE = 'idle',
  THINKING = 'thinking',
  PROCESSING = 'processing',
  COMPLETE = 'complete',
  ERROR = 'error'
}

export enum CredibilityLevel {
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
  VERY_LOW = 'VERY_LOW'
}

// User & Authentication
export interface User {
  id: string;
  email: string;
  name: string;
  institution?: string;
  role: 'researcher' | 'editor' | 'admin';
  createdAt: Date;
  lastLogin?: Date;
}

// Project Management
export interface Project {
  id: string;
  userId: string;
  toolType: ToolType;
  title: string;
  description?: string;
  status: ProjectStatus;
  workflows: Workflow[];
  findings?: Record<string, any>;
  auditTrail: AgentDecision[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Workflow {
  id: string;
  projectId: string;
  agentName: string;
  agentRole: string;
  inputData: Record<string, any>;
  outputData?: Record<string, any>;
  decisions: AgentDecision[];
  status: WorkflowStatus;
  errorMessage?: string;
  startedAt: Date;
  completedAt?: Date;
  durationSeconds?: number;
  progress?: number; // 0-100
}

// Agent System
export interface AgentDecision {
  agentName: string;
  agentRole: string;
  decision: string;
  reasoning: string;
  confidence: number; // 0-1
  timestamp: Date;
  metadata?: Record<string, any>;
}

export interface AgentMessage {
  from: string;
  to: string;
  message: string;
  timestamp: Date;
}

export interface AgentProgress {
  agentName: string;
  status: AgentStatus;
  currentTask?: string;
  progress: number; // 0-100
  eta?: number; // seconds
  message?: string;
}

// Shared Entities
export interface Paper {
  id: string;
  title: string;
  abstract: string;
  authors: string[];
  journal: string;
  year: number;
  doi?: string;
  pmid?: string;
  arxivId?: string;
  keywords: string[];
  databaseSource: string;
  credibilityLevel?: CredibilityLevel;
  credibilityScore?: number;
  extractedStatistics?: any;
  fullTextUrl?: string;
  pdfPath?: string;
  citationCount?: number;
  createdAt: Date;
}

export interface Researcher {
  id: string;
  orcid?: string;
  name: string;
  email?: string;
  institution: string;
  department?: string;
  country?: string;
  hIndex?: number;
  i10Index?: number;
  totalCitations?: number;
  publicationCount?: number;
  expertiseKeywords: string[];
  researchDomains: string[];
  recentPapers: string[]; // Paper IDs
  coauthors: string[]; // Researcher IDs
  recentReviewCount?: number;
  averageReviewTimeDays?: number;
  lastActive?: Date;
  createdAt: Date;
  updatedAt: Date;
}

// ===========================
// TOOL 1: META-ANALYSIS
// ===========================

export interface MetaAnalysisProject extends Project {
  toolType: ToolType.META_ANALYSIS;
  researchQuestion: string;
  topic: string;
  inclusionCriteria: string[];
  exclusionCriteria: string[];
  databases: string[];
  peerReviewOnly: boolean;
  searchResults?: SearchResults;
  screeningResults?: ScreeningResults;
  credibilityResults?: CredibilityResults;
  extractionResults?: DataExtractionResults;
  statisticalResults?: StatisticalResults;
  prismaFlow?: PrismaFlow;
}

export interface SearchResults {
  totalFound: number;
  databases: string[];
  studies: Paper[];
  searchDate: Date;
  queryDetails: Record<string, any>;
}

export interface ScreeningResults {
  included: number;
  excluded: number;
  uncertain: number;
  studies: Array<{
    paper: Paper;
    decision: 'included' | 'excluded' | 'uncertain';
    reasoning: string;
    confidence: number;
  }>;
}

export interface CredibilityResults {
  breakdown: {
    high: number;
    medium: number;
    low: number;
    very_low: number;
  };
  studiesWithScores: Array<{
    paper: Paper;
    credibility: {
      level: CredibilityLevel;
      score: number;
      reasoning: string;
      isPeerReviewed: boolean;
      isPreprint: boolean;
      replicability?: string;
    };
  }>;
}

export interface DataExtractionResults {
  extractedStudies: Array<{
    paper: Paper;
    effectSize?: number;
    sampleSize?: number;
    pValue?: number;
    confidenceInterval?: [number, number];
    statistics: Record<string, any>;
    confidence: number;
  }>;
}

export interface StatisticalResults {
  effectSize: number;
  confidenceInterval: [number, number];
  pValue: number;
  heterogeneity: {
    iSquared: number;
    tauSquared: number;
    qStatistic: number;
  };
  model: 'fixed' | 'random';
  forestPlot?: string; // URL or base64
  funnelPlot?: string;
  subgroupAnalysis?: any;
}

export interface PrismaFlow {
  identification: number;
  screening: number;
  eligibility: number;
  included: number;
  excluded: number;
  exclusionReasons: Record<string, number>;
  diagram?: string; // SVG or image URL
}

// ===========================
// TOOL 4: REVIEWER MATCHER
// ===========================

export interface ReviewerMatchProject extends Project {
  toolType: ToolType.REVIEWER_MATCHER;
  manuscriptTitle: string;
  manuscriptAbstract: string;
  manuscriptKeywords: string[];
  manuscriptFile?: string;
  journalId?: string;
  matches?: ReviewerMatch[];
}

export interface ReviewerMatch {
  id: string;
  manuscriptId: string;
  researcher: Researcher;
  expertiseScore: number; // 0-1
  availabilityScore: number; // 0-1
  conflictRisk: number; // 0-1
  overallScore: number; // 0-1
  ranking: number;
  reasoning: string;
  expertiseOverlap: string[];
  conflicts: ConflictDetection[];
  estimatedAvailability: {
    currentWorkload: 'low' | 'medium' | 'high';
    estimatedResponseTime: number; // days
    likelyToAccept: number; // 0-1
  };
  createdAt: Date;
}

export interface ConflictDetection {
  type: 'coauthorship' | 'citation' | 'institution' | 'collaboration';
  severity: 'high' | 'medium' | 'low';
  description: string;
  evidence: string[];
  timeframe?: string; // e.g., "last 5 years"
}

// ===========================
// TOOL 3: PEER REVIEW
// ===========================

export interface PeerReviewProject extends Project {
  toolType: ToolType.PEER_REVIEW;
  manuscriptId: string;
  manuscript: Manuscript;
  reviews?: GeneratedReview[];
  editorSummary?: EditorSummary;
}

export interface Manuscript {
  id: string;
  title: string;
  abstract: string;
  keywords: string[];
  authors: string[];
  submissionDate: Date;
  journalId?: string;
  filePath?: string;
  status: 'submitted' | 'under_review' | 'accepted' | 'rejected' | 'revision_required';
}

export interface GeneratedReview {
  id: string;
  manuscriptId: string;
  reviewerId?: string;
  reviewerType: 'ai' | 'human' | 'ai_assisted';
  recommendation: 'accept' | 'minor_revision' | 'major_revision' | 'reject';
  overallAssessment: string;
  strengths: string[];
  weaknesses: string[];
  detailedComments: ReviewSection[];
  constructiveFeedback: string;
  technicalAccuracy: number; // 1-5
  novelty: number; // 1-5
  clarity: number; // 1-5
  confidence: number; // 0-1
  biasScore?: number; // 0-1
  createdAt: Date;
}

export interface ReviewSection {
  section: string; // e.g., "Introduction", "Methodology", "Results"
  comments: string;
  rating?: number; // 1-5
  suggestions: string[];
}

export interface EditorSummary {
  manuscriptId: string;
  reviews: GeneratedReview[];
  consensus: string;
  disagreements: string[];
  recommendation: 'accept' | 'minor_revision' | 'major_revision' | 'reject';
  reasoning: string;
  keyPoints: string[];
  confidenceLevel: number; // 0-1
  createdAt: Date;
}

// ===========================
// TOOL 2: RESEARCH DIRECTION
// ===========================

export interface ResearchDirectionProject extends Project {
  toolType: ToolType.RESEARCH_DIRECTION;
  researcherOrcid?: string;
  publicationHistory?: Paper[];
  gaps?: ResearchGap[];
  trends?: ResearchTrend[];
  innovations?: MethodologicalInnovation[];
  proposals?: ResearchProposal[];
}

export interface ResearchGap {
  id: string;
  domain: string;
  description: string;
  evidence: string[];
  impactPotential: number; // 0-1
  feasibility: number; // 0-1
  noveltyScore: number; // 0-1
  reasoning: string;
  suggestedApproaches: string[];
  relatedPapers: Paper[];
  createdAt: Date;
}

export interface ResearchTrend {
  id: string;
  topic: string;
  description: string;
  trajectory: 'emerging' | 'growing' | 'mature' | 'declining';
  publicationVelocity: number; // papers per year
  citationVelocity: number; // citations per year
  emergingKeywords: string[];
  temporalData: Array<{
    year: number;
    publications: number;
    citations: number;
  }>;
  forecast?: string;
  createdAt: Date;
}

export interface MethodologicalInnovation {
  id: string;
  title: string;
  description: string;
  noveltyScore: number; // 0-1
  feasibilityScore: number; // 0-1
  crossDomainTransfer?: {
    fromDomain: string;
    toDomain: string;
    analogyReasoning: string;
  };
  expectedImpact: string;
  prerequisites: string[];
  potentialChallenges: string[];
  createdAt: Date;
}

export interface ResearchProposal {
  id: string;
  title: string;
  researchQuestion: string;
  background: string;
  significance: string;
  methodology: {
    approach: string;
    design: string;
    participants: string;
    measures: string;
    analysis: string;
  };
  expectedImpact: string;
  timeline: string;
  budget?: string;
  references: Paper[];
  impactPrediction: {
    expectedCitations: number;
    confidenceInterval: [number, number];
    noveltyScore: number;
    feasibilityScore: number;
  };
  format: 'NIH' | 'NSF' | 'general';
  createdAt: Date;
}

// ===========================
// UI STATE TYPES
// ===========================

export interface DashboardStats {
  totalProjects: number;
  activeProjects: number;
  completedProjects: number;
  projectsByTool: Record<ToolType, number>;
  recentActivity: ActivityItem[];
  quickActions: QuickAction[];
}

export interface ActivityItem {
  id: string;
  type: 'project_created' | 'project_completed' | 'workflow_started' | 'workflow_completed';
  projectId: string;
  projectTitle: string;
  toolType: ToolType;
  timestamp: Date;
  description: string;
}

export interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: string;
  toolType: ToolType;
  href: string;
  disabled?: boolean;
}

export interface NotificationMessage {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  actionUrl?: string;
}

// ===========================
// API RESPONSE TYPES
// ===========================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// ===========================
// CHART & VISUALIZATION TYPES
// ===========================

export interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }>;
}

export interface NetworkGraphNode {
  id: string;
  label: string;
  size: number;
  color?: string;
  metadata?: Record<string, any>;
}

export interface NetworkGraphEdge {
  source: string;
  target: string;
  weight: number;
  label?: string;
  color?: string;
}

export interface NetworkGraph {
  nodes: NetworkGraphNode[];
  edges: NetworkGraphEdge[];
}
