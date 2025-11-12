import React from 'react';
import Head from 'next/head';
import { AuthLayout } from '../components/auth/AuthLayout';
import { SignupForm } from '../components/auth/SignupForm';

export default function SignupPage() {
  const handleSignup = async (data: any) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));

    // In production, this would call your auth API
    console.log('Signup data:', data);

    // For demo, throw error if email already exists
    if (data.email === 'exists@test.com') {
      throw new Error('An account with this email already exists');
    }
  };

  const handleGoogleSignup = () => {
    // In production, this would initiate OAuth flow
    console.log('Google signup initiated');
    window.location.href = '/api/auth/google?signup=true';
  };

  return (
    <>
      <Head>
        <title>Create Account | Meta-Analysis Research Platform</title>
        <meta name="description" content="Create your account to access AI-powered meta-analysis tools, systematic reviews, and research synthesis." />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
      </Head>

      <AuthLayout
        title="Get started"
        subtitle="Create your account in minutes"
        side="left"
      >
        <SignupForm onSubmit={handleSignup} onGoogleSignup={handleGoogleSignup} />
      </AuthLayout>
    </>
  );
}
