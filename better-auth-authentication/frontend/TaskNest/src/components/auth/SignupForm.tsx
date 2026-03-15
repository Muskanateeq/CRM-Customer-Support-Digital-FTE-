/**
 * Signup Form Component
 *
 * Form for user registration with email, password, and name.
 * Integrates with AuthContext for authentication.
 */

'use client';

import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import SocialLoginButtons from './SocialLoginButtons';

export default function SignupForm() {
  const { register, isLoading, error, clearError } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  });
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [socialError, setSocialError] = useState<string | null>(null);

  /**
   * Handle input change
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear field error when user types
    if (formErrors[name]) {
      setFormErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }

    // Clear global error
    if (error) {
      clearError();
    }
  };

  /**
   * Validate form
   */
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name) {
      errors.name = 'Full name is required';
    }

    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
    }

    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    }

    if (!agreedToTerms) {
      errors.terms = 'You must agree to the Terms of Service and Privacy Policy';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate form
    if (!validateForm()) {
      return;
    }

    try {
      await register({
        email: formData.email,
        password: formData.password,
        name: formData.name,
      });
      // Navigation handled by AuthContext
    } catch (err) {
      // Error handled by AuthContext
      console.error('Registration failed:', err);
    }
  };

  return (
    <div>
      {/* Email/Password Form */}
      <form onSubmit={handleSubmit}>
        {/* Global error message */}
        {(error || socialError) && (
          <div className="error-message">
            {error || socialError}
          </div>
        )}

        {/* Name field */}
        <div className="form-group">
          <label className="form-label" htmlFor="name">Full Name</label>
          <input
            type="text"
            id="name"
            name="name"
            className="form-input"
            placeholder="Enter your full name"
            value={formData.name}
            onChange={handleChange}
            required
            autoComplete="name"
            disabled={isLoading}
          />
          {formErrors.name && (
            <p className="error-message" style={{ marginTop: '0.5rem', marginBottom: 0 }}>
              {formErrors.name}
            </p>
          )}
        </div>

        {/* Email field */}
        <div className="form-group">
          <label className="form-label" htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            name="email"
            className="form-input"
            placeholder="Enter your email"
            value={formData.email}
            onChange={handleChange}
            required
            autoComplete="email"
            disabled={isLoading}
          />
          {formErrors.email && (
            <p className="error-message" style={{ marginTop: '0.5rem', marginBottom: 0 }}>
              {formErrors.email}
            </p>
          )}
        </div>

        {/* Password field */}
        <div className="form-group">
          <label className="form-label" htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            className="form-input"
            placeholder="Create a password"
            value={formData.password}
            onChange={handleChange}
            required
            autoComplete="new-password"
            disabled={isLoading}
          />
          {formErrors.password && (
            <p className="error-message" style={{ marginTop: '0.5rem', marginBottom: 0 }}>
              {formErrors.password}
            </p>
          )}
        </div>

        {/* Terms checkbox */}
        <div className="checkbox-group">
          <input
            type="checkbox"
            id="terms"
            className="checkbox-input"
            checked={agreedToTerms}
            onChange={(e) => setAgreedToTerms(e.target.checked)}
            disabled={isLoading}
          />
          <label htmlFor="terms" className="checkbox-label">
            I agree to the{' '}
            <a href="#">Terms of Service</a>
            {' '}and{' '}
            <a href="#">Privacy Policy</a>
          </label>
        </div>
        {formErrors.terms && (
          <p className="error-message" style={{ marginTop: '-1rem', marginBottom: '1rem' }}>
            {formErrors.terms}
          </p>
        )}

        {/* Submit button */}
        <button
          type="submit"
          className="btn-primary"
          disabled={isLoading}
        >
          {isLoading ? 'Creating account...' : 'Create Account'}
        </button>
      </form>

      {/* Divider */}
      <div className="divider">
        <span>Or continue with</span>
      </div>

      {/* Social Login Buttons */}
      <SocialLoginButtons mode="signup" onError={setSocialError} />
    </div>
  );
}
