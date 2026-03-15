/**
 * Providers Component
 *
 * Client-side providers wrapper for the application.
 * Wraps all context providers (Auth, Refresh, Toast, etc.)
 */

'use client';

import React from 'react';
import { AuthProvider } from '@/contexts/AuthContext';
import { RefreshProvider } from '@/contexts/RefreshContext';

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <AuthProvider>
      <RefreshProvider>
        {children}
      </RefreshProvider>
    </AuthProvider>
  );
}
