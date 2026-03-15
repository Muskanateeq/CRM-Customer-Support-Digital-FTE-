/**
 * TrendIndicator Component
 * Shows trend direction with icon and percentage
 */

'use client';

import React from 'react';
import './TrendIndicator.css';

interface TrendIndicatorProps {
  direction: 'up' | 'down' | 'neutral';
  percentage?: number;
  label?: string;
}

export default function TrendIndicator({
  direction,
  percentage,
  label,
}: TrendIndicatorProps) {
  const getIcon = () => {
    switch (direction) {
      case 'up':
        return (
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16" aria-label="Trending up">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        );
      case 'down':
        return (
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16" aria-label="Trending down">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
          </svg>
        );
      case 'neutral':
        return (
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16" aria-label="Neutral trend">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
          </svg>
        );
    }
  };

  return (
    <div className={`trend-indicator trend-${direction}`} role="status" aria-label={`Trend: ${direction}`}>
      <span className="trend-icon">{getIcon()}</span>
      {percentage !== undefined && (
        <span className="trend-percentage">{Math.abs(percentage)}%</span>
      )}
      {label && <span className="trend-label">{label}</span>}
    </div>
  );
}
