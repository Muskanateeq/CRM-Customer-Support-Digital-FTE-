/**
 * Better Auth Client Configuration
 *
 * This file creates the Better Auth client for use in frontend components.
 * It provides methods for authentication operations and JWT token management.
 */

import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

// Determine base URL based on environment
// In production on Vercel, use empty string (same domain via proxy)
// In development, use localhost
const getBaseURL = () => {
  if (typeof window === "undefined") {
    // Server-side: use environment variable or localhost
    return process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
  }

  // Client-side: check if we're on Vercel
  const hostname = window.location.hostname;
  const isVercel = hostname.includes("vercel.app") || hostname === "custora-tau.vercel.app";

  if (isVercel) {
    // Production: use same domain (empty string means current domain)
    return "";
  }

  // Development: use localhost
  return "http://localhost:3000";
};

// Create Better Auth client with JWT plugin
export const authClient = createAuthClient({
  // Base URL for auth endpoints
  baseURL: getBaseURL(),
  basePath: "/api/auth",
  // Add JWT plugin to client
  plugins: [jwtClient()],
  fetchOptions: {
    credentials: "include", // Important: include cookies in requests
  },
});

/**
 * Get JWT token for API requests
 *
 * This function retrieves a JWT token from Better Auth
 * that can be sent to the FastAPI backend for authentication.
 *
 * @returns JWT token string or null if not authenticated
 */
export async function getJWTToken(): Promise<string | null> {
  try {
    // Use authClient.token() to get JWT token
    const { data, error } = await authClient.token();

    if (error) {
      console.error("Failed to get JWT token:", error);
      return null;
    }

    return data?.token || null;
  } catch (error) {
    console.error("Error getting JWT token:", error);
    return null;
  }
}

/**
 * Get authorization header for API requests
 *
 * @returns Authorization header object or empty object
 */
export async function getAuthHeader(): Promise<Record<string, string>> {
  const token = await getJWTToken();

  if (token) {
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  return {};
}

// Export auth client as default
export default authClient;
