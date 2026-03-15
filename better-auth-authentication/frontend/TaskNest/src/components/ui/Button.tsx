/**
 * Modern Button Component - Production Level
 *
 * Features:
 * - Ripple effect on click
 * - Smooth hover animations
 * - Gradient variants
 * - Enhanced visual feedback
 * - Icon support
 * - Loading states with spinner
 */

'use client';

import React, { useState, useRef } from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'gradient';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  fullWidth?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  children: React.ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  fullWidth = false,
  disabled,
  className = '',
  icon,
  iconPosition = 'left',
  children,
  onClick,
  ...props
}: ButtonProps) {
  const [ripples, setRipples] = useState<Array<{ x: number; y: number; id: number }>>([]);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Handle ripple effect
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled || isLoading) return;

    const button = buttonRef.current;
    if (!button) return;

    const rect = button.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const id = Date.now();

    setRipples((prev) => [...prev, { x, y, id }]);

    // Remove ripple after animation
    setTimeout(() => {
      setRipples((prev) => prev.filter((ripple) => ripple.id !== id));
    }, 600);

    onClick?.(e);
  };

  // Base styles with modern design
  const baseStyles = 'relative inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-300 focus:outline-none focus:ring-4 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden group';

  // Variant styles with enhanced effects
  const variantStyles = {
    primary: 'bg-gradient-to-r from-[#E49B0F] to-[#C28608] text-white hover:shadow-xl hover:shadow-[#E49B0F]/50 focus:ring-[#E49B0F]/30 hover:scale-105 active:scale-95',
    secondary: 'bg-white text-gray-900 border-2 border-gray-300 hover:border-[#E49B0F] hover:text-[#E49B0F] hover:shadow-lg focus:ring-[#E49B0F]/30 hover:scale-105 active:scale-95',
    ghost: 'bg-transparent text-[#E49B0F] hover:bg-[#E49B0F]/10 focus:ring-[#E49B0F]/30 hover:scale-105 active:scale-95',
    danger: 'bg-gradient-to-r from-red-600 to-red-700 text-white hover:shadow-xl hover:shadow-red-500/50 focus:ring-red-500/30 hover:scale-105 active:scale-95',
    gradient: 'bg-gradient-to-r from-[#E49B0F] via-[#F5B041] to-[#E49B0F] bg-size-200 text-white hover:bg-pos-100 hover:shadow-xl hover:shadow-[#E49B0F]/50 focus:ring-[#E49B0F]/30 animate-gradient hover:scale-105 active:scale-95',
  };

  // Size styles
  const sizeStyles = {
    sm: 'px-4 py-2 text-sm gap-2',
    md: 'px-6 py-3 text-base gap-2',
    lg: 'px-8 py-4 text-lg gap-3',
  };

  // Width styles
  const widthStyles = fullWidth ? 'w-full' : '';

  // Combine all styles
  const combinedStyles = `${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${widthStyles} ${className}`;

  return (
    <button
      ref={buttonRef}
      className={combinedStyles}
      disabled={disabled || isLoading}
      onClick={handleClick}
      {...props}
    >
      {/* Ripple effects */}
      {ripples.map((ripple) => (
        <span
          key={ripple.id}
          className="absolute bg-white/30 rounded-full animate-ripple pointer-events-none"
          style={{
            left: ripple.x,
            top: ripple.y,
            width: 0,
            height: 0,
          }}
        />
      ))}

      {/* Shine effect on hover */}
      <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />

      {/* Content */}
      <span className="relative flex items-center justify-center gap-2">
        {isLoading ? (
          <>
            <svg
              className="animate-spin h-5 w-5"
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
            <span>Loading...</span>
          </>
        ) : (
          <>
            {icon && iconPosition === 'left' && <span className="flex-shrink-0">{icon}</span>}
            <span>{children}</span>
            {icon && iconPosition === 'right' && <span className="flex-shrink-0">{icon}</span>}
          </>
        )}
      </span>

      {/* Custom Animations */}
      <style jsx>{`
        @keyframes ripple {
          to {
            width: 500px;
            height: 500px;
            opacity: 0;
            transform: translate(-50%, -50%);
          }
        }
        .animate-ripple {
          animation: ripple 0.6s ease-out;
        }
        .bg-size-200 {
          background-size: 200% 200%;
        }
        .bg-pos-100 {
          background-position: 100% 0;
        }
      `}</style>
    </button>
  );
}

// Export as default for easier imports
export default Button;
