# 🎨 Custora Frontend - Vercel Deployment Guide

Complete step-by-step guide to deploy your Next.js 14 frontend to Vercel (FREE tier).

---

## 📋 Prerequisites

- ✅ Vercel account (free)
- ✅ GitHub repository with frontend code
- ✅ Backend deployed on Hugging Face (from Phase 1)
- ✅ Neon PostgreSQL database
- ✅ OAuth credentials (Google, GitHub)

---

## 🎯 Step 1: Create Vercel Account

1. Go to **https://vercel.com/signup**
2. **Sign up with GitHub** (recommended for easy integration)
3. Authorize Vercel to access your GitHub repositories
4. Complete profile setup

---

## 🚀 Step 2: Import Project

1. Click **"Add New..."** → **"Project"**

2. **Import Git Repository:**
   - Select your GitHub account
   - Find repository: `Hackathon5`
   - Click **"Import"**

3. **Configure Project:**
   - **Framework Preset**: Next.js (auto-detected ✓)
   - **Root Directory**: Click **"Edit"** → Select `frontend/customer-support-form`
   - **Build Command**: `npm run build` (default, leave as is)
   - **Output Directory**: `.next` (default, leave as is)
   - **Install Command**: `npm install` (default, leave as is)

---

## 🔐 Step 3: Add Environment Variables

Click **"Environment Variables"** section and add the following:

### **App URLs**
```bash
# Variable Name: NEXT_PUBLIC_APP_URL
# Value: https://your-app.vercel.app
# Note: You'll update this after first deployment with actual URL

# Variable Name: NEXT_PUBLIC_BACKEND_URL  
# Value: https://YOUR-USERNAME-custora-backend.hf.space
# Note: Use your Hugging Face Space URL from Phase 1
```

### **Database (Neon PostgreSQL)**
```bash
# Variable Name: DATABASE_URL
# Value: postgresql://neondb_owner:npg_6pbM0ZLOvNYm@ep-lively-heart-aimqvdi0-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### **Better Auth**
```bash
# Variable Name: BETTER_AUTH_SECRET
# Value: YzYuynKxZ5ch2RNZCXMusrwMscgZ95df
# Note: Must be same as backend

# Variable Name: BETTER_AUTH_URL
# Value: https://your-app.vercel.app
# Note: You'll update this after first deployment
```

### **Google OAuth (Optional)**
```bash
# Variable Name: GOOGLE_CLIENT_ID
# Value: YOUR_GOOGLE_CLIENT_ID_HERE
# Get from: https://console.cloud.google.com/apis/credentials

# Variable Name: GOOGLE_CLIENT_SECRET
# Value: YOUR_GOOGLE_CLIENT_SECRET_HERE
```

### **GitHub OAuth (Optional)**
```bash
# Variable Name: GITHUB_CLIENT_ID
# Value: YOUR_GITHUB_CLIENT_ID_HERE
# Get from: https://github.com/settings/developers

# Variable Name: GITHUB_CLIENT_SECRET
# Value: YOUR_GITHUB_CLIENT_SECRET_HERE
```

**Important**: Select **"Production"** for all environment variables.

---

## 🏗️ Step 4: Deploy

1. Click **"Deploy"** button
2. **Wait for build** (2-3 minutes):
   - Installing dependencies
   - Building Next.js application
   - Optimizing production build
   - Deploying to edge network

3. **Deployment complete!** 🎉

---

## 🌐 Step 5: Get Your Frontend URL

After deployment, Vercel provides a URL:

```
https://your-project-name.vercel.app
```

Or with your username:
```
https://your-project-name-username.vercel.app
```

**Example:**
```
https://custora-ai.vercel.app
```

**Save this URL** - you'll need it for OAuth configuration!

---

## 🔄 Step 6: Update Environment Variables

Now that you have your actual Vercel URL, update these variables:

1. Go to **Project Settings** → **Environment Variables**

2. **Edit** `NEXT_PUBLIC_APP_URL`:
   - New value: `https://your-actual-app.vercel.app`

3. **Edit** `BETTER_AUTH_URL`:
   - New value: `https://your-actual-app.vercel.app`

4. **Redeploy** to apply changes:
   - Go to **Deployments** tab
   - Click **"..."** on latest deployment
   - Click **"Redeploy"**

---

## 🔐 Step 7: Update OAuth Redirect URIs

### **Google OAuth Configuration**

1. Go to **Google Cloud Console**: https://console.cloud.google.com/apis/credentials

2. Select your **OAuth 2.0 Client ID**

3. **Add Authorized JavaScript Origins:**
   ```
   https://your-app.vercel.app
   ```

4. **Add Authorized Redirect URIs:**
   ```
   https://your-app.vercel.app/api/auth/callback/google
   ```

5. Click **"Save"**

### **GitHub OAuth Configuration**

1. Go to **GitHub Developer Settings**: https://github.com/settings/developers

2. Select your **OAuth App**

3. **Update Homepage URL:**
   ```
   https://your-app.vercel.app
   ```

