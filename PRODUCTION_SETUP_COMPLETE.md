# 🎯 FINAL PRODUCTION SETUP
# Your Exact URLs and Configuration

## Your URLs:
- **Frontend (Vercel)**: https://custora-tau.vercel.app
- **Backend (Render)**: https://crm-customer-support-digital-fte.onrender.com

---

## ✅ STEP 1: Update Vercel Environment Variables

Go to: **https://vercel.com/dashboard** → **Your Project** → **Settings** → **Environment Variables**

### Add/Update These Variables:

```bash
# Backend URL
NEXT_PUBLIC_BACKEND_URL=https://crm-customer-support-digital-fte.onrender.com

# App URL (Your Vercel URL)
NEXT_PUBLIC_APP_URL=https://custora-tau.vercel.app

# Better Auth URL (Same as App URL)
BETTER_AUTH_URL=https://custora-tau.vercel.app

# Database (Keep same)
DATABASE_URL=<set-in-vercel-dashboard-only>

# Better Auth Secret (Keep same)
BETTER_AUTH_SECRET=<set-in-vercel-dashboard-only>

# OAuth Credentials (Keep your existing values from .env.local)
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
GITHUB_CLIENT_ID=<your-github-client-id>
GITHUB_CLIENT_SECRET=<your-github-client-secret>
```

**Important:** 
- Select **"Production, Preview, and Development"** for all variables
- Click **"Save"**

### After Saving:
1. Go to **"Deployments"** tab
2. Click **"Redeploy"** on the latest deployment
3. Wait 2-3 minutes for deployment to complete

---

## ✅ STEP 2: Update Render Environment Variables

Go to: **https://dashboard.render.com** → **crm-customer-support-digital-fte** → **Environment** tab

### Add/Update These Variables:

```bash
# CORS Origins (CRITICAL!)
API_CORS_ORIGINS=https://custora-tau.vercel.app,http://localhost:3000

# Better Auth URL
BETTER_AUTH_URL=https://custora-tau.vercel.app

# Frontend URL
FRONTEND_URL=https://custora-tau.vercel.app

# Environment
ENVIRONMENT=production
PYTHON_VERSION=3.11.0

# Database (Your Neon credentials)
DATABASE_URL=<set-in-render-dashboard-only>
POSTGRES_HOST=ep-lively-heart-aimqvdi0-pooler.c-4.us-east-1.aws.neon.tech
POSTGRES_PORT=5432
POSTGRES_DB=neondb
POSTGRES_USER=neondb_owner
POSTGRES_PASSWORD=<set-in-render-dashboard-only>
PROJECT_ID=ep-lively-heart-aimqvdi0

# OpenAI
OPENAI_API_KEY=<your-openai-key>
AGENT_MODEL=gpt-4o

# Auth Secret
BETTER_AUTH_SECRET=<set-in-render-dashboard-only>

# API Settings
API_HOST=0.0.0.0
LOG_LEVEL=INFO

# Channels
WEBFORM_ENABLED=true
GMAIL_ENABLED=false
WHATSAPP_ENABLED=false
KAFKA_ENABLED=false

# Pool Settings
DB_POOL_MIN_SIZE=2
DB_POOL_MAX_SIZE=10
```

**After Updating:**
- Click **"Save Changes"**
- Service will automatically restart (wait 60 seconds)

---

## ✅ STEP 3: Test Your Deployment

### A. Test Backend Health

```bash
curl https://crm-customer-support-digital-fte.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "environment": "production",
  "timestamp": "2026-08-19T...",
  "database": "connected"
}
```

### B. Test Backend API Documentation

Open in browser:
```
https://crm-customer-support-digital-fte.onrender.com/docs
```

You should see Swagger UI with all API endpoints.

### C. Test Frontend

1. Open: **https://custora-tau.vercel.app**
2. Fill out the support form
3. Click Submit
4. Check if:
   - Form submits successfully
   - No CORS errors in browser console (F12)
   - Data reaches backend

### D. Check for CORS Errors

Open browser console (F12) → Network tab:
- Should NOT see: `"blocked by CORS policy"`
- All API calls should return 200 status

---

## 🔍 Troubleshooting

### If You See CORS Error:

**Error**: "Access blocked by CORS policy"

**Fix:**
1. Go to Render → Environment
2. Double-check `API_CORS_ORIGINS` is exactly:
   ```
   https://custora-tau.vercel.app,http://localhost:3000
   ```
3. No trailing slash on URLs
4. Must start with `https://`
5. Save and wait 60 seconds

### If Backend Returns 502:

**Causes:**
- Backend is cold starting (free tier sleeps after 15 min)
- First request takes 30-60 seconds

**Fix:**
- Wait 60 seconds and try again
- Check Render logs for errors

### If Environment Variables Don't Work:

**Vercel:**
- Must redeploy after changing env vars
- Go to Deployments → Redeploy

**Render:**
- Service auto-restarts after saving
- Wait 60 seconds before testing

---

## 📋 Final Checklist

- [ ] Vercel env vars updated
- [ ] Frontend redeployed on Vercel
- [ ] Render CORS origins set to `https://custora-tau.vercel.app`
- [ ] Render Better Auth URL set to `https://custora-tau.vercel.app`
- [ ] Render service restarted (automatic)
- [ ] Backend health check returns 200
- [ ] Backend docs accessible
- [ ] Frontend loads without errors
- [ ] Form submission works end-to-end
- [ ] No CORS errors in browser console

---

## 🎯 Your Complete Setup

```bash
# Frontend (Vercel)
App: https://custora-tau.vercel.app
Dashboard: https://vercel.com/dashboard

# Backend (Render)
API: https://crm-customer-support-digital-fte.onrender.com
Health: https://crm-customer-support-digital-fte.onrender.com/health
Docs: https://crm-customer-support-digital-fte.onrender.com/docs
Dashboard: https://dashboard.render.com

# Database (Neon)
Host: ep-lively-heart-aimqvdi0-pooler.c-4.us-east-1.aws.neon.tech
Database: neondb
Dashboard: https://console.neon.tech
```

---

## 🚀 Quick Commands

```bash
# Test backend health
curl https://crm-customer-support-digital-fte.onrender.com/health

# Test backend root
curl https://crm-customer-support-digital-fte.onrender.com/

# Open frontend
open https://custora-tau.vercel.app

# Test CORS (from browser console F12)
fetch('https://crm-customer-support-digital-fte.onrender.com/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

---

## 💡 Important Notes

1. **Free Tier Sleep:**
   - Render free tier sleeps after 15 min of inactivity
   - First request after sleep takes 30-60 seconds
   - Consider upgrading to Starter ($7/mo) for production

2. **CORS Must Match Exactly:**
   - Backend CORS: `https://custora-tau.vercel.app`
   - Frontend URL: `https://custora-tau.vercel.app`
   - Must be identical (no trailing slash)

3. **Environment Variables:**
   - Vercel: Need to redeploy after changes
   - Render: Auto-restart after save (wait 60 sec)

4. **Logs:**
   - Vercel: Deployments → Click deployment → Function Logs
   - Render: Dashboard → Logs tab (real-time)

---

**Status**: Ready for Production ✅
**Time**: 5-10 minutes to complete setup
