/**
 * Authentication Context with Better Auth
 *
 * Provides authentication state and methods throughout the application.
 * Uses Better Auth for user login, logout, registration, and session management.
 */

'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import authClient, { getJWTToken } from '@/lib/auth-client';

/**
 * User Interface (from Better Auth)
 */
interface User {
  id: string;
  email: string;
  name?: string;
  emailVerified: boolean;
  image?: string;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Session Interface (from Better Auth)
 */
interface Session {
  user: User;
  session: {
    id: string;
    userId: string;
    expiresAt: Date;
    token: string;
    ipAddress?: string;
    userAgent?: string;
    createdAt: Date;
    updatedAt: Date;
  };
}

/**
 * Login Request
 */
interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Register Request
 */
interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
}

/**
 * Authentication Context State
 */
interface AuthContextState {
  user: User | null;
  session: Session | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  getToken: () => Promise<string | null>;
  clearError: () => void;
}

/**
 * Create Authentication Context
 */
const AuthContext = createContext<AuthContextState | undefined>(undefined);

/**
 * Authentication Provider Props
 */
interface AuthProviderProps {
  children: React.ReactNode;
}

/**
 * Authentication Provider Component
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  /**
   * Initialize authentication state from Better Auth session
   */
  useEffect(() => {
    const initAuth = async () => {
      try {
        console.log('[AuthContext] Initializing auth...');
        const { data, error } = await authClient.getSession();

        console.log('[AuthContext] getSession response:', { data, error });

        if (error) {
          console.error('[AuthContext] Failed to get session:', error);
          setSession(null);
        } else if (data) {
          console.log('[AuthContext] Session loaded successfully:', {
            user: data.user,
            session: data.session
          });
          setSession(data as Session);
        } else {
          console.log('[AuthContext] No session data returned');
          setSession(null);
        }
      } catch (err) {
        console.error('[AuthContext] Failed to initialize auth:', err);
        setSession(null);
      } finally {
        console.log('[AuthContext] Init complete, isLoading = false');
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  /**
   * Refresh session from Better Auth
   */
  const refreshSession = useCallback(async () => {
    try {
      console.log('[AuthContext] Refreshing session...');
      const { data, error } = await authClient.getSession();

      console.log('[AuthContext] Refresh session response:', { data, error });

      if (error) {
        console.error('[AuthContext] Failed to refresh session:', error);
        setSession(null);
      } else if (data) {
        console.log('[AuthContext] Session refreshed successfully:', {
          user: data.user,
          hasSession: !!data.session
        });
        setSession(data as Session);
      } else {
        console.log('[AuthContext] No session data on refresh');
        setSession(null);
      }
    } catch (err) {
      console.error('[AuthContext] Failed to refresh session:', err);
      setSession(null);
    }
  }, []);

  /**
   * Login user with Better Auth
   */
  const login = useCallback(async (credentials: LoginRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      console.log('[AuthContext] Starting login for:', credentials.email);

      const { data, error } = await authClient.signIn.email({
        email: credentials.email,
        password: credentials.password,
      });

      console.log('[AuthContext] Login response:', { data, error });

      if (error) {
        const errorMessage = error.message || 'Login failed. Please try again.';
        console.error('[AuthContext] Login error:', errorMessage);
        setError(errorMessage);
        throw new Error(errorMessage);
      }

      if (data) {
        console.log('[AuthContext] Login successful, fetching session...');

        // Wait a bit for cookies to be set
        await new Promise(resolve => setTimeout(resolve, 500));

        // Refresh session to get proper session structure
        const { data: sessionData, error: sessionError } = await authClient.getSession();

        console.log('[AuthContext] Session after login:', { sessionData, sessionError });

        if (sessionData) {
          setSession(sessionData as Session);
          console.log('[AuthContext] Session set, redirecting to /support');
        } else {
          console.warn('[AuthContext] No session data after login');
        }

        // Redirect to support portal after successful login
        router.push('/support');
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : 'Login failed. Please try again.';
      console.error('[AuthContext] Login exception:', err);
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  /**
   * Register new user with Better Auth
   */
  const register = useCallback(async (data: RegisterRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      console.log('[AuthContext] Starting registration for:', data.email);

      const { data: responseData, error } = await authClient.signUp.email({
        email: data.email,
        password: data.password,
        name: data.name || '',
      });

      console.log('[AuthContext] Registration response:', { responseData, error });

      if (error) {
        const errorMessage = error.message || 'Registration failed. Please try again.';
        console.error('[AuthContext] Registration error:', errorMessage);
        setError(errorMessage);
        throw new Error(errorMessage);
      }

      if (responseData) {
        console.log('[AuthContext] Registration successful, fetching session...');

        // Wait a bit for cookies to be set
        await new Promise(resolve => setTimeout(resolve, 500));

        // Refresh session to get proper session structure
        const { data: sessionData, error: sessionError } = await authClient.getSession();

        console.log('[AuthContext] Session after registration:', { sessionData, sessionError });

        if (sessionData) {
          setSession(sessionData as Session);
          console.log('[AuthContext] Session set, redirecting to /support');
        } else {
          console.warn('[AuthContext] No session data after registration');
        }

        // Redirect to support portal after successful signup
        router.push('/support');
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : 'Registration failed. Please try again.';
      console.error('[AuthContext] Registration exception:', err);
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  /**
   * Logout user with Better Auth
   */
  const logout = useCallback(async () => {
    try {
      await authClient.signOut();
      setSession(null);
      setError(null);
      // Redirect to home page
      router.push('/');
    } catch (err) {
      console.error('Logout failed:', err);
      // Force logout even if API call fails
      setSession(null);
      router.push('/');
    }
  }, [router]);

  /**
   * Get JWT token for API requests
   */
  const getToken = useCallback(async () => {
    return await getJWTToken();
  }, []);

  /**
   * Clear error message
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value: AuthContextState = {
    user: session?.user || null,
    session,
    isAuthenticated: !!session?.user,
    isLoading,
    error,
    login,
    register,
    logout,
    refreshSession,
    getToken,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * useAuth Hook
 *
 * Custom hook to access authentication context.
 * Must be used within AuthProvider.
 *
 * @throws Error if used outside AuthProvider
 */
export function useAuth(): AuthContextState {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}
