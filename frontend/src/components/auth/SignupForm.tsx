'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Eye, EyeOff, Mail, Lock, User, Building, Chrome,
  AlertCircle, CheckCircle2, ArrowRight, ArrowLeft, Crown, Check
} from 'lucide-react';
import { Button } from '../shared/Button';
import { cn } from '../../lib/utils';
import Link from 'next/link';

interface SignupFormProps {
  onSubmit?: (data: SignupFormData) => Promise<void>;
  onGoogleSignup?: () => void;
}

interface SignupFormData {
  accountType: 'researcher' | 'admin';
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
  institution: string;
  agreeToTerms: boolean;
}

type Step = 1 | 2 | 3;

export const SignupForm: React.FC<SignupFormProps> = ({ onSubmit, onGoogleSignup }) => {
  const [currentStep, setCurrentStep] = useState<Step>(1);
  const [formData, setFormData] = useState<SignupFormData>({
    accountType: 'researcher',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    institution: '',
    agreeToTerms: false
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Password strength calculation
  const getPasswordStrength = (password: string): { score: number; label: string; color: string } => {
    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;

    if (score <= 2) return { score: score * 20, label: 'Weak', color: 'bg-red-500' };
    if (score <= 3) return { score: score * 20, label: 'Fair', color: 'bg-yellow-500' };
    if (score <= 4) return { score: score * 20, label: 'Good', color: 'bg-blue-500' };
    return { score: 100, label: 'Excellent', color: 'bg-green-500' };
  };

  const passwordStrength = getPasswordStrength(formData.password);

  // Validation
  const validateStep = (step: Step): boolean => {
    const errors: Record<string, string> = {};

    if (step === 1) {
      // Account type is always valid as it has a default
    }

    if (step === 2) {
      if (!formData.email) {
        errors.email = 'Email is required';
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        errors.email = 'Invalid email format';
      }

      if (!formData.password) {
        errors.password = 'Password is required';
      } else if (formData.password.length < 8) {
        errors.password = 'Password must be at least 8 characters';
      }

      if (formData.password !== formData.confirmPassword) {
        errors.confirmPassword = 'Passwords do not match';
      }
    }

    if (step === 3) {
      if (!formData.fullName) {
        errors.fullName = 'Full name is required';
      }
      if (!formData.institution) {
        errors.institution = 'Institution is required';
      }
      if (!formData.agreeToTerms) {
        errors.agreeToTerms = 'You must agree to the terms';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(3, prev + 1) as Step);
      setError(null);
    }
  };

  const handleBack = () => {
    setCurrentStep((prev) => Math.max(1, prev - 1) as Step);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateStep(3)) return;

    setError(null);
    setIsLoading(true);

    try {
      if (onSubmit) {
        await onSubmit(formData);
        setSuccess(true);

        setTimeout(() => {
          window.location.href = '/onboarding';
        }, 1500);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Success screen
  if (success) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-2xl shadow-hard p-8 text-center"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <CheckCircle2 className="w-10 h-10 text-green-600" />
        </motion.div>
        <motion.h3
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-2xl font-bold text-gray-900 mb-2"
        >
          Welcome to the platform!
        </motion.h3>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-gray-600"
        >
          Let's get you set up...
        </motion.p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white rounded-2xl shadow-hard p-8"
    >
      {/* Progress indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          {[1, 2, 3].map((step) => (
            <React.Fragment key={step}>
              <motion.div
                className="flex flex-col items-center"
                initial={false}
                animate={{
                  scale: currentStep === step ? 1.1 : 1,
                }}
              >
                <motion.div
                  className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all duration-300",
                    currentStep > step
                      ? formData.accountType === 'admin'
                        ? "bg-accent-600 text-white"
                        : "bg-primary-600 text-white"
                      : currentStep === step
                        ? formData.accountType === 'admin'
                          ? "bg-accent-600 text-white shadow-glow-accent"
                          : "bg-primary-600 text-white shadow-glow-primary"
                        : "bg-gray-200 text-gray-400"
                  )}
                >
                  {currentStep > step ? <Check className="w-5 h-5" /> : step}
                </motion.div>
                <div className={cn(
                  "text-xs mt-2 font-medium transition-colors duration-300",
                  currentStep >= step ? "text-gray-900" : "text-gray-400"
                )}>
                  {step === 1 ? 'Type' : step === 2 ? 'Credentials' : 'Profile'}
                </div>
              </motion.div>
              {step < 3 && (
                <div className="flex-1 h-0.5 mx-4 bg-gray-200 relative overflow-hidden">
                  <motion.div
                    className={cn(
                      "absolute inset-y-0 left-0",
                      formData.accountType === 'admin' ? "bg-accent-600" : "bg-primary-600"
                    )}
                    initial={{ width: "0%" }}
                    animate={{ width: currentStep > step ? "100%" : "0%" }}
                    transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                  />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Error message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10, height: 0 }}
            animate={{ opacity: 1, y: 0, height: "auto" }}
            exit={{ opacity: 0, y: -10, height: 0 }}
            className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3 mb-6"
          >
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-red-900 text-sm">Error</div>
              <div className="text-red-700 text-sm">{error}</div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <form onSubmit={handleSubmit}>
        <AnimatePresence mode="wait">
          {/* Step 1: Account Type */}
          {currentStep === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
              className="space-y-4"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Choose your account type</h3>

              <motion.button
                type="button"
                onClick={() => setFormData({ ...formData, accountType: 'researcher' })}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={cn(
                  "w-full p-6 rounded-xl border-2 transition-all duration-300 text-left",
                  formData.accountType === 'researcher'
                    ? "border-primary-600 bg-primary-50 shadow-glow-primary"
                    : "border-gray-200 hover:border-gray-300"
                )}
              >
                <div className="flex items-start gap-4">
                  <div className={cn(
                    "w-12 h-12 rounded-xl flex items-center justify-center transition-colors duration-300",
                    formData.accountType === 'researcher' ? "bg-primary-600" : "bg-gray-100"
                  )}>
                    <User className={cn(
                      "w-6 h-6 transition-colors duration-300",
                      formData.accountType === 'researcher' ? "text-white" : "text-gray-400"
                    )} />
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900 mb-1">Researcher Account</div>
                    <div className="text-sm text-gray-600">
                      Conduct meta-analyses, access AI agents, and collaborate with your team
                    </div>
                  </div>
                  {formData.accountType === 'researcher' && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center"
                    >
                      <Check className="w-4 h-4 text-white" />
                    </motion.div>
                  )}
                </div>
              </motion.button>

              <motion.button
                type="button"
                onClick={() => setFormData({ ...formData, accountType: 'admin' })}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={cn(
                  "w-full p-6 rounded-xl border-2 transition-all duration-300 text-left",
                  formData.accountType === 'admin'
                    ? "border-accent-600 bg-accent-50 shadow-glow-accent"
                    : "border-gray-200 hover:border-gray-300"
                )}
              >
                <div className="flex items-start gap-4">
                  <div className={cn(
                    "w-12 h-12 rounded-xl flex items-center justify-center transition-colors duration-300",
                    formData.accountType === 'admin' ? "bg-accent-600" : "bg-gray-100"
                  )}>
                    <Crown className={cn(
                      "w-6 h-6 transition-colors duration-300",
                      formData.accountType === 'admin' ? "text-white" : "text-gray-400"
                    )} />
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900 mb-1">Admin Account</div>
                    <div className="text-sm text-gray-600">
                      Manage reviewers, approve papers, handle payouts, and oversee the platform
                    </div>
                  </div>
                  {formData.accountType === 'admin' && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-6 h-6 bg-accent-600 rounded-full flex items-center justify-center"
                    >
                      <Check className="w-4 h-4 text-white" />
                    </motion.div>
                  )}
                </div>
              </motion.button>

              <motion.div className="pt-4" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button
                  type="button"
                  onClick={handleNext}
                  fullWidth
                  size="lg"
                  className={cn(
                    formData.accountType === 'admin'
                      ? "bg-accent-600 hover:bg-accent-700 focus-visible:ring-accent-500"
                      : ""
                  )}
                  icon={<ArrowRight className="w-5 h-5" />}
                >
                  Continue
                </Button>
              </motion.div>
            </motion.div>
          )}

          {/* Step 2: Credentials */}
          {currentStep === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
              className="space-y-5"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Create your credentials</h3>

              {/* Email */}
              <div>
                <div className={cn(
                  "relative rounded-xl border-2 transition-all duration-300",
                  validationErrors.email
                    ? "border-red-300"
                    : focusedField === 'email'
                      ? formData.accountType === 'admin'
                        ? "border-accent-600 shadow-glow-accent"
                        : "border-primary-600 shadow-glow-primary"
                      : "border-gray-200 hover:border-gray-300"
                )}>
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                    <Mail className="w-5 h-5" />
                  </div>
                  <input
                    type="email"
                    id="email"
                    value={formData.email}
                    onChange={(e) => {
                      setFormData({ ...formData, email: e.target.value });
                      setValidationErrors({ ...validationErrors, email: '' });
                    }}
                    onFocus={() => setFocusedField('email')}
                    onBlur={() => setFocusedField(null)}
                    className="w-full px-12 py-4 bg-transparent outline-none text-gray-900"
                    placeholder="Email address"
                  />
                </div>
                {validationErrors.email && (
                  <motion.p
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-red-600 text-xs mt-1.5 ml-1"
                  >
                    {validationErrors.email}
                  </motion.p>
                )}
              </div>

              {/* Password */}
              <div>
                <div className={cn(
                  "relative rounded-xl border-2 transition-all duration-300",
                  validationErrors.password
                    ? "border-red-300"
                    : focusedField === 'password'
                      ? formData.accountType === 'admin'
                        ? "border-accent-600 shadow-glow-accent"
                        : "border-primary-600 shadow-glow-primary"
                      : "border-gray-200 hover:border-gray-300"
                )}>
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                    <Lock className="w-5 h-5" />
                  </div>
                  <input
                    type={showPassword ? "text" : "password"}
                    id="password"
                    value={formData.password}
                    onChange={(e) => {
                      setFormData({ ...formData, password: e.target.value });
                      setValidationErrors({ ...validationErrors, password: '' });
                    }}
                    onFocus={() => setFocusedField('password')}
                    onBlur={() => setFocusedField(null)}
                    className="w-full px-12 py-4 bg-transparent outline-none text-gray-900"
                    placeholder="Password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>

                {/* Password strength indicator */}
                {formData.password && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="mt-2 space-y-1"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-600">Password strength</span>
                      <span className={cn(
                        "font-semibold",
                        passwordStrength.score <= 40 ? "text-red-600" :
                        passwordStrength.score <= 60 ? "text-yellow-600" :
                        passwordStrength.score <= 80 ? "text-blue-600" :
                        "text-green-600"
                      )}>
                        {passwordStrength.label}
                      </span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <motion.div
                        className={cn("h-full rounded-full", passwordStrength.color)}
                        initial={{ width: 0 }}
                        animate={{ width: `${passwordStrength.score}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  </motion.div>
                )}

                {validationErrors.password && (
                  <motion.p
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-red-600 text-xs mt-1.5 ml-1"
                  >
                    {validationErrors.password}
                  </motion.p>
                )}
              </div>

              {/* Confirm Password */}
              <div>
                <div className={cn(
                  "relative rounded-xl border-2 transition-all duration-300",
                  validationErrors.confirmPassword
                    ? "border-red-300"
                    : focusedField === 'confirmPassword'
                      ? formData.accountType === 'admin'
                        ? "border-accent-600 shadow-glow-accent"
                        : "border-primary-600 shadow-glow-primary"
                      : "border-gray-200 hover:border-gray-300"
                )}>
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                    <Lock className="w-5 h-5" />
                  </div>
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    id="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={(e) => {
                      setFormData({ ...formData, confirmPassword: e.target.value });
                      setValidationErrors({ ...validationErrors, confirmPassword: '' });
                    }}
                    onFocus={() => setFocusedField('confirmPassword')}
                    onBlur={() => setFocusedField(null)}
                    className="w-full px-12 py-4 bg-transparent outline-none text-gray-900"
                    placeholder="Confirm password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {validationErrors.confirmPassword && (
                  <motion.p
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-red-600 text-xs mt-1.5 ml-1"
                  >
                    {validationErrors.confirmPassword}
                  </motion.p>
                )}
              </div>

              <div className="flex gap-3 pt-2">
                <motion.div className="flex-1" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                  <Button
                    type="button"
                    onClick={handleBack}
                    variant="outline"
                    fullWidth
                    size="lg"
                    icon={<ArrowLeft className="w-5 h-5" />}
                  >
                    Back
                  </Button>
                </motion.div>
                <motion.div className="flex-1" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                  <Button
                    type="button"
                    onClick={handleNext}
                    fullWidth
                    size="lg"
                    className={cn(
                      formData.accountType === 'admin'
                        ? "bg-accent-600 hover:bg-accent-700 focus-visible:ring-accent-500"
                        : ""
                    )}
                    icon={<ArrowRight className="w-5 h-5" />}
                  >
                    Continue
                  </Button>
                </motion.div>
              </div>
            </motion.div>
          )}

          {/* Step 3: Profile */}
          {currentStep === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
              className="space-y-5"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Complete your profile</h3>

              {/* Full Name */}
              <div>
                <div className={cn(
                  "relative rounded-xl border-2 transition-all duration-300",
                  validationErrors.fullName
                    ? "border-red-300"
                    : focusedField === 'fullName'
                      ? formData.accountType === 'admin'
                        ? "border-accent-600 shadow-glow-accent"
                        : "border-primary-600 shadow-glow-primary"
                      : "border-gray-200 hover:border-gray-300"
                )}>
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                    <User className="w-5 h-5" />
                  </div>
                  <input
                    type="text"
                    id="fullName"
                    value={formData.fullName}
                    onChange={(e) => {
                      setFormData({ ...formData, fullName: e.target.value });
                      setValidationErrors({ ...validationErrors, fullName: '' });
                    }}
                    onFocus={() => setFocusedField('fullName')}
                    onBlur={() => setFocusedField(null)}
                    className="w-full px-12 py-4 bg-transparent outline-none text-gray-900"
                    placeholder="Full name"
                  />
                </div>
                {validationErrors.fullName && (
                  <motion.p
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-red-600 text-xs mt-1.5 ml-1"
                  >
                    {validationErrors.fullName}
                  </motion.p>
                )}
              </div>

              {/* Institution */}
              <div>
                <div className={cn(
                  "relative rounded-xl border-2 transition-all duration-300",
                  validationErrors.institution
                    ? "border-red-300"
                    : focusedField === 'institution'
                      ? formData.accountType === 'admin'
                        ? "border-accent-600 shadow-glow-accent"
                        : "border-primary-600 shadow-glow-primary"
                      : "border-gray-200 hover:border-gray-300"
                )}>
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                    <Building className="w-5 h-5" />
                  </div>
                  <input
                    type="text"
                    id="institution"
                    value={formData.institution}
                    onChange={(e) => {
                      setFormData({ ...formData, institution: e.target.value });
                      setValidationErrors({ ...validationErrors, institution: '' });
                    }}
                    onFocus={() => setFocusedField('institution')}
                    onBlur={() => setFocusedField(null)}
                    className="w-full px-12 py-4 bg-transparent outline-none text-gray-900"
                    placeholder="Institution or Organization"
                  />
                </div>
                {validationErrors.institution && (
                  <motion.p
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-red-600 text-xs mt-1.5 ml-1"
                  >
                    {validationErrors.institution}
                  </motion.p>
                )}
              </div>

              {/* Terms agreement */}
              <div>
                <label className={cn(
                  "flex items-start gap-3 cursor-pointer group p-4 rounded-xl border-2 transition-all duration-300",
                  validationErrors.agreeToTerms
                    ? "border-red-300 bg-red-50"
                    : formData.agreeToTerms
                      ? formData.accountType === 'admin'
                        ? "border-accent-200 bg-accent-50"
                        : "border-primary-200 bg-primary-50"
                      : "border-gray-200 hover:border-gray-300"
                )}>
                  <div className="relative flex-shrink-0 mt-0.5">
                    <input
                      type="checkbox"
                      checked={formData.agreeToTerms}
                      onChange={(e) => {
                        setFormData({ ...formData, agreeToTerms: e.target.checked });
                        setValidationErrors({ ...validationErrors, agreeToTerms: '' });
                      }}
                      className="sr-only peer"
                    />
                    <div className={cn(
                      "w-5 h-5 border-2 rounded transition-all duration-200",
                      formData.agreeToTerms
                        ? formData.accountType === 'admin'
                          ? "bg-accent-600 border-accent-600"
                          : "bg-primary-600 border-primary-600"
                        : "border-gray-300 group-hover:border-gray-400"
                    )}>
                      {formData.agreeToTerms && (
                        <motion.svg
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="w-full h-full text-white"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </motion.svg>
                      )}
                    </div>
                  </div>
                  <span className="text-sm text-gray-700 leading-relaxed">
                    I agree to the{' '}
                    <a href="/terms" className={cn(
                      "font-semibold transition-colors",
                      formData.accountType === 'admin'
                        ? "text-accent-600 hover:text-accent-700"
                        : "text-primary-600 hover:text-primary-700"
                    )}>
                      Terms of Service
                    </a>{' '}
                    and{' '}
                    <a href="/privacy" className={cn(
                      "font-semibold transition-colors",
                      formData.accountType === 'admin'
                        ? "text-accent-600 hover:text-accent-700"
                        : "text-primary-600 hover:text-primary-700"
                    )}>
                      Privacy Policy
                    </a>
                  </span>
                </label>
                {validationErrors.agreeToTerms && (
                  <motion.p
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-red-600 text-xs mt-1.5 ml-1"
                  >
                    {validationErrors.agreeToTerms}
                  </motion.p>
                )}
              </div>

              <div className="flex gap-3 pt-2">
                <motion.div className="flex-1" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                  <Button
                    type="button"
                    onClick={handleBack}
                    variant="outline"
                    fullWidth
                    size="lg"
                    icon={<ArrowLeft className="w-5 h-5" />}
                  >
                    Back
                  </Button>
                </motion.div>
                <motion.div className="flex-1" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                  <Button
                    type="submit"
                    loading={isLoading}
                    fullWidth
                    size="lg"
                    className={cn(
                      "shadow-lg",
                      formData.accountType === 'admin'
                        ? "bg-accent-600 hover:bg-accent-700 focus-visible:ring-accent-500"
                        : ""
                    )}
                  >
                    {isLoading ? 'Creating account...' : 'Create account'}
                  </Button>
                </motion.div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Divider - only show on step 1 */}
        {currentStep === 1 && (
          <>
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">Or sign up with</span>
              </div>
            </div>

            {/* Social signup */}
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <button
                type="button"
                onClick={onGoogleSignup}
                className="w-full px-6 py-4 border-2 border-gray-200 rounded-xl font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 flex items-center justify-center gap-3 group"
              >
                <Chrome className="w-5 h-5 text-gray-500 group-hover:text-gray-700 transition-colors" />
                Google Scholar
              </button>
            </motion.div>
          </>
        )}

        {/* Sign in link */}
        <div className="text-center text-sm text-gray-600 mt-6">
          Already have an account?{' '}
          <Link
            href="/login"
            className={cn(
              "font-semibold transition-colors",
              formData.accountType === 'admin'
                ? "text-accent-600 hover:text-accent-700"
                : "text-primary-600 hover:text-primary-700"
            )}
          >
            Sign in
          </Link>
        </div>
      </form>
    </motion.div>
  );
};

export default SignupForm;