4. **Update Authorization Callback URL:**
   ```
   https://your-app.vercel.app/api/auth/callback/github
   ```

5. Click **"Update application"**

---

## 🔧 Step 8: Update Backend CORS

Your backend needs to allow requests from your Vercel frontend.

1. Go to **Hugging Face Space** → **Settings** → **Variables and secrets**

2. **Update** `API_CORS_ORIGINS`:
   ```
   https://your-app.vercel.app,http://localhost:3000
   ```

3. **Update** `FRONTEND_URL`:
   ```
   https://your-app.vercel.app
   ```

4. **Restart** your Hugging Face Space:
   - Click **"Factory reboot"** in Space settings

---

## ✅ Step 9: Test Deployment

### Test 1: Homepage
Visit: `https://your-app.vercel.app`

**Expected:**
- ✓ Homepage loads with Hero section
- ✓ Features section displays
- ✓ Navigation works
- ✓ No console errors

### Test 2: Authentication
1. Click **"Login"** or **"Sign Up"**
2. Try email/password registration
3. Try Google OAuth login
4. Try GitHub OAuth login

**Expected:**
- ✓ Registration creates account
- ✓ Login redirects to dashboard
- ✓ OAuth flows work correctly
- ✓ Session persists on refresh

### Test 3: Support Portal
1. Login to your account
2. Go to **"Support"** page
3. Submit a test query
4. Watch for AI response streaming

**Expected:**
- ✓ Form submission works
- ✓ AI response streams in real-time
- ✓ Conversation history shows
- ✓ Ticket created successfully

### Test 4: Dashboard
1. Go to **"Dashboard"** page
2. Check stats and recent tickets

**Expected:**
- ✓ Dashboard loads
- ✓ Stats display correctly
- ✓ Recent tickets show
- ✓ Navigation works

### Test 5: Admin Portal
1. Go to `/admin/login`
2. Login with admin credentials
3. Check admin dashboard

**Expected:**
- ✓ Admin login works
- ✓ Admin dashboard loads
- ✓ Ticket management works
- ✓ Can respond to tickets

---

## 🔧 Troubleshooting

### ❌ Build Fails

**Problem**: Vercel build fails with errors

**Solutions:**
- Check build logs in Vercel dashboard
- Verify `package.json` scripts are correct
- Ensure all dependencies are in `package.json`
- Test build locally: `npm run build`
- Check for TypeScript errors: `npm run lint`

### ❌ Environment Variables Not Working

**Problem**: App can't connect to backend or database

**Solutions:**
- Verify all environment variables are set in Vercel
- Check variable names match exactly (case-sensitive)
- Ensure `NEXT_PUBLIC_*` prefix for client-side variables
- Redeploy after adding/updating variables
- Check browser console for actual values

### ❌ OAuth Login Fails

**Problem**: Google/GitHub login doesn't work

**Solutions:**
- Verify redirect URIs in Google/GitHub console
- Ensure URLs match exactly (no trailing slashes)
- Check OAuth credentials are correct in Vercel
- Clear browser cookies and try again
- Check browser console for error messages

### ❌ Backend API Calls Fail

**Problem**: Frontend can't reach backend

**Solutions:**
- Verify `NEXT_PUBLIC_BACKEND_URL` is correct
- Check backend CORS settings allow your frontend URL
- Test backend health: `curl https://backend-url/health`
- Check browser Network tab for actual errors
- Verify backend is running on Hugging Face

### ❌ Database Connection Issues

**Problem**: Better Auth or database queries fail

**Solutions:**
- Verify `DATABASE_URL` is correct
- Ensure Neon database is not sleeping
- Check Better Auth tables exist in database
- Run migrations if needed
- Test database connection locally

### ❌ SSE Streaming Not Working

**Problem**: AI responses don't stream

**Solutions:**
- Check backend `/channels/webform/message/stream` endpoint
- Verify backend is returning SSE events
- Check browser console for EventSource errors
- Test endpoint directly: `curl -N backend-url/api/v1/channels/webform/message/stream`
- Ensure no proxy/CDN is buffering responses

---

## 📊 Monitoring & Analytics

### Vercel Analytics (Built-in)

1. Go to **Project** → **Analytics** tab
2. View:
   - Page views
   - Unique visitors
   - Top pages
   - Performance metrics

### Vercel Speed Insights

1. Install package:
   ```bash
   npm install @vercel/speed-insights
   ```

2. Add to `app/layout.tsx`:
   ```tsx
   import { SpeedInsights } from '@vercel/speed-insights/next';
   
   export default function RootLayout({ children }) {
     return (
       <html>
         <body>
           {children}
           <SpeedInsights />
         </body>
       </html>
     );
   }
   ```

3. Redeploy to see real-time performance data

### Error Tracking (Optional)

**Sentry Integration:**
1. Sign up at https://sentry.io
2. Install: `npm install @sentry/nextjs`
3. Run: `npx @sentry/wizard@latest -i nextjs`
4. Follow setup wizard
5. Redeploy

---

## 💰 Cost & Limits

