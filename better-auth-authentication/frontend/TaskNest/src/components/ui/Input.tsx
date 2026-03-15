/**
 * Modern Input Component - Production Level
 *
 * Features:
 * - Smooth focus animations
 * - Enhanced visual feedback
 * - Modern styling with Gamboge accent
 * - Icon support
 * - Better accessibility
 */

import React, { forwardRef, useState } from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      fullWidth = false,
      className = '',
      id,
      icon,
      ...props
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = useState(false);
    // Use useId for stable IDs across server and client (fixes hydration error)
    const generatedId = React.useId();
    const inputId = id || generatedId;

    // Base styles with modern design - INCREASED PADDING FOR BETTER VISIBILITY
    const baseStyles = 'px-5 py-4 text-base border-2 rounded-xl transition-all duration-300 focus:outline-none';

    // State styles with enhanced animations
    const stateStyles = error
      ? 'border-red-500 focus:border-red-600 focus:ring-4 focus:ring-red-100 bg-red-50'
      : isFocused
      ? 'border-[#E49B0F] ring-4 ring-[#E49B0F]/20 bg-white shadow-lg shadow-[#E49B0F]/10'
      : 'border-gray-300 hover:border-[#E49B0F]/50 bg-white hover:shadow-md';

    // Width styles
    const widthStyles = fullWidth ? 'w-full' : '';

    // Disabled styles
    const disabledStyles = props.disabled
      ? 'bg-gray-100 cursor-not-allowed opacity-60 hover:shadow-none'
      : '';

    // Icon padding
    const iconPadding = icon ? 'pl-12' : '';

    // Combine all styles
    const combinedStyles = `${baseStyles} ${stateStyles} ${widthStyles} ${disabledStyles} ${iconPadding} ${className}`;

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {label && (
          <label
            htmlFor={inputId}
            className={`block text-sm font-semibold mb-2 transition-colors ${
              isFocused ? 'text-[#E49B0F]' : error ? 'text-red-600' : 'text-gray-700'
            }`}
          >
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}

        <div className="relative">
          {icon && (
            <div className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors ${
              isFocused ? 'text-[#E49B0F]' : 'text-gray-400'
            }`}>
              {icon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            className={combinedStyles}
            onFocus={(e) => {
              setIsFocused(true);
              props.onFocus?.(e);
            }}
            onBlur={(e) => {
              setIsFocused(false);
              props.onBlur?.(e);
            }}
            {...props}
          />

          {/* Focus indicator line */}
          <div
            className={`absolute bottom-0 left-0 h-0.5 bg-gradient-to-r from-[#E49B0F] to-[#F5B041] transition-all duration-300 ${
              isFocused ? 'w-full' : 'w-0'
            }`}
          />
        </div>

        {error && (
          <div className="mt-2 flex items-start gap-2 animate-fade-in">
            <svg
              className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
            <p className="text-sm text-red-600 font-medium">{error}</p>
          </div>
        )}

        {helperText && !error && (
          <p className="mt-2 text-sm text-gray-500 flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

// Export as default for easier imports
export default Input;
