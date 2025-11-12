import React from 'react';
import Head from 'next/head';
import { AuthLayout } from '../components/auth/AuthLayout';
import { LoginForm } from '../components/auth/LoginForm';

export default function LoginPage() {
  const handleLogin = async (data: any) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));

    // In production, this would call your auth API
    console.log('Login data:', data);

    // For demo, throw error if email is 'error@test.com'
    if (data.email === 'error@test.com') {
      throw new Error('Invalid credentials');
    }
  };

  const handleGoogleLogin = () => {
    // In production, this would initiate OAuth flow
    console.log('Google login initiated');
    window.location.href = '/api/auth/google';
  };

  return (
    <>
      <Head>
        <title>Sign In | Meta-Analysis Research Platform</title>
        <meta name="description" content="Sign in to access AI-powered meta-analysis tools, systematic reviews, and research synthesis." />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
      </Head>

      <AuthLayout
        title="Welcome back"
        subtitle="Sign in to continue your research"
        side="right"
      >
        <LoginForm onSubmit={handleLogin} onGoogleLogin={handleGoogleLogin} />
      </AuthLayout>
    </>
  );
}
