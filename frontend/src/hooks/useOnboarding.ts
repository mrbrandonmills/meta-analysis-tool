import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/router';
import toast from 'react-hot-toast';
import {
  OnboardingData,
  BasicInfo,
  AcademicProfile,
  ResearchExpertise,
  ReviewExperience,
  PaymentInfo,
} from '@/types/onboarding';
import { api } from '@/lib/api';

const ONBOARDING_STORAGE_KEY = 'researcher_onboarding_data';

interface UseOnboardingReturn {
  currentStep: number;
  formData: Partial<OnboardingData>;
  isSubmitting: boolean;
  error: string | null;
  nextStep: () => void;
  prevStep: () => void;
  goToStep: (step: number) => void;
  updateBasicInfo: (data: Partial<BasicInfo>) => void;
  updateAcademicProfile: (data: Partial<AcademicProfile>) => void;
  updateResearchExpertise: (data: Partial<ResearchExpertise>) => void;
  updateReviewExperience: (data: Partial<ReviewExperience>) => void;
  updatePaymentInfo: (data: Partial<PaymentInfo>) => void;
  submitOnboarding: () => Promise<void>;
  clearFormData: () => void;
}

export function useOnboarding(): UseOnboardingReturn {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<Partial<OnboardingData>>({
    basicInfo: {},
    academicProfile: {},
    researchExpertise: {
      primaryDomains: [],
      keywords: [],
      methodologies: [],
    },
    reviewExperience: {
      journalsReviewedFor: [],
      languages: [],
    },
    payment: {},
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load saved data from localStorage on mount
  useEffect(() => {
    const savedData = localStorage.getItem(ONBOARDING_STORAGE_KEY);
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData);
        setFormData(parsed.formData || formData);
        setCurrentStep(parsed.currentStep || 1);
      } catch (err) {
        console.error('Failed to parse saved onboarding data:', err);
      }
    }
  }, []);

  // Save to localStorage whenever formData or currentStep changes
  useEffect(() => {
    localStorage.setItem(
      ONBOARDING_STORAGE_KEY,
      JSON.stringify({ formData, currentStep })
    );
  }, [formData, currentStep]);

  const nextStep = useCallback(() => {
    setCurrentStep((prev) => Math.min(prev + 1, 5));
    window.scrollTo(0, 0);
  }, []);

  const prevStep = useCallback(() => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
    window.scrollTo(0, 0);
  }, []);

  const goToStep = useCallback((step: number) => {
    setCurrentStep(Math.max(1, Math.min(step, 5)));
    window.scrollTo(0, 0);
  }, []);

  const updateBasicInfo = useCallback((data: Partial<BasicInfo>) => {
    setFormData((prev) => ({
      ...prev,
      basicInfo: {
        ...prev.basicInfo,
        ...data,
      },
    }));
  }, []);

  const updateAcademicProfile = useCallback((data: Partial<AcademicProfile>) => {
    setFormData((prev) => ({
      ...prev,
      academicProfile: {
        ...prev.academicProfile,
        ...data,
      },
    }));
  }, []);

  const updateResearchExpertise = useCallback((data: Partial<ResearchExpertise>) => {
    setFormData((prev) => ({
      ...prev,
      researchExpertise: {
        ...prev.researchExpertise,
        ...data,
      },
    }));
  }, []);

  const updateReviewExperience = useCallback((data: Partial<ReviewExperience>) => {
    setFormData((prev) => ({
      ...prev,
      reviewExperience: {
        ...prev.reviewExperience,
        ...data,
      },
    }));
  }, []);

  const updatePaymentInfo = useCallback((data: Partial<PaymentInfo>) => {
    setFormData((prev) => ({
      ...prev,
      payment: {
        ...prev.payment,
        ...data,
      },
    }));
  }, []);

  const submitOnboarding = useCallback(async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      // Validate payment information
      if (!formData.payment?.stripePaymentMethodId) {
        throw new Error('Payment method is required');
      }

      if (!formData.payment?.agreeToTerms || !formData.payment?.agreeToPrivacy || !formData.payment?.agreeToPayoutTerms) {
        throw new Error('You must agree to all terms and policies');
      }

      // Step 1: Create subscription
      const subscriptionResponse = await api.post('/subscriptions/create', {
        payment_method_id: formData.payment.stripePaymentMethodId,
        billing_email: formData.payment.billingEmail || formData.basicInfo?.email,
      });

      // Step 2: Update researcher profile with all collected data
      const profileData = {
        full_name: formData.basicInfo?.fullName,
        email: formData.basicInfo?.email,
        institution: formData.basicInfo?.institution,
        department: formData.basicInfo?.department,
        position: formData.basicInfo?.position,
        country: formData.basicInfo?.country,
        orcid_id: formData.academicProfile?.orcidId,
        google_scholar_url: formData.academicProfile?.googleScholarUrl,
        researchgate_url: formData.academicProfile?.researchGateUrl,
        personal_website: formData.academicProfile?.personalWebsite,
        h_index: formData.academicProfile?.hIndex,
        total_citations: formData.academicProfile?.totalCitations,
        primary_domains: formData.researchExpertise?.primaryDomains,
        custom_domains: formData.researchExpertise?.customDomains,
        research_keywords: formData.researchExpertise?.keywords,
        methodologies: formData.researchExpertise?.methodologies,
        review_experience_level: formData.reviewExperience?.experienceLevel,
        journals_reviewed_for: formData.reviewExperience?.journalsReviewedFor,
        max_concurrent_reviews: formData.reviewExperience?.maxConcurrentReviews,
        preferred_review_time: formData.reviewExperience?.preferredReviewTime,
        availability_status: formData.reviewExperience?.availabilityStatus,
        languages: formData.reviewExperience?.languages,
        subscription_id: subscriptionResponse.data.subscription_id,
      };

      const userId = localStorage.getItem('user_id') || 'current';
      const profileResponse = await api.put(`/researchers/${userId}`, profileData);

      // Step 3: Trigger AI enrichment service
      await api.post(`/researchers/${userId}/enrich`, {
        google_scholar_url: formData.academicProfile?.googleScholarUrl,
        orcid_id: formData.academicProfile?.orcidId,
      });

      // Clear saved onboarding data
      localStorage.removeItem(ONBOARDING_STORAGE_KEY);

      // Show success message
      toast.success('Welcome to the peer review community!');

      // Redirect to success page
      router.push('/onboarding/success');

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to complete onboarding';
      setError(errorMessage);
      toast.error(errorMessage);
      console.error('Onboarding submission error:', err);
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, router]);

  const clearFormData = useCallback(() => {
    localStorage.removeItem(ONBOARDING_STORAGE_KEY);
    setFormData({
      basicInfo: {},
      academicProfile: {},
      researchExpertise: {
        primaryDomains: [],
        keywords: [],
        methodologies: [],
      },
      reviewExperience: {
        journalsReviewedFor: [],
        languages: [],
      },
      payment: {},
    });
    setCurrentStep(1);
  }, []);

  return {
    currentStep,
    formData,
    isSubmitting,
    error,
    nextStep,
    prevStep,
    goToStep,
    updateBasicInfo,
    updateAcademicProfile,
    updateResearchExpertise,
    updateReviewExperience,
    updatePaymentInfo,
    submitOnboarding,
    clearFormData,
  };
}

export default useOnboarding;