### Free Tier (Hobby)
- ✅ 100 GB bandwidth/month
- ✅ Unlimited deployments
- ✅ Automatic HTTPS
- ✅ Edge network (global CDN)
- ✅ Preview deployments for PRs
- ✅ 100 GB-hours serverless function execution
- ⚠️ 1 concurrent build

### Pro Tier ($20/month)
- ✅ 1 TB bandwidth/month
- ✅ 1000 GB-hours serverless execution
- ✅ 12 concurrent builds
- ✅ Advanced analytics
- ✅ Password protection
- ✅ Team collaboration

### Enterprise
- Custom pricing
- Dedicated support
- SLA guarantees
- Advanced security

---

## 🔄 Continuous Deployment

### Automatic Deployments

Vercel automatically deploys when you push to GitHub:

1. **Production Deployments** (main branch):
   ```bash
   git add .
   git commit -m "Update: feature description"
   git push origin main
   ```
   - Deploys to production URL
   - Runs all checks
   - Updates live site

2. **Preview Deployments** (other branches):
   ```bash
   git checkout -b feature/new-feature
   git add .
   git commit -m "Add: new feature"
   git push origin feature/new-feature
   ```
   - Creates preview URL
   - Unique URL for each branch
   - Perfect for testing before merge

3. **Pull Request Previews**:
   - Every PR gets a preview deployment
   - Comment on PR with preview URL
   - Test changes before merging

### Deployment Protection

Enable in **Project Settings** → **Git**:
- ✅ **Ignored Build Step**: Skip builds for specific paths
- ✅ **Build Command Override**: Custom build logic
- ✅ **Environment Variables**: Per-branch variables

---

## 🎨 Custom Domain (Optional)

### Add Custom Domain

1. Go to **Project Settings** → **Domains**

2. Click **"Add"**

3. Enter your domain: `custora.com`

4. **Configure DNS** (at your domain registrar):
   - **A Record**: `76.76.21.21`
   - **CNAME**: `cname.vercel-dns.com`

5. **Wait for verification** (5-10 minutes)

6. **Update environment variables**:
   - `NEXT_PUBLIC_APP_URL`: `https://custora.com`
   - `BETTER_AUTH_URL`: `https://custora.com`

7. **Update OAuth redirects** to use custom domain

8. **Redeploy** application

---

## 🔐 Security Best Practices

### Environment Variables
- ✅ Never commit `.env.local` to GitHub
- ✅ Use Vercel environment variables for secrets
- ✅ Rotate secrets regularly
- ✅ Use different secrets for dev/prod

### Headers
- ✅ Security headers configured in `vercel.json`
- ✅ CSP headers for XSS protection
- ✅ HSTS for HTTPS enforcement

### Authentication
- ✅ Use secure cookies (httpOnly, secure, sameSite)
- ✅ Implement rate limiting on API routes
- ✅ Validate JWT tokens on backend
- ✅ Use strong BETTER_AUTH_SECRET (32+ chars)

### Database
- ✅ Use connection pooling (Neon)
- ✅ Enable SSL for database connections
- ✅ Limit database access to specific IPs (optional)

---

## 📞 Support & Resources

### Documentation
- **Vercel Docs**: https://vercel.com/docs
- **Next.js Docs**: https://nextjs.org/docs
- **Better Auth Docs**: https://www.better-auth.com/docs

### Community
- **Vercel Discord**: https://vercel.com/discord
- **Next.js Discord**: https://nextjs.org/discord
- **GitHub Discussions**: Your repository

### Vercel Support
- **Email**: support@vercel.com
- **Twitter**: @vercel
- **Status Page**: https://www.vercel-status.com

---

## ✅ Deployment Checklist

Before going live:

- [ ] Vercel account created
- [ ] Project imported from GitHub
- [ ] Root directory set to `frontend/customer-support-form`
- [ ] All environment variables added
- [ ] First deployment successful
- [ ] Environment variables updated with actual URLs
- [ ] OAuth redirect URIs updated
- [ ] Backend CORS configured
- [ ] Homepage loads correctly
- [ ] Authentication works (email + OAuth)
- [ ] Support portal functional
- [ ] AI responses streaming
- [ ] Dashboard displays data
- [ ] Admin portal accessible
- [ ] Custom domain configured (optional)
- [ ] Analytics enabled
- [ ] Error tracking set up (optional)

---

## 🎉 Next Steps

After frontend is deployed:

1. **Test End-to-End Flow**:
   - User registration → Login → Support query → AI response → Ticket creation

2. **Configure GitHub Actions** (Phase 3):
   - Automated testing
   - Automated deployments
   - CI/CD pipeline

3. **Monitor Performance**:
   - Check Vercel Analytics
   - Monitor error rates
   - Track user engagement

4. **Optimize**:
   - Enable image optimization
   - Add caching strategies
   - Optimize bundle size

5. **Scale**:
   - Upgrade to Pro if needed
   - Add custom domain
   - Enable advanced features

---

**Your frontend is now live on Vercel! 🎨**

**Production URLs:**
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-username-custora-backend.hf.space`
- API Docs: `https://your-username-custora-backend.hf.space/docs`
