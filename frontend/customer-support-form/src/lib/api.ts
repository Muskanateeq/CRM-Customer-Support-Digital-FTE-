/**
 * API Helper Functions
 *
 * Utilities for making authenticated API requests to the backend.
 * Automatically includes JWT token in Authorization header.
 */

import { getAuthHeader } from "./auth-client";

/**
 * Fetch with authentication
 *
 * Makes a fetch request with JWT token automatically included.
 *
 * @param url - API endpoint URL
 * @param options - Fetch options
 * @returns Fetch response
 */
export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const authHeader = await getAuthHeader();

  return fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
      ...authHeader,
    },
  });
}

/**
 * GET request with authentication
 */
export async function apiGet(url: string) {
  const response = await fetchWithAuth(url, {
    method: "GET",
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * POST request with authentication
 */
export async function apiPost(url: string, data: unknown) {
  const response = await fetchWithAuth(url, {
    method: "POST",
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * PUT request with authentication
 */
export async function apiPut(url: string, data: unknown) {
  const response = await fetchWithAuth(url, {
    method: "PUT",
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * DELETE request with authentication
 */
export async function apiDelete(url: string) {
  const response = await fetchWithAuth(url, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }

  return response.json();
}
