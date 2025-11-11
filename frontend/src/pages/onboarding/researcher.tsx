import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import {
  User,
  GraduationCap,
  Microscope,
  FileCheck,
  CreditCard,
  HelpCircle,
  Globe,
  Mail,
  Building,
  Users,
  MapPin,
} from 'lucide-react';
import OnboardingLayout from '@/components/onboarding/OnboardingLayout';
import ResearchDomainSelector from '@/components/onboarding/ResearchDomainSelector';
import KeywordInput from '@/components/onboarding/KeywordInput';
import StripePaymentForm from '@/components/onboarding/StripePaymentForm';
import { useOnboarding } from '@/hooks/useOnboarding';
import {
  ResearchDomain,
  ResearchMethodology,
  Language,
  RESEARCH_POSITIONS,
  RESEARCH_METHODOLOGIES,
  LANGUAGES,
  REVIEW_EXPERIENCE_LEVELS,
  PREFERRED_REVIEW_TIMES,
  MAX_CONCURRENT_REVIEWS,
  COMMON_UNIVERSITIES,
} from '@/types/onboarding';
import { cn } from '@/lib/utils';

// Country list (abbreviated for space - expand as needed)
const COUNTRIES = [
  'United States',
  'United Kingdom',
  'Canada',
  'Germany',
  'France',
  'Netherlands',
  'Switzerland',
  'Australia',
  'Japan',
  'China',
  'Singapore',
  'Sweden',
  'Other',
];

export default function ResearcherOnboarding() {
  const router = useRouter();
  const {
    currentStep,
    formData,
    isSubmitting,
    error,
    nextStep,
    prevStep,
    updateBasicInfo,
    updateAcademicProfile,
    updateResearchExpertise,
    updateReviewExperience,
    updatePaymentInfo,
    submitOnboarding,
  } = useOnboarding();

  // Validation states for each step
  const [step1Valid, setStep1Valid] = useState(false);
  const [step3Valid, setStep3Valid] = useState(false);
  const [step4Valid, setStep4Valid] = useState(false);
  const [step5Valid, setStep5Valid] = useState(false);

  // Step 1: Basic Information validation
  useEffect(() => {
    const valid =
      !!formData.basicInfo?.fullName &&
      !!formData.basicInfo?.email &&
      !!formData.basicInfo?.institution &&
      !!formData.basicInfo?.department &&
      !!formData.basicInfo?.position &&
      !!formData.basicInfo?.country;
    setStep1Valid(valid);
  }, [formData.basicInfo]);

  // Step 3: Research Expertise validation
  useEffect(() => {
    const domains = formData.researchExpertise?.primaryDomains?.length || 0;
    const customDomains = formData.researchExpertise?.customDomains?.length || 0;
    const keywords = formData.researchExpertise?.keywords?.length || 0;
    const methodologies = formData.researchExpertise?.methodologies?.length || 0;

    const valid = domains + customDomains > 0 && keywords >= 5 && methodologies > 0;
    setStep3Valid(valid);
  }, [formData.researchExpertise]);

  // Step 4: Review Experience validation
  useEffect(() => {
    const valid =
      !!formData.reviewExperience?.experienceLevel &&
      !!formData.reviewExperience?.maxConcurrentReviews &&
      !!formData.reviewExperience?.preferredReviewTime &&
      (formData.reviewExperience?.languages?.length || 0) > 0;
    setStep4Valid(valid);
  }, [formData.reviewExperience]);

  // Step 5: Payment validation
  useEffect(() => {
    const valid =
      !!formData.payment?.agreeToTerms &&
      !!formData.payment?.agreeToPrivacy &&
      !!formData.payment?.agreeToPayoutTerms;
    setStep5Valid(valid);
  }, [formData.payment]);

  const handleNext = () => {
    if (currentStep === 5) {
      submitOnboarding();
    } else {
      nextStep();
    }
  };

  const getStepConfig = () => {
    switch (currentStep) {
      case 1:
        return {
          title: 'Basic Information',
          description: 'Tell us about yourself and your institution',
          icon: User,
        };
      case 2:
        return {
          title: 'Academic Profile',
          description: 'Connect your academic profiles for enhanced matching',
          icon: GraduationCap,
        };
      case 3:
        return {
          title: 'Research Expertise',
          description: 'Help us understand your research focus and methodology',
          icon: Microscope,
        };
      case 4:
        return {
          title: 'Peer Review Experience',
          description: 'Share your review experience and availability',
          icon: FileCheck,
        };
      case 5:
        return {
          title: 'Subscription & Payment',
          description: 'Complete your subscription to join the community',
          icon: CreditCard,
        };
      default:
        return { title: '', description: '', icon: User };
    }
  };

  const stepConfig = getStepConfig();

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return <Step1BasicInfo formData={formData} updateBasicInfo={updateBasicInfo} />;
      case 2:
        return (
          <Step2AcademicProfile
            formData={formData}
            updateAcademicProfile={updateAcademicProfile}
          />
        );
      case 3:
        return (
          <Step3ResearchExpertise
            formData={formData}
            updateResearchExpertise={updateResearchExpertise}
          />
        );
      case 4:
        return (
          <Step4ReviewExperience
            formData={formData}
            updateReviewExperience={updateReviewExperience}
          />
        );
      case 5:
        return <Step5Payment formData={formData} updatePaymentInfo={updatePaymentInfo} />;
      default:
        return null;
    }
  };

  const isNextDisabled = () => {
    switch (currentStep) {
      case 1:
        return !step1Valid;
      case 2:
        return false; // Step 2 is optional
      case 3:
        return !step3Valid;
      case 4:
        return !step4Valid;
      case 5:
        return !step5Valid;
      default:
        return false;
    }
  };

  return (
    <OnboardingLayout
      currentStep={currentStep}
      totalSteps={5}
      stepTitle={stepConfig.title}
      stepDescription={stepConfig.description}
      onNext={handleNext}
      onBack={currentStep > 1 ? prevStep : undefined}
      nextDisabled={isNextDisabled()}
      nextLoading={isSubmitting}
      nextLabel={currentStep === 5 ? 'Subscribe & Complete' : undefined}
      showSkip={currentStep === 2}
      onSkip={currentStep === 2 ? nextStep : undefined}
    >
      {renderStepContent()}
    </OnboardingLayout>
  );
}

