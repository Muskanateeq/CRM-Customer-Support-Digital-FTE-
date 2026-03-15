/**
 * Better Auth API Route Handler
 *
 * This route handles all Better Auth endpoints:
 * - POST /api/auth/sign-up (registration)
 * - POST /api/auth/sign-in/email (login)
 * - POST /api/auth/sign-out (logout)
 * - GET /api/auth/session (get current session)
 * - GET /api/auth/jwks (JWKS endpoint for JWT verification)
 * - POST /api/auth/token (get JWT token)
 */

import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

// Export Better Auth handlers for all HTTP methods
export const { GET, POST } = toNextJsHandler(auth);
