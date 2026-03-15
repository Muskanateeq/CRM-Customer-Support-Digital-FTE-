/**
 * LiveRegion Component - Screen Reader Announcements
 *
 * Features:
 * - Announces dynamic content changes to screen readers
 * - Supports polite and assertive announcements
 * - Auto-clears announcements after delay
 * - Singleton pattern for global announcements
 */

'use client';

import React, { useEffect, useState } from 'react';

export interface LiveRegionProps {
  'aria-live'?: 'polite' | 'assertive';
  'aria-atomic'?: boolean;
  role?: 'status' | 'alert';
}

export default function LiveRegion({
  'aria-live': ariaLive = 'polite',
  'aria-atomic': ariaAtomic = true,
  role = 'status',
}: LiveRegionProps) {
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Listen for custom announcement events
    const handleAnnouncement = (event: CustomEvent<string>) => {
      setMessage(event.detail);

      // Clear message after 1 second to allow re-announcement of same message
      setTimeout(() => {
        setMessage('');
      }, 1000);
    };

    window.addEventListener('announce' as keyof WindowEventMap, handleAnnouncement as EventListener);

    return () => {
      window.removeEventListener('announce' as keyof WindowEventMap, handleAnnouncement as EventListener);
    };
  }, []);

  return (
    <div
      aria-live={ariaLive}
      aria-atomic={ariaAtomic}
      role={role}
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
      {message}
    </div>
  );
}

/**
 * Announce utility function
 *
 * Usage:
 * announce('Task completed successfully');
 * announce('Error: Failed to save task', 'assertive');
 */
export function announce(message: string, _priority: 'polite' | 'assertive' = 'polite') {
  const event = new CustomEvent('announce', { detail: message });
  window.dispatchEvent(event);
}
