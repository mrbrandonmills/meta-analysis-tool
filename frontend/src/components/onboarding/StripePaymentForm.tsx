/**
 * Stripe Payment Form Component
 *
 * SETUP REQUIRED:
 * 1. Install Stripe dependencies:
 *    npm install @stripe/stripe-js @stripe/react-stripe-js
 *
 * 2. Add Stripe publishable key to environment variables:
 *    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
 *
 * 3. Wrap this component with Stripe Elements provider in parent component
 */

import React, { useState } from 'react';
import { CreditCard, Lock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/shared/Button';

interface StripePaymentFormProps {
  onSuccess: (paymentMethodId: string) => void;
  onError: (error: string) => void;
  billingEmail: string;
  loading?: boolean;
  className?: string;
}

export const StripePaymentForm: React.FC<StripePaymentFormProps> = ({
  onSuccess,
  onError,
  billingEmail,
  loading = false,
  className,
}) => {
  const [cardholderName, setCardholderName] = useState('');
  const [processing, setProcessing] = useState(false);

  // Note: This is a placeholder implementation
  // In production, you would use @stripe/react-stripe-js components:
  // - CardElement from '@stripe/react-stripe-js'
  // - useStripe and useElements hooks

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!cardholderName.trim()) {
      onError('Cardholder name is required');
      return;
    }

    setProcessing(true);

    try {
      // In production, you would:
      // 1. Use stripe.createPaymentMethod() with card element
      // 2. Send payment method ID to backend
      // 3. Backend creates subscription with Stripe

      // Placeholder success
      setTimeout(() => {
        onSuccess('pm_placeholder_' + Date.now());
        setProcessing(false);
      }, 1500);

    } catch (err) {
      onError(err instanceof Error ? err.message : 'Payment failed');
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={cn('space-y-6', className)}>
      {/* Security badge */}
      <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
        <Lock className="w-5 h-5 text-green-600" aria-hidden="true" />
        <p className="text-sm text-green-800">
          Your payment information is secure and encrypted
        </p>
      </div>

      {/* Billing email (read-only) */}
      <div>
        <label htmlFor="billing-email" className="block text-sm font-medium text-gray-700 mb-2">
          Billing Email
        </label>
        <input
          id="billing-email"
          type="email"
          value={billingEmail}
          readOnly
          className="w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg text-gray-600"
        />
      </div>

      {/* Cardholder name */}
      <div>
        <label htmlFor="cardholder-name" className="block text-sm font-medium text-gray-700 mb-2">
          Cardholder Name
          <span className="text-red-500 ml-1">*</span>
        </label>
        <input
          id="cardholder-name"
          type="text"
          value={cardholderName}
          onChange={(e) => setCardholderName(e.target.value)}
          placeholder="John Doe"
          required
          className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
        />
      </div>

      {/* Card element placeholder */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Card Information
          <span className="text-red-500 ml-1">*</span>
        </label>

        {/* This would be replaced with <CardElement /> from Stripe */}
        <div className="p-4 border-2 border-gray-300 rounded-lg bg-white">
          <div className="flex items-center gap-3 text-gray-400">
            <CreditCard className="w-5 h-5" aria-hidden="true" />
            <span className="text-sm">Stripe payment form would appear here</span>
          </div>
          <p className="text-xs text-gray-500 mt-2 italic">
            Install @stripe/react-stripe-js to enable payment processing
          </p>
        </div>
      </div>

      {/* Subscription details */}
      <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Monthly Subscription</span>
          <span className="font-semibold text-gray-900">$100.00</span>
        </div>
        <div className="border-t border-gray-300 pt-2 space-y-1 text-xs text-gray-600">
          <div className="flex justify-between">
            <span>Platform Access</span>
            <span>$80.00</span>
          </div>
          <div className="flex justify-between">
            <span>Review Pool Contribution</span>
            <span>$20.00</span>
          </div>
        </div>
        <div className="border-t border-gray-300 pt-2 flex justify-between font-semibold">
          <span>Total Today</span>
          <span>$100.00</span>
        </div>
        <p className="text-xs text-gray-500 pt-2 border-t border-gray-200">
          You will be charged $100 monthly. Cancel anytime from your account settings.
        </p>
      </div>

      {/* Submit button */}
      <Button
        type="submit"
        variant="primary"
        size="lg"
        fullWidth
        loading={processing || loading}
        className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
      >
        {processing ? 'Processing Payment...' : 'Subscribe & Complete Onboarding'}
      </Button>

      {/* Terms reminder */}
      <p className="text-xs text-gray-500 text-center">
        By subscribing, you agree to our Terms of Service and Privacy Policy
      </p>
    </form>
  );
};

// Stripe Elements Wrapper (to be used in parent component)
export const StripePaymentFormWrapper: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  // In production, you would:
  // 1. Load Stripe with loadStripe(publishableKey)
  // 2. Wrap children with <Elements stripe={stripePromise}>

  return (
    <div>
      {children}
      {/* <Elements stripe={stripePromise}>{children}</Elements> */}
    </div>
  );
};

export default StripePaymentForm;