// Step 1: Basic Information
function Step1BasicInfo({ formData, updateBasicInfo }: any) {
  const [institutionSuggestions, setInstitutionSuggestions] = useState<string[]>([]);
  const [showInstitutionSuggestions, setShowInstitutionSuggestions] = useState(false);

  const handleInstitutionChange = (value: string) => {
    updateBasicInfo({ institution: value });
    if (value.length > 1) {
      const filtered = COMMON_UNIVERSITIES.filter((uni) =>
        uni.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 5);
      setInstitutionSuggestions(filtered);
      setShowInstitutionSuggestions(filtered.length > 0);
    } else {
      setShowInstitutionSuggestions(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Full Name */}
      <div>
        <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-2">
          Full Name <span className="text-red-500">*</span>
        </label>
        <div className="relative">
          <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            id="fullName"
            type="text"
            value={formData.basicInfo?.fullName || ''}
            onChange={(e) => updateBasicInfo({ fullName: e.target.value })}
            placeholder="Dr. Jane Smith"
            className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          />
        </div>
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
          Email <span className="text-red-500">*</span>
        </label>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            id="email"
            type="email"
            value={formData.basicInfo?.email || ''}
            onChange={(e) => updateBasicInfo({ email: e.target.value })}
            placeholder="jane.smith@university.edu"
            className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          />
        </div>
      </div>

      {/* Institution */}
      <div className="relative">
        <label htmlFor="institution" className="block text-sm font-medium text-gray-700 mb-2">
          Institution <span className="text-red-500">*</span>
        </label>
        <div className="relative">
          <Building className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            id="institution"
            type="text"
            value={formData.basicInfo?.institution || ''}
            onChange={(e) => handleInstitutionChange(e.target.value)}
            onBlur={() => setTimeout(() => setShowInstitutionSuggestions(false), 200)}
            placeholder="Stanford University"
            className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          />
        </div>
        {showInstitutionSuggestions && (
          <div className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
            {institutionSuggestions.map((uni) => (
              <button
                key={uni}
                type="button"
                onClick={() => {
                  updateBasicInfo({ institution: uni });
                  setShowInstitutionSuggestions(false);
                }}
                className="w-full px-4 py-2 text-left hover:bg-green-50 transition-colors"
              >
                {uni}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Department */}
      <div>
        <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-2">
          Department <span className="text-red-500">*</span>
        </label>
        <div className="relative">
          <Users className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            id="department"
            type="text"
            value={formData.basicInfo?.department || ''}
            onChange={(e) => updateBasicInfo({ department: e.target.value })}
            placeholder="Psychology"
            className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          />
        </div>
      </div>

      {/* Position */}
      <div>
        <label htmlFor="position" className="block text-sm font-medium text-gray-700 mb-2">
          Position <span className="text-red-500">*</span>
        </label>
        <select
          id="position"
          value={formData.basicInfo?.position || ''}
          onChange={(e) => updateBasicInfo({ position: e.target.value })}
          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          required
        >
          <option value="">Select your position</option>
          {RESEARCH_POSITIONS.map((pos) => (
            <option key={pos.value} value={pos.value}>
              {pos.label}
            </option>
          ))}
        </select>
      </div>

      {/* Country */}
      <div>
        <label htmlFor="country" className="block text-sm font-medium text-gray-700 mb-2">
          Country <span className="text-red-500">*</span>
        </label>
        <div className="relative">
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <select
            id="country"
            value={formData.basicInfo?.country || ''}
            onChange={(e) => updateBasicInfo({ country: e.target.value })}
            className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent appearance-none"
            required
          >
            <option value="">Select your country</option>
            {COUNTRIES.map((country) => (
              <option key={country} value={country}>
                {country}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}

// Step 2: Academic Profile
function Step2AcademicProfile({ formData, updateAcademicProfile }: any) {
  return (
    <div className="space-y-6">
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          This step is optional, but connecting your profiles helps our AI matching algorithm find the best papers for you to review.
        </p>
      </div>

      {/* ORCID ID */}
      <div>
        <label htmlFor="orcidId" className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
          ORCID ID
          <button
            type="button"
            className="text-gray-400 hover:text-gray-600"
            title="ORCID provides a persistent digital identifier for researchers"
          >
            <HelpCircle className="w-4 h-4" />
          </button>
        </label>
        <input
          id="orcidId"
          type="text"
          value={formData.academicProfile?.orcidId || ''}
          onChange={(e) => updateAcademicProfile({ orcidId: e.target.value })}
          placeholder="0000-0001-2345-6789"
          pattern="[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]"
          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">Format: 0000-0001-2345-6789</p>
      </div>

      {/* Google Scholar */}
      <div>
        <label htmlFor="googleScholar" className="block text-sm font-medium text-gray-700 mb-2">
          Google Scholar Profile URL
        </label>
        <div className="relative">
          <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            id="googleScholar"
            type="url"
            value={formData.academicProfile?.googleScholarUrl || ''}
            onChange={(e) => updateAcademicProfile({ googleScholarUrl: e.target.value })}
            placeholder="https://scholar.google.com/citations?user=..."
            className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* ResearchGate */}
      <div>
        <label htmlFor="researchGate" className="block text-sm font-medium text-gray-700 mb-2">
          ResearchGate Profile URL
        </label>
        <div className="relative">
          <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            id="researchGate"
            type="url"
            value={formData.academicProfile?.researchGateUrl || ''}
            onChange={(e) => updateAcademicProfile({ researchGateUrl: e.target.value })}
            placeholder="https://www.researchgate.net/profile/..."
            className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Personal Website */}
      <div>
        <label htmlFor="website" className="block text-sm font-medium text-gray-700 mb-2">
          Personal Website
        </label>
        <div className="relative">
          <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            id="website"
            type="url"
            value={formData.academicProfile?.personalWebsite || ''}
            onChange={(e) => updateAcademicProfile({ personalWebsite: e.target.value })}
            placeholder="https://yourwebsite.com"
            className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* H-index and Citations */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="hIndex" className="block text-sm font-medium text-gray-700 mb-2">
            H-index
          </label>
          <input
            id="hIndex"
            type="number"
            min="0"
            value={formData.academicProfile?.hIndex || ''}
            onChange={(e) =>
              updateAcademicProfile({ hIndex: parseInt(e.target.value) || undefined })
            }
            placeholder="0"
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>
        <div>
          <label htmlFor="citations" className="block text-sm font-medium text-gray-700 mb-2">
            Total Citations
          </label>
          <input
            id="citations"
            type="number"
            min="0"
            value={formData.academicProfile?.totalCitations || ''}
            onChange={(e) =>
              updateAcademicProfile({ totalCitations: parseInt(e.target.value) || undefined })
            }
            placeholder="0"
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>
      </div>

      <p className="text-xs text-gray-500 italic">
        If you provide a Google Scholar profile, we'll automatically fetch your h-index and citation count
      </p>
    </div>
  );
}

// Step 3: Research Expertise
function Step3ResearchExpertise({ formData, updateResearchExpertise }: any) {
  const handleDomainChange = (domains: ResearchDomain[], customDomains?: string[]) => {
    updateResearchExpertise({ primaryDomains: domains, customDomains });
  };

  const handleKeywordChange = (keywords: string[]) => {
    updateResearchExpertise({ keywords });
  };

  const handleMethodologyToggle = (methodology: ResearchMethodology) => {
    const current = formData.researchExpertise?.methodologies || [];
    const updated = current.includes(methodology)
      ? current.filter((m: ResearchMethodology) => m !== methodology)
      : [...current, methodology];
    updateResearchExpertise({ methodologies: updated });
  };

  return (
    <div className="space-y-8">
      {/* Research Domains */}
      <ResearchDomainSelector
        selectedDomains={formData.researchExpertise?.primaryDomains || []}
        customDomains={formData.researchExpertise?.customDomains}
        onChange={handleDomainChange}
      />

      {/* Keywords */}
      <KeywordInput
        keywords={formData.researchExpertise?.keywords || []}
        onChange={handleKeywordChange}
      />

      {/* Methodologies */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Research Methodologies <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 gap-3">
          {RESEARCH_METHODOLOGIES.map((method) => {
            const isSelected = (formData.researchExpertise?.methodologies || []).includes(
              method.value
            );
            return (
              <button
                key={method.value}
                type="button"
                onClick={() => handleMethodologyToggle(method.value)}
                className={cn(
                  'px-4 py-3 rounded-lg text-sm font-medium transition-all border-2',
                  isSelected
                    ? 'bg-green-50 border-green-500 text-green-700'
                    : 'bg-white border-gray-300 text-gray-700 hover:border-green-300'
                )}
              >
                {method.label}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// Step 4: Review Experience
function Step4ReviewExperience({ formData, updateReviewExperience }: any) {
  const [journalInput, setJournalInput] = useState('');

  const handleAddJournal = () => {
    if (journalInput.trim()) {
      const current = formData.reviewExperience?.journalsReviewedFor || [];
      updateReviewExperience({
        journalsReviewedFor: [...current, journalInput.trim()],
      });
      setJournalInput('');
    }
  };

  const handleRemoveJournal = (journal: string) => {
    const current = formData.reviewExperience?.journalsReviewedFor || [];
    updateReviewExperience({
      journalsReviewedFor: current.filter((j: string) => j !== journal),
    });
  };

  const handleLanguageToggle = (language: Language) => {
    const current = formData.reviewExperience?.languages || [];
    const updated = current.includes(language)
      ? current.filter((l: Language) => l !== language)
      : [...current, language];
    updateReviewExperience({ languages: updated });
  };

  return (
    <div className="space-y-6">
      {/* Experience Level */}
      <div>
        <label htmlFor="experienceLevel" className="block text-sm font-medium text-gray-700 mb-2">
          Previous Review Experience <span className="text-red-500">*</span>
        </label>
        <select
          id="experienceLevel"
          value={formData.reviewExperience?.experienceLevel || ''}
          onChange={(e) => updateReviewExperience({ experienceLevel: e.target.value })}
          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          required
        >
          <option value="">Select experience level</option>
          {REVIEW_EXPERIENCE_LEVELS.map((level) => (
            <option key={level.value} value={level.value}>
              {level.label}
            </option>
          ))}
        </select>
      </div>

      {/* Journals Reviewed For */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Journals Reviewed For
        </label>
        <div className="space-y-2">
          {(formData.reviewExperience?.journalsReviewedFor || []).map((journal: string) => (
            <div
              key={journal}
              className="flex items-center justify-between px-4 py-2 bg-gray-50 rounded-lg"
            >
              <span className="text-sm text-gray-700">{journal}</span>
              <button
                type="button"
                onClick={() => handleRemoveJournal(journal)}
                className="text-red-500 hover:text-red-700"
              >
                Remove
              </button>
            </div>
          ))}
          <div className="flex gap-2">
            <input
              type="text"
              value={journalInput}
              onChange={(e) => setJournalInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddJournal()}
              placeholder="Journal name"
              className="flex-1 px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            <button
              type="button"
              onClick={handleAddJournal}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Add
            </button>
          </div>
        </div>
      </div>

      {/* Max Concurrent Reviews */}
      <div>
        <label htmlFor="maxReviews" className="block text-sm font-medium text-gray-700 mb-2">
          Maximum Concurrent Reviews <span className="text-red-500">*</span>
        </label>
        <select
          id="maxReviews"
          value={formData.reviewExperience?.maxConcurrentReviews || ''}
          onChange={(e) =>
            updateReviewExperience({ maxConcurrentReviews: parseInt(e.target.value) })
          }
          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          required
        >
          <option value="">Select maximum</option>
          {MAX_CONCURRENT_REVIEWS.map((max) => (
            <option key={max.value} value={max.value}>
              {max.label}
            </option>
          ))}
        </select>
      </div>

      {/* Preferred Review Time */}
      <div>
        <label htmlFor="reviewTime" className="block text-sm font-medium text-gray-700 mb-2">
          Preferred Review Time <span className="text-red-500">*</span>
        </label>
        <select
          id="reviewTime"
          value={formData.reviewExperience?.preferredReviewTime || ''}
          onChange={(e) =>
            updateReviewExperience({ preferredReviewTime: parseInt(e.target.value) })
          }
          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          required
        >
          <option value="">Select timeframe</option>
          {PREFERRED_REVIEW_TIMES.map((time) => (
            <option key={time.value} value={time.value}>
              {time.label}
            </option>
          ))}
        </select>
      </div>

      {/* Availability */}
      <div>
        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={formData.reviewExperience?.availabilityStatus || false}
            onChange={(e) => updateReviewExperience({ availabilityStatus: e.target.checked })}
            className="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500"
          />
          <span className="text-sm font-medium text-gray-700">
            I am currently available for peer reviews
          </span>
        </label>
      </div>

      {/* Languages */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Languages <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {LANGUAGES.map((lang) => {
            const isSelected = (formData.reviewExperience?.languages || []).includes(lang.value);
            return (
              <button
                key={lang.value}
                type="button"
                onClick={() => handleLanguageToggle(lang.value)}
                className={cn(
                  'px-3 py-2 rounded-lg text-sm font-medium transition-all border-2',
                  isSelected
                    ? 'bg-green-50 border-green-500 text-green-700'
                    : 'bg-white border-gray-300 text-gray-700 hover:border-green-300'
                )}
              >
                {lang.label}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// Step 5: Payment
function Step5Payment({ formData, updatePaymentInfo }: any) {
  const handlePaymentSuccess = (paymentMethodId: string) => {
    updatePaymentInfo({
      stripePaymentMethodId: paymentMethodId,
      billingEmail: formData.basicInfo?.email,
    });
  };

  const handlePaymentError = (error: string) => {
    console.error('Payment error:', error);
  };

  return (
    <div className="space-y-6">
      {/* Pricing breakdown */}
      <div className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border-2 border-green-200">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Subscription Details</h3>

        <div className="space-y-3 mb-6">
          <div className="flex justify-between items-center">
            <span className="text-gray-700">Monthly Subscription</span>
            <span className="text-2xl font-bold text-green-600">$100</span>
          </div>

          <div className="border-t border-green-200 pt-3 space-y-2 text-sm">
            <div className="flex justify-between text-gray-600">
              <span>Platform Access</span>
              <span>$80</span>
            </div>
            <div className="flex justify-between text-gray-600">
              <span>Review Pool Contribution</span>
              <span>$20</span>
            </div>
          </div>
        </div>

        <div className="p-4 bg-white rounded-lg border border-green-200">
          <h4 className="font-semibold text-gray-900 mb-2">Monthly Payout System</h4>
          <p className="text-sm text-gray-700 mb-3">
            Complete approved reviews to earn from the monthly pool
          </p>
          <div className="text-xs text-gray-600 space-y-1">
            <p className="font-medium">Example calculation:</p>
            <p>If 10 researchers contribute $20 each ($200 pool) and you complete 2 out of 10 reviews, you earn $40</p>
            <p className="text-green-600 font-medium mt-2">High-quality reviews = Higher earnings!</p>
          </div>
        </div>
      </div>

      {/* Payment form */}
      <StripePaymentForm
        onSuccess={handlePaymentSuccess}
        onError={handlePaymentError}
        billingEmail={formData.basicInfo?.email || ''}
      />

      {/* Terms and agreements */}
      <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={formData.payment?.agreeToTerms || false}
            onChange={(e) => updatePaymentInfo({ agreeToTerms: e.target.checked })}
            className="mt-1 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
            required
          />
          <span className="text-sm text-gray-700">
            I agree to the{' '}
            <a href="/terms" target="_blank" className="text-green-600 hover:text-green-700 underline">
              Terms of Service
            </a>
          </span>
        </label>

        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={formData.payment?.agreeToPrivacy || false}
            onChange={(e) => updatePaymentInfo({ agreeToPrivacy: e.target.checked })}
            className="mt-1 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
            required
          />
          <span className="text-sm text-gray-700">
            I agree to the{' '}
            <a href="/privacy" target="_blank" className="text-green-600 hover:text-green-700 underline">
              Privacy Policy
            </a>
          </span>
        </label>

        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={formData.payment?.agreeToPayoutTerms || false}
            onChange={(e) => updatePaymentInfo({ agreeToPayoutTerms: e.target.checked })}
            className="mt-1 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
            required
          />
          <span className="text-sm text-gray-700">
            I understand that payouts are distributed monthly based on completed, approved reviews
          </span>
        </label>
      </div>
    </div>
  );
}
