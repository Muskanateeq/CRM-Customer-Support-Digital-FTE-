/**
 * ProgressBar Component
 * Animated progress bar with shimmer effect
 */

'use client';

import React from 'react';
import './ProgressBar.css';

interface ProgressBarProps {
  value: number; // 0-100
  color?: 'primary' | 'success' | 'warning' | 'danger';
  showLabel?: boolean;
  animated?: boolean;
  height?: 'sm' | 'md' | 'lg';
}

export default function ProgressBar({
  value,
  color = 'primary',
  showLabel = true,
  animated = true,
  height = 'md',
}: ProgressBarProps) {
  // Clamp value between 0 and 100
  const clampedValue = Math.min(Math.max(value, 0), 100);

  return (
    <div className="progress-bar-container">
      <div className={`progress-bar progress-bar-${height}`}>
        <div
          className={`progress-bar-fill progress-bar-${color} ${animated ? 'animated' : ''}`}
          style={{ width: `${clampedValue}%` }}
          role="progressbar"
          aria-valuenow={clampedValue}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Progress: ${clampedValue}%`}
        >
          {animated && <div className="progress-bar-shimmer" />}
        </div>
      </div>
      {showLabel && (
        <span className="progress-bar-label">{clampedValue}%</span>
      )}
    </div>
  );
}
