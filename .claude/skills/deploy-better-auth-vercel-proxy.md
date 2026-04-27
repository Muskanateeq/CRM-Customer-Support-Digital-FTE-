# Deploy Better Auth with Vercel Proxy

## Description
Deploy Better Auth authentication system with cross-domain cookie support using Vercel proxy approach. Solves Safari ITP blocking and state_mismatch errors by making auth requests appear same-domain.

## Problem Solved
- Cross-domain cookie blocking (Safari ITP)
- OAuth state_mismatch errors
- Authentication works locally but fails in production
- Different domains for frontend (Vercel) and auth server (Render/other)

## Solution Architecture
```
User Browser
    ↓
Vercel Frontend (https://your-app.vercel.app)
    ↓ Request to /api/auth/*
Vercel Proxy (rewrites)
    ↓ Forwards to
Auth Server (https://your-auth-server.com)
    ↓ Response with cookies
Vercel Proxy
    ↓ Sets cookies for your-app.vercel.app
User Browser (cookies work! same domain)
```

## Prerequisites
- Existing auth server deployed (Render, Railway, etc.)
- Better Auth configured with social providers
- Vercel project for frontend
- OAuth apps configured (Google, GitHub, etc.)

## Implementation Steps

### Step 1: Configure Vercel Proxy

Create or update `vercel.json` in your frontend root:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "rewrites": [
    {
      "source": "/api/auth/:path*",
      "destination": "https://your-auth-server.com/api/auth/:path*"
    }
  ]
}
```

**Replace:** `your-auth-server.com` with your actual auth server URL

### Step 2: Update Frontend Auth Configuration

In your auth client configuration (e.g., `src/config/env.ts`):

```typescript
const PRODUCTION_CONFIG = {
  AUTH_SERVER_URL: '', // Empty string = same domain (Vercel proxy)
  BACKEND_API_URL: 'https://your-backend.com',
};

const DEVELOPMENT_CONFIG = {
  AUTH_SERVER_URL: 'http://localhost:3001', // Local auth server
  BACKEND_API_URL: 'http://localhost:8001',
};

function getConfig() {
  if (typeof window === 'undefined') {
    return DEVELOPMENT_CONFIG;
  }

  const hostname = window.location.hostname;
  const isProduction = hostname.includes('vercel.app') || 
                       hostname.includes('your-domain.com');

  return isProduction ? PRODUCTION_CONFIG : DEVELOPMENT_CONFIG;
}

export const ENV = {
  get AUTH_SERVER_URL() {
    return getConfig().AUTH_SERVER_URL;
  },
  get BACKEND_API_URL() {
    return getConfig().BACKEND_API_URL;
  },
};
```

### Step 3: Update Auth Client

In your auth client file (e.g., `src/lib/auth-client.ts`):

```typescript
import { createAuthClient } from "better-auth/react";
import { ENV } from "../config/env";

