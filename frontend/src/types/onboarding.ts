/**
 * TypeScript types for researcher onboarding flow
 * Used for collecting comprehensive profile data for AI matching algorithm
 */

export type ResearchPosition =
  | 'phd_student'
  | 'postdoc'
  | 'assistant_professor'
  | 'associate_professor'
  | 'full_professor'
  | 'research_scientist'
  | 'other';

export type ResearchDomain =
  | 'psychology'
  | 'neuroscience'
  | 'cognitive_science'
  | 'clinical_psychology'
  | 'social_psychology'
  | 'developmental_psychology'
  | 'educational_psychology'
  | 'organizational_psychology'
  | 'other';

export type ResearchMethodology =
  | 'experimental'
  | 'computational'
  | 'clinical_trials'
  | 'surveys_questionnaires'
  | 'neuroimaging'
  | 'meta_analysis'
  | 'qualitative'
  | 'mixed_methods';

export type Language =
  | 'english'
  | 'spanish'
  | 'french'
  | 'german'
  | 'mandarin'
  | 'portuguese'
  | 'italian'
  | 'japanese'
  | 'korean'
  | 'russian'
  | 'arabic';

export type ReviewExperienceLevel = '0' | '1-5' | '6-10' | '11-20' | '21-50' | '50+';

export type PreferredReviewTime = 7 | 14 | 21 | 30;

export interface BasicInfo {
  fullName: string;
  email: string;
  institution: string;
  department: string;
  position: ResearchPosition;
  country: string;
}

export interface AcademicProfile {
  orcidId?: string;
  googleScholarUrl?: string;
  researchGateUrl?: string;
  personalWebsite?: string;
  hIndex?: number;
  totalCitations?: number;
}

export interface ResearchExpertise {
  primaryDomains: ResearchDomain[];
  customDomains?: string[];
  keywords: string[];
  methodologies: ResearchMethodology[];
}

export interface ReviewExperience {
  experienceLevel: ReviewExperienceLevel;
  journalsReviewedFor: string[];
  maxConcurrentReviews: number;
  preferredReviewTime: PreferredReviewTime;
  availabilityStatus: boolean;
  languages: Language[];
}

export interface PaymentInfo {
  stripePaymentMethodId: string;
  billingEmail: string;
  agreeToTerms: boolean;
  agreeToPrivacy: boolean;
  agreeToPayoutTerms: boolean;
}

export interface OnboardingData {
  basicInfo: BasicInfo;
  academicProfile: AcademicProfile;
  researchExpertise: ResearchExpertise;
  reviewExperience: ReviewExperience;
  payment: PaymentInfo;
}

export interface OnboardingStep {
  number: number;
  title: string;
  description: string;
  isComplete: boolean;
  isActive: boolean;
}

export interface ValidationErrors {
  [key: string]: string | undefined;
}

// Constants for form options
export const RESEARCH_POSITIONS: { value: ResearchPosition; label: string }[] = [
  { value: 'phd_student', label: 'PhD Student' },
  { value: 'postdoc', label: 'Postdoc' },
  { value: 'assistant_professor', label: 'Assistant Professor' },
  { value: 'associate_professor', label: 'Associate Professor' },
  { value: 'full_professor', label: 'Full Professor' },
  { value: 'research_scientist', label: 'Research Scientist' },
  { value: 'other', label: 'Other' },
];

export const RESEARCH_DOMAINS: { value: ResearchDomain; label: string }[] = [
  { value: 'psychology', label: 'Psychology' },
  { value: 'neuroscience', label: 'Neuroscience' },
  { value: 'cognitive_science', label: 'Cognitive Science' },
  { value: 'clinical_psychology', label: 'Clinical Psychology' },
  { value: 'social_psychology', label: 'Social Psychology' },
  { value: 'developmental_psychology', label: 'Developmental Psychology' },
  { value: 'educational_psychology', label: 'Educational Psychology' },
  { value: 'organizational_psychology', label: 'Organizational Psychology' },
  { value: 'other', label: 'Other' },
];

export const RESEARCH_METHODOLOGIES: { value: ResearchMethodology; label: string }[] = [
  { value: 'experimental', label: 'Experimental' },
  { value: 'computational', label: 'Computational' },
  { value: 'clinical_trials', label: 'Clinical Trials' },
  { value: 'surveys_questionnaires', label: 'Surveys/Questionnaires' },
  { value: 'neuroimaging', label: 'Neuroimaging' },
  { value: 'meta_analysis', label: 'Meta-analysis' },
  { value: 'qualitative', label: 'Qualitative' },
  { value: 'mixed_methods', label: 'Mixed Methods' },
];

export const LANGUAGES: { value: Language; label: string }[] = [
  { value: 'english', label: 'English' },
  { value: 'spanish', label: 'Spanish' },
  { value: 'french', label: 'French' },
  { value: 'german', label: 'German' },
  { value: 'mandarin', label: 'Mandarin' },
  { value: 'portuguese', label: 'Portuguese' },
  { value: 'italian', label: 'Italian' },
  { value: 'japanese', label: 'Japanese' },
  { value: 'korean', label: 'Korean' },
  { value: 'russian', label: 'Russian' },
  { value: 'arabic', label: 'Arabic' },
];

export const REVIEW_EXPERIENCE_LEVELS: { value: ReviewExperienceLevel; label: string }[] = [
  { value: '0', label: 'No previous reviews' },
  { value: '1-5', label: '1-5 reviews' },
  { value: '6-10', label: '6-10 reviews' },
  { value: '11-20', label: '11-20 reviews' },
  { value: '21-50', label: '21-50 reviews' },
  { value: '50+', label: '50+ reviews' },
];

export const PREFERRED_REVIEW_TIMES: { value: PreferredReviewTime; label: string }[] = [
  { value: 7, label: '7 days' },
  { value: 14, label: '14 days' },
  { value: 21, label: '21 days' },
  { value: 30, label: '30 days' },
];

export const MAX_CONCURRENT_REVIEWS: { value: number; label: string }[] = [
  { value: 1, label: '1 review' },
  { value: 2, label: '2 reviews' },
  { value: 3, label: '3 reviews' },
  { value: 4, label: '4 reviews' },
  { value: 5, label: '5 reviews' },
];

// Common psychology research keywords for autocomplete
export const COMMON_RESEARCH_KEYWORDS = [
  'fMRI',
  'EEG',
  'cognitive load',
  'working memory',
  'attention',
  'executive function',
  'neuroplasticity',
  'neuroimaging',
  'psychotherapy',
  'depression',
  'anxiety',
  'PTSD',
  'social cognition',
  'emotion regulation',
  'decision making',
  'learning',
  'memory consolidation',
  'behavioral economics',
  'developmental disorders',
  'aging',
  'brain connectivity',
  'machine learning',
  'statistical modeling',
  'randomized controlled trial',
  'longitudinal study',
  'cross-cultural research',
];

// Top universities for autocomplete
export const COMMON_UNIVERSITIES = [
  'Stanford University',
  'Harvard University',
  'MIT',
  'University of California, Berkeley',
  'Oxford University',
  'Cambridge University',
  'Yale University',
  'Princeton University',
  'Columbia University',
  'University of Pennsylvania',
  'University of Chicago',
  'Johns Hopkins University',
  'Duke University',
  'Northwestern University',
  'Cornell University',
  'University of Michigan',
  'University of Toronto',
  'ETH Zurich',
  'Imperial College London',
  'University College London',
];
