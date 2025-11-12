'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, EyeOff, Mail, Lock, Chrome, AlertCircle, CheckCircle2, Crown } from 'lucide-react';
import { Button } from '../shared/Button';
import { cn } from '../../lib/utils';
import Link from 'next/link';

interface LoginFormProps {
  onSubmit?: (data: LoginFormData) => Promise<void>;
  onGoogleLogin?: () => void;
}

interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
  isMasterAdmin: boolean;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSubmit, onGoogleLogin }) => {
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
    rememberMe: false,
    isMasterAdmin: false
  });

  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      if (onSubmit) {
        await onSubmit(formData);
        setSuccess(true);

        // Simulate redirect after success animation
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1500);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Invalid credentials. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    if (onGoogleLogin) {
      onGoogleLogin();
    }
  };

  // Success overlay
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
          Welcome back!
        </motion.h3>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-gray-600"
        >
          Redirecting to your dashboard...
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
      {/* Master Admin Toggle */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mb-6"
      >
        <button
          type="button"
          onClick={() => setFormData({ ...formData, isMasterAdmin: !formData.isMasterAdmin })}
          className={cn(
            "w-full p-4 rounded-xl border-2 transition-all duration-300 flex items-center justify-between group",
            formData.isMasterAdmin
              ? "border-accent-600 bg-accent-50"
              : "border-gray-200 hover:border-gray-300 bg-white"
          )}
        >
          <div className="flex items-center gap-3">
            <div className={cn(
              "w-10 h-10 rounded-lg flex items-center justify-center transition-colors duration-300",
              formData.isMasterAdmin ? "bg-accent-600" : "bg-gray-100 group-hover:bg-gray-200"
            )}>
              <Crown className={cn(
                "w-5 h-5 transition-colors duration-300",
                formData.isMasterAdmin ? "text-white" : "text-gray-400"
              )} />
            </div>
            <div className="text-left">
              <div className={cn(
                "font-semibold transition-colors duration-300",
                formData.isMasterAdmin ? "text-accent-900" : "text-gray-700"
              )}>
                Master Admin Access
              </div>
              <div className={cn(
                "text-sm transition-colors duration-300",
                formData.isMasterAdmin ? "text-accent-700" : "text-gray-500"
              )}>
                {formData.isMasterAdmin ? "Enabled" : "Researcher account"}
              </div>
            </div>
          </div>
          <motion.div
            animate={{ rotate: formData.isMasterAdmin ? 180 : 0 }}
            transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className={cn(
              "w-12 h-6 rounded-full relative transition-colors duration-300",
              formData.isMasterAdmin ? "bg-accent-600" : "bg-gray-200"
            )}>
              <motion.div
                className="absolute top-0.5 w-5 h-5 bg-white rounded-full shadow-sm"
                animate={{ left: formData.isMasterAdmin ? 26 : 2 }}
                transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
              />
            </div>
          </motion.div>
        </button>
      </motion.div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Error message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10, height: 0 }}
              animate={{ opacity: 1, y: 0, height: "auto" }}
              exit={{ opacity: 0, y: -10, height: 0 }}
              className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <div className="font-semibold text-red-900 text-sm">Login failed</div>
                <div className="text-red-700 text-sm">{error}</div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Email field */}
        <div className="relative">
          <motion.div
            animate={{
              scale: focusedField === 'email' ? 1.02 : 1,
            }}
            transition={{ duration: 0.2 }}
          >
            <div className={cn(
              "relative rounded-xl border-2 transition-all duration-300",
              focusedField === 'email'
                ? formData.isMasterAdmin
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
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                onFocus={() => setFocusedField('email')}
                onBlur={() => setFocusedField(null)}
                className="w-full px-12 py-4 bg-transparent outline-none text-gray-900 placeholder-transparent peer"
                placeholder="Email address"
                required
              />
              <motion.label
                htmlFor="email"
                className={cn(
                  "absolute left-12 transition-all duration-200 pointer-events-none",
                  formData.email || focusedField === 'email'
                    ? "top-2 text-xs font-medium"
                    : "top-1/2 -translate-y-1/2 text-base",
                  focusedField === 'email'
                    ? formData.isMasterAdmin
                      ? "text-accent-600"
                      : "text-primary-600"
                    : "text-gray-500"
                )}
              >
                Email address
              </motion.label>
            </div>
          </motion.div>
        </div>

        {/* Password field */}
        <div className="relative">
          <motion.div
            animate={{
              scale: focusedField === 'password' ? 1.02 : 1,
            }}
            transition={{ duration: 0.2 }}
          >
            <div className={cn(
              "relative rounded-xl border-2 transition-all duration-300",
              focusedField === 'password'
                ? formData.isMasterAdmin
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
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                onFocus={() => setFocusedField('password')}
                onBlur={() => setFocusedField(null)}
                className="w-full px-12 py-4 bg-transparent outline-none text-gray-900 placeholder-transparent peer"
                placeholder="Password"
                required
              />
              <motion.label
                htmlFor="password"
                className={cn(
                  "absolute left-12 transition-all duration-200 pointer-events-none",
                  formData.password || focusedField === 'password'
                    ? "top-2 text-xs font-medium"
                    : "top-1/2 -translate-y-1/2 text-base",
                  focusedField === 'password'
                    ? formData.isMasterAdmin
                      ? "text-accent-600"
                      : "text-primary-600"
                    : "text-gray-500"
                )}
              >
                Password
              </motion.label>
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </motion.div>
        </div>

        {/* Remember me & Forgot password */}
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 cursor-pointer group">
            <div className="relative">
              <input
                type="checkbox"
                checked={formData.rememberMe}
                onChange={(e) => setFormData({ ...formData, rememberMe: e.target.checked })}
                className="sr-only peer"
              />
              <div className={cn(
                "w-5 h-5 border-2 rounded transition-all duration-200",
                formData.rememberMe
                  ? formData.isMasterAdmin
                    ? "bg-accent-600 border-accent-600"
                    : "bg-primary-600 border-primary-600"
                  : "border-gray-300 group-hover:border-gray-400"
              )}>
                {formData.rememberMe && (
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
            <span className="text-sm text-gray-700 group-hover:text-gray-900 transition-colors">
              Remember me
            </span>
          </label>

          <Link
            href="/forgot-password"
            className={cn(
              "text-sm font-medium transition-colors",
              formData.isMasterAdmin
                ? "text-accent-600 hover:text-accent-700"
                : "text-primary-600 hover:text-primary-700"
            )}
          >
            Forgot password?
          </Link>
        </div>

        {/* Submit button */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Button
            type="submit"
            loading={isLoading}
            fullWidth
            size="lg"
            className={cn(
              "shadow-lg transition-all duration-300",
              formData.isMasterAdmin
                ? "bg-accent-600 hover:bg-accent-700 focus-visible:ring-accent-500"
                : ""
            )}
          >
            {isLoading ? 'Signing in...' : formData.isMasterAdmin ? 'Sign in as Admin' : 'Sign in'}
          </Button>
        </motion.div>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-200" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-4 bg-white text-gray-500">Or continue with</span>
          </div>
        </div>

        {/* Social login */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <button
            type="button"
            onClick={handleGoogleLogin}
            className="w-full px-6 py-4 border-2 border-gray-200 rounded-xl font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 flex items-center justify-center gap-3 group"
          >
            <Chrome className="w-5 h-5 text-gray-500 group-hover:text-gray-700 transition-colors" />
            Google Scholar
          </button>
        </motion.div>

        {/* Sign up link */}
        <div className="text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <Link
            href="/signup"
            className={cn(
              "font-semibold transition-colors",
              formData.isMasterAdmin
                ? "text-accent-600 hover:text-accent-700"
                : "text-primary-600 hover:text-primary-700"
            )}
          >
            Sign up for free
          </Link>
        </div>
      </form>
    </motion.div>
  );
};

export default LoginForm;
