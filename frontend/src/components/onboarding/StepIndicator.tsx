import React from 'react';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Step {
  number: number;
  title: string;
  description: string;
}

interface StepIndicatorProps {
  steps: Step[];
  currentStep: number;
  className?: string;
}

export const StepIndicator: React.FC<StepIndicatorProps> = ({
  steps,
  currentStep,
  className,
}) => {
  return (
    <div className={cn('w-full', className)}>
      {/* Progress bar */}
      <div className="relative">
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200">
          <div
            className="h-full bg-gradient-to-r from-green-500 to-emerald-600 transition-all duration-500 ease-out"
            style={{
              width: `${((currentStep - 1) / (steps.length - 1)) * 100}%`,
            }}
          />
        </div>

        {/* Steps */}
        <div className="relative flex justify-between">
          {steps.map((step) => {
            const isComplete = step.number < currentStep;
            const isActive = step.number === currentStep;
            const isFuture = step.number > currentStep;

            return (
              <div
                key={step.number}
                className="flex flex-col items-center"
                style={{ width: `${100 / steps.length}%` }}
              >
                {/* Circle node */}
                <div
                  className={cn(
                    'w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 relative z-10',
                    isComplete &&
                      'bg-gradient-to-br from-green-500 to-emerald-600 shadow-lg scale-100',
                    isActive &&
                      'bg-gradient-to-br from-green-500 to-emerald-600 shadow-xl scale-110 ring-4 ring-green-100',
                    isFuture && 'bg-gray-200'
                  )}
                  aria-current={isActive ? 'step' : undefined}
                  aria-label={`Step ${step.number}: ${step.title}`}
                >
                  {isComplete ? (
                    <Check className="w-5 h-5 text-white" aria-hidden="true" />
                  ) : (
                    <span
                      className={cn(
                        'text-sm font-semibold',
                        isActive ? 'text-white' : 'text-gray-500'
                      )}
                    >
                      {step.number}
                    </span>
                  )}
                </div>

                {/* Step label */}
                <div className="mt-3 text-center">
                  <p
                    className={cn(
                      'text-sm font-medium transition-colors',
                      isActive
                        ? 'text-green-600'
                        : isComplete
                        ? 'text-gray-700'
                        : 'text-gray-400'
                    )}
                  >
                    {step.title}
                  </p>
                  <p
                    className={cn(
                      'text-xs mt-1 transition-colors hidden sm:block',
                      isActive
                        ? 'text-gray-600'
                        : 'text-gray-400'
                    )}
                  >
                    {step.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Mobile progress text */}
      <div className="mt-6 sm:hidden">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">
            Step {currentStep} of {steps.length}
          </span>
          <span className="text-sm font-medium text-green-600">
            {Math.round(((currentStep - 1) / (steps.length - 1)) * 100)}% Complete
          </span>
        </div>
        <div className="mt-2 text-sm text-gray-700 font-medium">
          {steps[currentStep - 1]?.title}
        </div>
      </div>
    </div>
  );
};

export default StepIndicator;
