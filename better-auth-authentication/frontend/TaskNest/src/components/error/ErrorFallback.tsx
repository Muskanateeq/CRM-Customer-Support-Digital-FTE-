/**
 * ErrorFallback Component - Reusable Error UI
 *
 * Features:
 * - Lightweight error display
 * - Customizable title and message
 * - Retry functionality
 * - Multiple variants (page, card, inline)
 */

'use client';

import React from 'react';
import Button from '@/components/ui/Button';

export interface ErrorFallbackProps {
  error?: Error;
  resetError?: () => void;
  title?: string;
  message?: string;
  variant?: 'page' | 'card' | 'inline';
  showDetails?: boolean;
}

export default function ErrorFallback({
  error,
  resetError,
  title = 'Something went wrong',
  message = 'An unexpected error occurred. Please try again.',
  variant = 'card',
  showDetails = false,
}: ErrorFallbackProps) {
  /**
   * Page variant - Full page error
   */
  if (variant === 'page') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border-2 border-red-200 p-8 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
          <p className="text-gray-600 mb-6">{message}</p>

          {showDetails && error && (
            <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-lg text-left">
              <p className="text-xs text-red-800 font-mono break-all">{error.message}</p>
            </div>
          )}

          {resetError && (
            <Button variant="gradient" onClick={resetError} className="w-full">
              Try Again
            </Button>
          )}
        </div>
      </div>
    );
  }

  /**
   * Card variant - Card-style error
   */
  if (variant === 'card') {
    return (
      <div className="bg-white rounded-xl border-2 border-red-200 p-6 text-center">
        <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-sm text-gray-600 mb-4">{message}</p>

        {showDetails && error && (
          <div className="mb-4 p-2 bg-red-50 border border-red-200 rounded text-left">
            <p className="text-xs text-red-800 font-mono break-all">{error.message}</p>
          </div>
        )}

        {resetError && (
          <Button variant="gradient" onClick={resetError} size="sm">
            Try Again
          </Button>
        )}
      </div>
    );
  }

  /**
   * Inline variant - Compact inline error
   */
  return (
    <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-red-900">{title}</h4>
          <p className="text-sm text-red-800 mt-1">{message}</p>

          {showDetails && error && (
            <p className="text-xs text-red-700 font-mono mt-2 break-all">{error.message}</p>
          )}
        </div>
        {resetError && (
          <button
            onClick={resetError}
            className="flex-shrink-0 text-sm font-medium text-red-600 hover:text-red-800 transition-colors"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
}
