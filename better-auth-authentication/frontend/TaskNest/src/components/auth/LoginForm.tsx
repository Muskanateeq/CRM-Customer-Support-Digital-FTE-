/**
 * Login Form Component
 *
 * Form for user login with email and password.
 * Integrates with AuthContext for authentication.
 */

'use client';

import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import SocialLoginButtons from './SocialLoginButtons';

export default function LoginForm() {
  const { login, isLoading, error, clearError } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
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

    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
    }

    if (!formData.password) {
      errors.password = 'Password is required';
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
      await login({
        email: formData.email,
        password: formData.password,
      });
      // Navigation handled by AuthContext
    } catch (err) {
      // Error handled by AuthContext
      console.error('Login failed:', err);
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
            placeholder="Enter your password"
            value={formData.password}
            onChange={handleChange}
            required
            autoComplete="current-password"
            disabled={isLoading}
          />
          {formErrors.password && (
            <p className="error-message" style={{ marginTop: '0.5rem', marginBottom: 0 }}>
              {formErrors.password}
            </p>
          )}
          <div className="forgot-password">
            <a href="#">Forgot password?</a>
          </div>
        </div>

        {/* Submit button */}
        <button
          type="submit"
          className="btn-primary"
          disabled={isLoading}
        >
          {isLoading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>

      {/* Divider */}
      <div className="divider">
        <span>Or continue with</span>
      </div>

      {/* Social Login Buttons */}
      <SocialLoginButtons mode="login" onError={setSocialError} />
    </div>
  );
}
