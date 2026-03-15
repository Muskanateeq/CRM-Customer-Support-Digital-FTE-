/**
 * Spinner Component
 *
 * Loading spinner with multiple sizes and colors.
 * Uses Gamboge color scheme.
 */

import React from 'react';

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'white' | 'black';
  className?: string;
}

export function Spinner({
  size = 'md',
  color = 'primary',
  className = '',
}: SpinnerProps) {
  // Size styles
  const sizeStyles = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16',
  };

  // Color styles
  const colorStyles = {
    primary: 'text-[#E49B0F]',
    white: 'text-white',
    black: 'text-black',
  };

  return (
    <div className={`inline-block ${className}`} role="status" aria-label="Loading">
      <svg
        className={`animate-spin ${sizeStyles[size]} ${colorStyles[color]}`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <span className="sr-only">Loading...</span>
    </div>
  );
}

/**
 * Full Page Spinner
 *
 * Centered spinner that covers the entire viewport.
 */
export function FullPageSpinner() {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-white bg-opacity-75 z-50">
      <Spinner size="xl" color="primary" />
    </div>
  );
}

// Export Spinner as default
export default Spinner;
