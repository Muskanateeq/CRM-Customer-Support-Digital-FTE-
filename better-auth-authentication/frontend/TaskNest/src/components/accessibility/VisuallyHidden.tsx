/**
 * VisuallyHidden Component - Screen Reader Only Content
 *
 * Features:
 * - Hides content visually but keeps it accessible to screen readers
 * - Useful for descriptive labels, skip links, and announcements
 * - Follows accessibility best practices
 */

'use client';

import React from 'react';

export interface VisuallyHiddenProps {
  children: React.ReactNode;
  as?: React.ElementType;
}

export default function VisuallyHidden({
  children,
  as: Component = 'span',
}: VisuallyHiddenProps) {
  return (
    <Component
      style={{
        position: 'absolute',
        width: '1px',
        height: '1px',
        padding: '0',
        margin: '-1px',
        overflow: 'hidden',
        clip: 'rect(0, 0, 0, 0)',
        whiteSpace: 'nowrap',
        border: '0',
      }}
    >
      {children}
    </Component>
  );
}
