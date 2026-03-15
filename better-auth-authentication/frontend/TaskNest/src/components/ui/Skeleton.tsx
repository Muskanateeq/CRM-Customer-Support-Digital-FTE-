/**
 * Skeleton Component - Generic Loading Placeholder
 *
 * Features:
 * - Animated shimmer effect
 * - Customizable width, height, and shape
 * - Rounded corners support
 * - Accessible loading state
 */

'use client';

import React from 'react';

export interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  className?: string;
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

export default function Skeleton({
  width = '100%',
  height = '1rem',
  className = '',
  rounded = 'md',
}: SkeletonProps) {
  const roundedClass = {
    none: '',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    xl: 'rounded-xl',
    full: 'rounded-full',
  }[rounded];

  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  };

  return (
    <div
      className={`bg-gray-200 animate-pulse relative overflow-hidden ${roundedClass} ${className}`}
      style={style}
      role="status"
      aria-label="Loading..."
    >
      {/* Shimmer effect */}
      <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/40 to-transparent" />
    </div>
  );
}
