/**
 * Better Auth Server Configuration
 *
 * This file configures Better Auth to handle authentication for Custora CRM.
 * It connects to the Neon PostgreSQL database and enables JWT token generation.
 */

import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { nextCookies } from "better-auth/next-js";
import { Pool } from "pg";

// Determine if we're in production
const isProduction = process.env.NODE_ENV === "production";
const appUrl = process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";

export const auth = betterAuth({
  // Database connection - uses Neon PostgreSQL with pg Pool
  database: new Pool({
    connectionString: process.env.DATABASE_URL!,
    ssl: {
      rejectUnauthorized: false, // Required for Neon
    },
  }),

  // Base URL for authentication endpoints
  baseURL: appUrl,
  basePath: "/api/auth",

  // Secret key for signing tokens (must match backend)
  secret: process.env.BETTER_AUTH_SECRET!,

  // Email and password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Disable for now, enable later
    minPasswordLength: 8,
    maxPasswordLength: 128,
  },

  // Social providers - Google and GitHub
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
      enabled: !!(process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET),
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID || "",
      clientSecret: process.env.GITHUB_CLIENT_SECRET || "",
      enabled: !!(process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET),
    },
  },

  // Account linking configuration
  account: {
    accountLinking: {
      enabled: true,
      // Trusted providers will auto-link even without email verification
      trustedProviders: ["google", "github"],
    },
  },

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update session every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24 * 7, // 7 days
    },
  },

  // Cookie configuration - production vs development
  cookies: {
    sessionToken: {
      name: "better-auth.session_token",
      options: {
        httpOnly: true,
        sameSite: isProduction ? "lax" : "lax",
        path: "/",
        secure: isProduction, // true in production, false in development
      },
    },
  },

  // Enable JWT plugin and Next.js cookies plugin for token generation
  plugins: [
    nextCookies(), // Required for Next.js on Vercel
    jwt({
      jwt: {
        // JWT configuration
        issuer: appUrl,
        audience: appUrl,
        expirationTime: "7d",

        // Define JWT payload structure
        definePayload: ({ user, session }) => {
          return {
            user_id: user.id,
            email: user.email,
            session_id: session.id,
          };
        },
      },
    }),
  ],

  // Trusted origins for CORS - include both local and production
  trustedOrigins: [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://custora-tau.vercel.app",
    "https://*.vercel.app", // Wildcard for all Vercel preview deployments
    "https://dzon-developer-custora-backend.hf.space",
    process.env.NEXT_PUBLIC_APP_URL || "",
  ].filter(Boolean),
});

// Export the auth handler type for use in API routes
export type Auth = typeof auth;
