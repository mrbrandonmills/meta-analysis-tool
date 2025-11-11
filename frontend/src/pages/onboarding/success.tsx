import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import {
  CheckCircle,
  Sparkles,
  FileSearch,
  UserCheck,
  TrendingUp,
  ArrowRight,
  Loader2,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/shared/Button';
import { cn } from '@/lib/utils';

const ENRICHMENT_STEPS = [
  {
    id: 'google_scholar',
    label: 'Fetching Google Scholar data',
    description: 'Citations, h-index, publications',
    icon: FileSearch,
    duration: 3000,
  },
  {
    id: 'orcid',
    label: 'Enriching ORCID profile',
    description: 'Research areas, affiliations',
    icon: UserCheck,
    duration: 2500,
  },
  {
    id: 'analysis',
    label: 'AI-powered profile analysis',
    description: 'Expertise mapping, matching algorithm',
    icon: Sparkles,
    duration: 3500,
  },
  {
    id: 'complete',
    label: 'Profile complete!',
    description: 'Ready for peer review matching',
    icon: CheckCircle,
    duration: 1000,
  },
];

const NEXT_STEPS = [
  {
    title: 'Complete Your Profile',
    description: 'Add more details to improve matching accuracy',
    action: 'Go to Settings',
    href: '/settings',
    icon: UserCheck,
    color: 'blue',
  },
  {
    title: 'Browse Available Papers',
    description: 'See papers waiting for review in your expertise area',
    action: 'View Papers',
    href: '/papers',
    icon: FileSearch,
    color: 'purple',
  },
  {
    title: 'Get Matched',
    description: 'Our AI will match you with relevant papers',
    action: 'Start Reviewing',
    href: '/dashboard',
    icon: Sparkles,
    color: 'green',
  },
];

export default function OnboardingSuccess() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [isEnrichmentComplete, setIsEnrichmentComplete] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);

  useEffect(() => {
    // Simulate enrichment process
    let stepIndex = 0;
    const timers: NodeJS.Timeout[] = [];

    const progressToNextStep = () => {
      if (stepIndex < ENRICHMENT_STEPS.length) {
        setCurrentStep(stepIndex);

        if (stepIndex === ENRICHMENT_STEPS.length - 1) {
          // Last step - show completion
          const timer = setTimeout(() => {
            setIsEnrichmentComplete(true);
            setShowConfetti(true);
            setTimeout(() => setShowConfetti(false), 3000);
          }, ENRICHMENT_STEPS[stepIndex].duration);
          timers.push(timer);
        } else {
          // Continue to next step
          const timer = setTimeout(() => {
            stepIndex++;
            progressToNextStep();
          }, ENRICHMENT_STEPS[stepIndex].duration);
          timers.push(timer);
        }
      }
    };

    progressToNextStep();

    return () => {
      timers.forEach((timer) => clearTimeout(timer));
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 flex items-center justify-center p-6">
      {/* Confetti effect */}
      <AnimatePresence>
        {showConfetti && (
          <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
            {Array.from({ length: 50 }).map((_, i) => (
              <motion.div
                key={i}
                initial={{ y: -20, x: Math.random() * window.innerWidth, opacity: 1 }}
                animate={{ y: window.innerHeight + 20, rotate: 360 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 2 + Math.random() * 2, delay: Math.random() * 0.5 }}
                className={cn(
                  'absolute w-3 h-3 rounded-full',
                  ['bg-green-500', 'bg-emerald-500', 'bg-teal-500', 'bg-blue-500', 'bg-purple-500'][
                    i % 5
                  ]
                )}
              />
            ))}
          </div>
        )}
      </AnimatePresence>

      <div className="max-w-4xl w-full">
        {/* Main success card */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="bg-white/90 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 overflow-hidden"
        >
          {/* Header */}
          <div className="px-8 py-6 bg-gradient-to-r from-green-500 to-emerald-600 text-white">
            <motion.div
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="flex items-center gap-3"
            >
              <CheckCircle className="w-12 h-12" />
              <div>
                <h1 className="text-3xl font-bold">Welcome to the Community!</h1>
                <p className="text-green-100 mt-1">Your subscription is active</p>
              </div>
            </motion.div>
          </div>

          {/* Enrichment process */}
          <div className="px-8 py-10">
            {!isEnrichmentComplete ? (
              <div className="space-y-6">
                <div className="text-center mb-8">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">
                    Setting Up Your Profile
                  </h2>
                  <p className="text-gray-600">
                    We're enriching your profile with AI-powered data analysis
                  </p>
                </div>

                {/* Progress steps */}
                <div className="space-y-4">
                  {ENRICHMENT_STEPS.map((step, index) => {
                    const isActive = index === currentStep;
                    const isComplete = index < currentStep;
                    const Icon = step.icon;

                    return (
                      <motion.div
                        key={step.id}
                        initial={{ x: -20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: index * 0.1 }}
                        className={cn(
                          'flex items-start gap-4 p-4 rounded-xl border-2 transition-all',
                          isActive && 'bg-green-50 border-green-500 shadow-md',
                          isComplete && 'bg-gray-50 border-gray-300',
                          !isActive && !isComplete && 'bg-white border-gray-200'
                        )}
                      >
                        <div
                          className={cn(
                            'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center',
                            isActive && 'bg-green-500 text-white',
                            isComplete && 'bg-green-500 text-white',
                            !isActive && !isComplete && 'bg-gray-200 text-gray-400'
                          )}
                        >
                          {isActive ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                          ) : (
                            <Icon className="w-5 h-5" />
                          )}
                        </div>

                        <div className="flex-1">
                          <h3
                            className={cn(
                              'font-semibold',
                              isActive ? 'text-green-900' : 'text-gray-900'
                            )}
                          >
                            {step.label}
                          </h3>
                          <p
                            className={cn(
                              'text-sm mt-0.5',
                              isActive ? 'text-green-700' : 'text-gray-600'
                            )}
                          >
                            {step.description}
                          </p>
                        </div>

                        {isComplete && (
                          <CheckCircle className="flex-shrink-0 w-6 h-6 text-green-500" />
                        )}
                      </motion.div>
                    );
                  })}
                </div>

                {/* Estimated time */}
                <div className="text-center mt-6">
                  <p className="text-sm text-gray-500">
                    Estimated time: 30-60 seconds
                  </p>
                </div>
              </div>
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                {/* Success message */}
                <div className="text-center mb-10">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', duration: 0.6 }}
                    className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full mb-4 shadow-lg"
                  >
                    <CheckCircle className="w-12 h-12 text-white" />
                  </motion.div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    Your Profile is Ready!
                  </h2>
                  <p className="text-gray-600">
                    You're all set to start contributing to the peer review community
                  </p>
                </div>

                {/* Next steps */}
                <div className="space-y-4 mb-8">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    What's Next?
                  </h3>

                  {NEXT_STEPS.map((step, index) => {
                    const Icon = step.icon;
                    const colorClasses = {
                      blue: 'bg-blue-50 border-blue-200 text-blue-600',
                      purple: 'bg-purple-50 border-purple-200 text-purple-600',
                      green: 'bg-green-50 border-green-200 text-green-600',
                    }[step.color];

                    return (
                      <motion.div
                        key={step.title}
                        initial={{ x: -20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: 0.2 + index * 0.1 }}
                        className="group flex items-center gap-4 p-4 bg-white border-2 border-gray-200 rounded-xl hover:border-green-300 hover:shadow-md transition-all cursor-pointer"
                        onClick={() => router.push(step.href)}
                      >
                        <div className={cn('p-3 rounded-lg border', colorClasses)}>
                          <Icon className="w-6 h-6" />
                        </div>

                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">
                            {step.title}
                          </h4>
                          <p className="text-sm text-gray-600 mt-0.5">{step.description}</p>
                        </div>

                        <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" />
                      </motion.div>
                    );
                  })}
                </div>

                {/* CTA buttons */}
                <div className="flex gap-4">
                  <Button
                    variant="primary"
                    size="lg"
                    fullWidth
                    onClick={() => router.push('/dashboard')}
                    className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
                    icon={<TrendingUp className="w-5 h-5" />}
                  >
                    Go to Dashboard
                  </Button>
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Additional info */}
        {isEnrichmentComplete && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="mt-6 text-center"
          >
            <p className="text-sm text-gray-600">
              Need help getting started?{' '}
              <a
                href="mailto:support@metaanalysis.ai"
                className="text-green-600 hover:text-green-700 font-medium underline"
              >
                Contact our support team
              </a>
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
