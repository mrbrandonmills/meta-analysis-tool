/**
 * Authentication Components
 *
 * Museum-quality authentication system for the Meta-Analysis Research Platform.
 * Export all auth-related components for easy importing.
 */

export { AuthLayout } from './AuthLayout';
export { LoginForm } from './LoginForm';
export { SignupForm } from './SignupForm';

// Re-export types for convenience
export type { default as LoginFormProps } from './LoginForm';
export type { default as SignupFormProps } from './SignupForm';
