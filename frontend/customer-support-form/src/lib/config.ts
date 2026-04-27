/**
 * Frontend Configuration
 *
 * Handles environment-specific configuration for API URLs.
 * In production, uses Vercel proxy to avoid cross-domain issues.
 */

/**
 * Get backend API URL based on environment
 *
 * Development: Direct to localhost:8001
 * Production: Via Vercel proxy /api/backend
 */
export function getBackendURL(): string {
  // Server-side rendering
  if (typeof window === "undefined") {
    return process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8001";
  }

  // Client-side: check if we're on Vercel
  const hostname = window.location.hostname;
  const isProduction = hostname.includes("vercel.app") || hostname === "custora-tau.vercel.app";

  if (isProduction) {
    // Production: use Vercel proxy (same domain)
    return "/api/backend";
  }

  // Development: direct to backend
  return process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8001";
}

/**
 * Get app URL based on environment
 */
export function getAppURL(): string {
  if (typeof window === "undefined") {
    return process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
  }

  const hostname = window.location.hostname;
  const isProduction = hostname.includes("vercel.app") || hostname === "custora-tau.vercel.app";

  if (isProduction) {
    return `https://${hostname}`;
  }

  return "http://localhost:3000";
}

/**
 * Check if running in production
 */
export function isProduction(): boolean {
  if (typeof window === "undefined") {
    return process.env.NODE_ENV === "production";
  }

  const hostname = window.location.hostname;
  return hostname.includes("vercel.app") || hostname === "custora-tau.vercel.app";
}

export const config = {
  backendURL: getBackendURL(),
  appURL: getAppURL(),
  isProduction: isProduction(),
};
