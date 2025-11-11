import React, { useState } from 'react';
import { ArrowLeft, ArrowRight, X } from 'lucide-react';
import { useRouter } from 'next/router';
import { cn } from '@/lib/utils';
import { Button } from '@/components/shared/Button';
import StepIndicator from './StepIndicator';

interface OnboardingLayoutProps {
  currentStep: number;
  totalSteps: number;
  stepTitle: string;
  stepDescription: string;
  children: React.ReactNode;
  onNext?: () => void;
  onBack?: () => void;
  onSkip?: () => void;
  nextDisabled?: boolean;
  nextLoading?: boolean;
  nextLabel?: string;
  showSkip?: boolean;
  hideNavigation?: boolean;
  className?: string;
}

export const OnboardingLayout: React.FC<OnboardingLayoutProps> = ({
  currentStep,
  totalSteps,
  stepTitle,
  stepDescription,
  children,
  onNext,
  onBack,
  onSkip,
  nextDisabled = false,
  nextLoading = false,
  nextLabel,
  showSkip = false,
  hideNavigation = false,
  className,
}) => {
  const router = useRouter();
  const [showExitModal, setShowExitModal] = useState(false);

  const steps = Array.from({ length: totalSteps }, (_, i) => ({
    number: i + 1,
    title: `Step ${i + 1}`,
    description: '',
  }));

  const handleExit = () => {
    setShowExitModal(true);
  };

  const confirmExit = () => {
    router.push('/dashboard');
  };

  const getNextButtonLabel = () => {
    if (nextLabel) return nextLabel;
    if (currentStep === totalSteps) return 'Complete';
    return 'Continue';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                Researcher Onboarding
              </h1>
              <p className="text-sm text-gray-600 mt-0.5">Join the peer review community</p>
            </div>
            <button
              onClick={handleExit}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Exit onboarding"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Progress indicator */}
      <div className="max-w-5xl mx-auto px-6 py-8">
        <StepIndicator steps={steps} currentStep={currentStep} />
      </div>

      {/* Main content */}
      <div className="max-w-3xl mx-auto px-6 pb-12">
        <div
          className={cn(
            'bg-white/90 backdrop-blur-md rounded-2xl shadow-xl border border-white/20 overflow-hidden',
            className
          )}
        >
          {/* Step header */}
          <div className="px-8 py-6 bg-gradient-to-r from-green-500/10 to-emerald-500/10 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900">{stepTitle}</h2>
            <p className="text-gray-600 mt-1">{stepDescription}</p>
          </div>

          {/* Step content */}
          <div className="px-8 py-8">{children}</div>

          {/* Navigation */}
          {!hideNavigation && (
            <div className="px-8 py-6 bg-gray-50 border-t border-gray-200">
              <div className="flex items-center justify-between gap-4">
                <div className="flex gap-3">
                  {currentStep > 1 && onBack && (
                    <Button
                      variant="outline"
                      onClick={onBack}
                      icon={<ArrowLeft className="w-4 h-4" />}
                      disabled={nextLoading}
                    >
                      Back
                    </Button>
                  )}
                  {showSkip && onSkip && (
                    <Button
                      variant="ghost"
                      onClick={onSkip}
                      disabled={nextLoading}
                    >
                      Skip for now
                    </Button>
                  )}
                </div>

                {onNext && (
                  <Button
                    variant="primary"
                    onClick={onNext}
                    disabled={nextDisabled || nextLoading}
                    loading={nextLoading}
                    icon={
                      currentStep < totalSteps ? (
                        <ArrowRight className="w-4 h-4" />
                      ) : undefined
                    }
                    className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
                  >
                    {getNextButtonLabel()}
                  </Button>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Helper text */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Need help?{' '}
            <a
              href="mailto:support@metaanalysis.ai"
              className="text-green-600 hover:text-green-700 font-medium"
            >
              Contact support
            </a>
          </p>
        </div>
      </div>

      {/* Exit confirmation modal */}
      {showExitModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 overflow-hidden">
            <div className="px-6 py-5 bg-gradient-to-r from-orange-500/10 to-red-500/10 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-900">Exit Onboarding?</h3>
            </div>
            <div className="px-6 py-5">
              <p className="text-gray-700">
                Your progress will be saved, but you'll need to complete onboarding to access all
                features and start reviewing papers.
              </p>
            </div>
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-3 justify-end">
              <Button variant="outline" onClick={() => setShowExitModal(false)}>
                Continue Onboarding
              </Button>
              <Button variant="danger" onClick={confirmExit}>
                Exit Anyway
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OnboardingLayout;
