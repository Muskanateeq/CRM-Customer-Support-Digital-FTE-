/**
 * Refresh Context
 *
 * Provides a centralized way to trigger data refreshes across the app.
 * Used by chatbot to automatically update UI after performing actions.
 */

'use client';

import React, { createContext, useContext, useCallback, ReactNode } from 'react';

interface RefreshContextType {
  /**
   * Trigger refresh of all data (tasks, stats, etc.)
   */
  refreshAll: () => void;

  /**
   * Register a refresh callback
   */
  registerRefresh: (key: string, callback: () => void) => void;

  /**
   * Unregister a refresh callback
   */
  unregisterRefresh: (key: string) => void;
}

const RefreshContext = createContext<RefreshContextType | undefined>(undefined);

interface RefreshProviderProps {
  children: ReactNode;
}

export function RefreshProvider({ children }: RefreshProviderProps) {
  // Store refresh callbacks
  const refreshCallbacks = React.useRef<Map<string, () => void>>(new Map());

  /**
   * Register a refresh callback
   */
  const registerRefresh = useCallback((key: string, callback: () => void) => {
    refreshCallbacks.current.set(key, callback);
  }, []);

  /**
   * Unregister a refresh callback
   */
  const unregisterRefresh = useCallback((key: string) => {
    refreshCallbacks.current.delete(key);
  }, []);

  /**
   * Trigger all registered refresh callbacks
   */
  const refreshAll = useCallback(() => {
    console.log('[RefreshContext] Triggering refresh for all registered callbacks');
    refreshCallbacks.current.forEach((callback, key) => {
      console.log(`[RefreshContext] Refreshing: ${key}`);
      callback();
    });
  }, []);

  return (
    <RefreshContext.Provider value={{ refreshAll, registerRefresh, unregisterRefresh }}>
      {children}
    </RefreshContext.Provider>
  );
}

/**
 * Hook to access refresh context
 */
export function useRefresh() {
  const context = useContext(RefreshContext);
  if (!context) {
    throw new Error('useRefresh must be used within RefreshProvider');
  }
  return context;
}