export const authClient = createAuthClient({
  baseURL: ENV.AUTH_SERVER_URL !== undefined && ENV.AUTH_SERVER_URL !== null
    ? ENV.AUTH_SERVER_URL
    : "http://localhost:3001",
  fetchOptions: {
    credentials: "include",
  },
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession
} = authClient;
```

### Step 4: Update Auth Server Environment Variables

On your auth server (Render/Railway/etc.), update:

```env
# Change BETTER_AUTH_URL to your Vercel domain
BETTER_AUTH_URL=https://your-app.vercel.app

# Frontend URL (same as above)
FRONTEND_URL=https://your-app.vercel.app

# Keep other variables as-is
DATABASE_URL=your_database_url
BETTER_AUTH_SECRET=your_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

**Important:** After updating, the auth server will auto-redeploy.

### Step 5: Update OAuth Redirect URIs

#### Google Cloud Console
1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth 2.0 Client
3. **Authorized JavaScript origins:**
   - Add: `https://your-app.vercel.app`
4. **Authorized redirect URIs:**
   - Add: `https://your-app.vercel.app/api/auth/callback/google`
5. Save

#### GitHub OAuth App
1. Go to: https://github.com/settings/developers
2. Find your OAuth App
3. **Homepage URL:**
   - Set: `https://your-app.vercel.app`
4. **Authorization callback URL:**
   - Set: `https://your-app.vercel.app/api/auth/callback/github`
5. Update application

### Step 6: Clean Vercel Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

**Remove these** (no longer needed, auth server handles them):
- `DATABASE_URL`
- `BETTER_AUTH_SECRET`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`

Vercel only needs frontend-specific variables now.

### Step 7: Deploy

```bash
git add -A
git commit -m "Configure Vercel proxy for Better Auth"
git push origin main
```

Vercel will auto-deploy. Wait 2-3 minutes.

### Step 8: Test Authentication

1. **Clear browser cache** (Ctrl + Shift + R)
2. Go to: `https://your-app.vercel.app/signin`
3. Test email/password sign in
4. Test Google sign in
5. Test GitHub sign in
6. Verify session persists after page refresh
7. Test in Safari (should work now!)

## Verification Checklist

- [ ] `vercel.json` has rewrite configuration
- [ ] Frontend `AUTH_SERVER_URL` is empty string in production
- [ ] Auth server `BETTER_AUTH_URL` points to Vercel domain
- [ ] Google OAuth redirect URI uses Vercel domain
- [ ] GitHub OAuth callback URL uses Vercel domain
- [ ] Vercel environment variables cleaned (auth vars removed)
- [ ] Deployment successful
- [ ] Email/password sign in works
- [ ] Google sign in works
- [ ] GitHub sign in works
- [ ] Session persists after refresh
- [ ] Works in Safari

## Troubleshooting

### Issue: 404 on /api/auth/*
**Cause:** Vercel rewrite not configured correctly
**Solution:** Check `vercel.json` syntax, ensure auth server URL is correct

### Issue: redirect_uri_mismatch
**Cause:** OAuth redirect URIs not updated
**Solution:** Verify Google/GitHub console has Vercel domain URLs

### Issue: Cookies not set
**Cause:** Auth server still using old domain
**Solution:** Verify `BETTER_AUTH_URL` on auth server is Vercel domain

### Issue: CORS errors
**Cause:** Auth server CORS not allowing Vercel domain
**Solution:** Add Vercel domain to `trustedOrigins` in Better Auth config

## Benefits

✅ **Same-domain cookies** - Browser accepts cookies from Vercel domain
✅ **Safari compatible** - No ITP blocking
✅ **Simple** - No serverless complexity
✅ **Proven** - Documented approach in Better Auth docs
✅ **Maintainable** - Auth server remains independent
✅ **Fast** - Vercel edge network proxying

## Alternative Approaches Tried

### ❌ Serverless Function Approach
- Created `api/auth/[...auth].mjs` serverless function
- Issues: POST requests returned 404, complex debugging
- Abandoned due to Vercel routing limitations

### ❌ Direct Cross-Domain
- Frontend on Vercel, auth on Render (different domains)
- Issues: Safari ITP blocking, state_mismatch errors
- Cookies don't work across domains

### ✅ Vercel Proxy (Current)
- Simple rewrite configuration
- Auth server remains on Render
- All requests appear same-domain
- Works perfectly!

## Notes

- Auth server can stay on any platform (Render, Railway, Fly.io)
- Vercel only handles proxying, not auth logic
- Local development still uses localhost:3001
- Production uses Vercel domain for everything
- No code changes needed in auth server logic

## Related Documentation

- [Better Auth Cookies](https://better-auth.com/docs/concepts/cookies)
- [Vercel Rewrites](https://vercel.com/docs/projects/project-configuration#rewrites)
- [Safari ITP](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/)

## Success Criteria

Authentication should work exactly like local development:
- Sign in redirects properly
- Session persists
- Sign out works
- Works in all browsers (Chrome, Safari, Firefox)
- No console errors
- OAuth flows complete successfully
