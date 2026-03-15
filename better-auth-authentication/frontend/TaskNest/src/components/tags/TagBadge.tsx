/**
 * TagBadge Component
 * Dark Golden Theme - Modern SaaS Design
 */

'use client';

import React from 'react';
import './TagBadge.css';

export interface TagBadgeProps {
  name: string;
  onRemove?: () => void;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'primary' | 'outline';
  className?: string;
}

export default function TagBadge({
  name,
  onRemove,
  size = 'md',
  variant = 'default',
  className = '',
}: TagBadgeProps) {
  return (
    <span className={`tag-badge size-${size} variant-${variant} ${className}`}>
      {/* Tag icon */}
      <svg
        className="tag-badge-icon"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
        />
      </svg>

      {/* Tag name */}
      <span className="tag-badge-name">{name}</span>

      {/* Remove button */}
      {onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="tag-badge-remove"
          aria-label="Remove tag"
        >
          <svg
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      )}
    </span>
  );
}
