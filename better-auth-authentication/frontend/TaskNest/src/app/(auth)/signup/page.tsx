/**
 * Signup Page - TaskNest
 * Modern dark theme authentication page
 */

'use client';

import React from 'react';
import Link from 'next/link';
import SignupForm from '@/components/auth/SignupForm';
import '../auth.css';

export default function SignupPage() {
  return (
    <div className="auth-page">
      {/* Back to Home Button */}
      <Link href="/" className="back-to-home">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M19 12H5M12 19l-7-7 7-7" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        <span>Back to Home</span>
      </Link>

      <div className="signup-container">
        {/* Logo */}
        <div className="logo">
          <Link href="/">
            <div className="logo-text">TaskNest</div>
          </Link>
        </div>

        {/* Signup Card */}
        <div className="signup-card">
          {/* Header */}
          <div className="signup-header">
            <h1>Create Account</h1>
            <p>Start your journey with TaskNest today</p>
          </div>

          {/* Signup Form */}
          <SignupForm />

          {/* Sign In Link */}
          <div className="signin-link">
            Already have an account? <Link href="/login">Sign in</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
