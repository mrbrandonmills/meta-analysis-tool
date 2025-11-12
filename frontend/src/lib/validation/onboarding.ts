/**
 * Comprehensive form validation for researcher onboarding
 * Uses schema-based validation with detailed error messages
 */

import { OnboardingData, ValidationErrors } from '@/types/onboarding';

// Validation rules
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const ORCID_REGEX = /^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$/;
const URL_REGEX = /^https?:\/\/.+/;

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationErrors;
}

/**
 * Validate Step 1: Basic Information
 */
export function validateBasicInfo(data: Partial<OnboardingData['basicInfo']>): ValidationResult {
  const errors: ValidationErrors = {};

  // Full Name
  if (!data?.fullName?.trim()) {
    errors.fullName = 'Full name is required';
  } else if (data.fullName.trim().length < 2) {
    errors.fullName = 'Full name must be at least 2 characters';
  } else if (data.fullName.trim().length > 100) {
    errors.fullName = 'Full name must not exceed 100 characters';
  }

  // Email
  if (!data?.email?.trim()) {
    errors.email = 'Email is required';
  } else if (!EMAIL_REGEX.test(data.email)) {
    errors.email = 'Please enter a valid email address';
  }

  // Institution
  if (!data?.institution?.trim()) {
    errors.institution = 'Institution is required';
  } else if (data.institution.trim().length < 2) {
    errors.institution = 'Institution name must be at least 2 characters';
  }

  // Department
  if (!data?.department?.trim()) {
    errors.department = 'Department is required';
  } else if (data.department.trim().length < 2) {
    errors.department = 'Department name must be at least 2 characters';
  }

  // Position
  if (!data?.position) {
    errors.position = 'Position is required';
  }

  // Country
  if (!data?.country) {
    errors.country = 'Country is required';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Validate Step 2: Academic Profile (all fields optional)
 */
export function validateAcademicProfile(
  data: Partial<OnboardingData['academicProfile']>
): ValidationResult {
  const errors: ValidationErrors = {};

  // ORCID ID (optional, but must be valid format if provided)
  if (data?.orcidId && !ORCID_REGEX.test(data.orcidId)) {
    errors.orcidId = 'Invalid ORCID ID format. Expected: 0000-0001-2345-6789';
  }

  // Google Scholar URL
  if (data?.googleScholarUrl && !URL_REGEX.test(data.googleScholarUrl)) {
    errors.googleScholarUrl = 'Please enter a valid URL starting with http:// or https://';
  } else if (
    data?.googleScholarUrl &&
    !data.googleScholarUrl.includes('scholar.google')
  ) {
    errors.googleScholarUrl = 'Please enter a valid Google Scholar URL';
  }

  // ResearchGate URL
  if (data?.researchGateUrl && !URL_REGEX.test(data.researchGateUrl)) {
    errors.researchGateUrl = 'Please enter a valid URL starting with http:// or https://';
  } else if (
    data?.researchGateUrl &&
    !data.researchGateUrl.includes('researchgate.net')
  ) {
    errors.researchGateUrl = 'Please enter a valid ResearchGate URL';
  }

  // Personal Website URL
  if (data?.personalWebsite && !URL_REGEX.test(data.personalWebsite)) {
    errors.personalWebsite = 'Please enter a valid URL starting with http:// or https://';
  }

  // H-index (if provided, must be non-negative)
  if (data?.hIndex !== undefined && data.hIndex < 0) {
    errors.hIndex = 'H-index cannot be negative';
  } else if (data?.hIndex !== undefined && data.hIndex > 500) {
    errors.hIndex = 'Please verify your h-index value (seems unusually high)';
  }

  // Total Citations (if provided, must be non-negative)
  if (data?.totalCitations !== undefined && data.totalCitations < 0) {
    errors.totalCitations = 'Total citations cannot be negative';
  } else if (data?.totalCitations !== undefined && data.totalCitations > 1000000) {
    errors.totalCitations = 'Please verify your citation count (seems unusually high)';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Validate Step 3: Research Expertise
 */
export function validateResearchExpertise(
  data: Partial<OnboardingData['researchExpertise']>
): ValidationResult {
  const errors: ValidationErrors = {};

  // Primary Domains (at least one required)
  const totalDomains =
    (data?.primaryDomains?.length || 0) + (data?.customDomains?.length || 0);

  if (totalDomains === 0) {
    errors.primaryDomains = 'Please select at least one research domain';
  } else if (totalDomains > 5) {
    errors.primaryDomains = 'Please select no more than 5 research domains';
  }

  // Keywords (minimum 5, maximum 20)
  const keywordCount = data?.keywords?.length || 0;

  if (keywordCount < 5) {
    errors.keywords = `Please add at least ${5 - keywordCount} more keyword${
      5 - keywordCount === 1 ? '' : 's'
    }`;
  } else if (keywordCount > 20) {
    errors.keywords = 'Please remove some keywords (maximum 20 allowed)';
  }

  // Validate individual keywords
  if (data?.keywords) {
    const invalidKeywords = data.keywords.filter(
      (keyword) => keyword.trim().length < 2 || keyword.trim().length > 50
    );
    if (invalidKeywords.length > 0) {
      errors.keywords = 'Keywords must be between 2 and 50 characters';
    }
  }

  // Methodologies (at least one required)
  if (!data?.methodologies || data.methodologies.length === 0) {
    errors.methodologies = 'Please select at least one research methodology';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Validate Step 4: Review Experience
 */
export function validateReviewExperience(
  data: Partial<OnboardingData['reviewExperience']>
): ValidationResult {
  const errors: ValidationErrors = {};

  // Experience Level
  if (!data?.experienceLevel) {
    errors.experienceLevel = 'Please select your review experience level';
  }

  // Max Concurrent Reviews
  if (!data?.maxConcurrentReviews) {
    errors.maxConcurrentReviews = 'Please select maximum concurrent reviews';
  } else if (data.maxConcurrentReviews < 1 || data.maxConcurrentReviews > 5) {
    errors.maxConcurrentReviews = 'Maximum concurrent reviews must be between 1 and 5';
  }

  // Preferred Review Time
  if (!data?.preferredReviewTime) {
    errors.preferredReviewTime = 'Please select your preferred review timeframe';
  } else if (![7, 14, 21, 30].includes(data.preferredReviewTime)) {
    errors.preferredReviewTime = 'Please select a valid review timeframe';
  }

  // Languages (at least one required)
  if (!data?.languages || data.languages.length === 0) {
    errors.languages = 'Please select at least one language';
  }

  // Journals Reviewed For (optional, but validate if provided)
  if (data?.journalsReviewedFor) {
    const invalidJournals = data.journalsReviewedFor.filter(
      (journal) => journal.trim().length < 2
    );
    if (invalidJournals.length > 0) {
      errors.journalsReviewedFor = 'Journal names must be at least 2 characters';
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Validate Step 5: Payment
 */
export function validatePaymentInfo(data: Partial<OnboardingData['payment']>): ValidationResult {
  const errors: ValidationErrors = {};

  // Payment Method ID (would be set by Stripe)
  // In production, this is validated by Stripe before submission

  // Billing Email
  if (!data?.billingEmail?.trim()) {
    errors.billingEmail = 'Billing email is required';
  } else if (!EMAIL_REGEX.test(data.billingEmail)) {
    errors.billingEmail = 'Please enter a valid billing email';
  }

  // Terms Agreement
  if (!data?.agreeToTerms) {
    errors.agreeToTerms = 'You must agree to the Terms of Service';
  }

  // Privacy Policy Agreement
  if (!data?.agreeToPrivacy) {
    errors.agreeToPrivacy = 'You must agree to the Privacy Policy';
  }

  // Payout Terms Agreement
  if (!data?.agreeToPayoutTerms) {
    errors.agreeToPayoutTerms = 'You must agree to the payout terms';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Validate entire onboarding form (all steps)
 */
export function validateOnboardingForm(data: Partial<OnboardingData>): {
  isValid: boolean;
  stepErrors: {
    step1: ValidationErrors;
    step2: ValidationErrors;
    step3: ValidationErrors;
    step4: ValidationErrors;
    step5: ValidationErrors;
  };
  summary: string[];
} {
  const step1 = validateBasicInfo(data.basicInfo || {});
  const step2 = validateAcademicProfile(data.academicProfile || {});
  const step3 = validateResearchExpertise(data.researchExpertise || {});
  const step4 = validateReviewExperience(data.reviewExperience || {});
  const step5 = validatePaymentInfo(data.payment || {});

  const allValid = step1.isValid && step2.isValid && step3.isValid && step4.isValid && step5.isValid;

  const summary: string[] = [];
  if (!step1.isValid) summary.push('Step 1: Basic Information has errors');
  if (!step2.isValid) summary.push('Step 2: Academic Profile has errors');
  if (!step3.isValid) summary.push('Step 3: Research Expertise has errors');
  if (!step4.isValid) summary.push('Step 4: Review Experience has errors');
  if (!step5.isValid) summary.push('Step 5: Payment & Agreements has errors');

  return {
    isValid: allValid,
    stepErrors: {
      step1: step1.errors,
      step2: step2.errors,
      step3: step3.errors,
      step4: step4.errors,
      step5: step5.errors,
    },
    summary,
  };
}

/**
 * Real-time field validation helper
 */
export function validateField(
  fieldName: string,
  value: any,
  context?: any
): string | undefined {
  switch (fieldName) {
    case 'email':
    case 'billingEmail':
      if (!value?.trim()) return 'Email is required';
      if (!EMAIL_REGEX.test(value)) return 'Invalid email format';
      return undefined;

    case 'orcidId':
      if (value && !ORCID_REGEX.test(value)) {
        return 'Invalid ORCID format (e.g., 0000-0001-2345-6789)';
      }
      return undefined;

    case 'googleScholarUrl':
      if (value && !URL_REGEX.test(value)) return 'Invalid URL format';
      if (value && !value.includes('scholar.google')) {
        return 'Must be a Google Scholar URL';
      }
      return undefined;

    case 'researchGateUrl':
      if (value && !URL_REGEX.test(value)) return 'Invalid URL format';
      if (value && !value.includes('researchgate.net')) {
        return 'Must be a ResearchGate URL';
      }
      return undefined;

    default:
      return undefined;
  }
}
