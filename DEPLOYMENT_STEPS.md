# 🚀 PRODUCTION DEPLOYMENT - CHANGES REQUIRED

Your Backend URL: `https://crm-customer-support-digital-fte.onrender.com`
Your Frontend URL: `https://custora.vercel.app` (check your Vercel dashboard)

---

## ✅ STEP 1: Frontend Changes (Vercel)

### A. Push Updated vercel.json (DONE ✓)

File `frontend/customer-support-form/vercel.json` has been updated with your Render backend URL.

**Commit and push:**
```bash
git add frontend/customer-support-form/vercel.json
git commit -m "Update backend URL to Render"
git push origin main
```

### B. Update Vercel Environment Variables

Go to: **https://vercel.com/dashboard** → **Your Project** → **Settings** → **Environment Variables**

**Update/Add these variables:**

```bash
# Backend URL (Your Render URL)
NEXT_PUBLIC_BACKEND_URL=https://crm-customer-support-digital-fte.onrender.com

# App URL (Your Vercel URL - get from Vercel Domains tab)
NEXT_PUBLIC_APP_URL=https://custora.vercel.app

# Better Auth URL (Same as App URL)
BETTER_AUTH_URL=https://custora.vercel.app

# Database (Keep same as before)
DATABASE_URL=postgresql://neondb_owner:<redacted-neon-password>@ep-lively-heart-aimqvdi0-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require

# Better Auth Secret (Keep same)
BETTER_AUTH_SECRET=<generate-and-store-in-dashboard>

# OAuth (Keep your existing values from .env.local)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

**Important**: Select **"Production, Preview, and Development"** for all environments

### C. Redeploy Frontend

After updating environment variables and pushing code:

1. Vercel will auto-deploy when you push to main
2. OR manually: **Deployments** tab → Click **"Redeploy"** on latest
3. Wait 2-3 minutes

---

## ✅ STEP 2: Backend Changes (Render)

Go to: **https://dashboard.render.com** → **Your Service** → **Environment** tab

### Update These Environment Variables:

#### 1. CORS Origins (CRITICAL!)

```bash
API_CORS_ORIGINS=https://custora.vercel.app,http://localhost:3000
```

⚠️ **Replace `custora.vercel.app` with your actual Vercel domain**

To get your Vercel domain:
- Go to Vercel Dashboard → Your Project → **Domains** tab
- Copy the URL (e.g., `https://your-project-name.vercel.app`)

#### 2. Better Auth URL

```bash
BETTER_AUTH_URL=https://custora.vercel.app
```

#### 3. Frontend URL

```bash
FRONTEND_URL=https://custora.vercel.app
```

#### 4. Verify All Required Vars Are Set

Make sure these exist in Render:

```bash
# Environment
ENVIRONMENT=production
PYTHON_VERSION=3.11.0

# Database (from your Neon)
DATABASE_URL=postgresql://neondb_owner:<redacted-neon-password>@ep-lively-heart-aimqvdi0-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require
POSTGRES_HOST=ep-lively-heart-aimqvdi0-pooler.c-4.us-east-1.aws.neon.tech
POSTGRES_PORT=5432
POSTGRES_DB=neondb
POSTGRES_USER=neondb_owner
POSTGRES_PASSWORD=<redacted-neon-password>
PROJECT_ID=ep-lively-heart-aimqvdi0

# OpenAI
OPENAI_API_KEY=your-openai-key
AGENT_MODEL=gpt-4o

# Auth
BETTER_AUTH_SECRET=<generate-and-store-in-dashboard>

# Channels
WEBFORM_ENABLED=true
GMAIL_ENABLED=false
WHATSAPP_ENABLED=false
KAFKA_ENABLED=false

# API
API_HOST=0.0.0.0
LOG_LEVEL=INFO
```

#### 5. Save Changes

Click **"Save Changes"** → Service will restart automatically (30-60 seconds)

---

## ✅ STEP 3: Test Your Deployment

### A. Test Backend Health

```bash
curl https://crm-customer-support-digital-fte.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "production",
  "timestamp": "...",
  "database": "connected"
}
```

### B. Test Backend API Docs

Open in browser:
```
https://crm-customer-support-digital-fte.onrender.com/docs
```

Should show Swagger UI with all endpoints

### C. Test Frontend

1. Open your Vercel URL: `https://custora.vercel.app`
2. Try submitting a support form
3. Check browser console (F12) for errors
4. Verify data reaches backend

---

## 🔍 Quick Troubleshooting

### Issue: CORS Error

If you see: `"blocked by CORS policy"`

**Fix:**
1. Go to Render → Environment
2. Update `API_CORS_ORIGINS` with your exact Vercel URL
3. Must include `https://`
4. No trailing slash
5. Save and wait 60 seconds

### Issue: 502 Bad Gateway

**Causes:**
- Backend is cold starting (wait 30-60 seconds on free tier)
- Backend crashed (check Render logs)

**Fix:**
1. Render Dashboard → Logs tab
2. Look for errors
3. Verify all environment variables are set

### Issue: Frontend Can't Connect to Backend

**Check:**
1. `vercel.json` has correct backend URL
2. Environment variables updated in Vercel
3. Frontend redeployed after changes

---

## 📋 Quick Checklist

- [ ] `vercel.json` updated with Render URL
- [ ] Git committed and pushed
- [ ] Vercel env vars updated
- [ ] Frontend redeployed (automatic on push)
- [ ] Render CORS origins set to Vercel URL
- [ ] Render Better Auth URL set to Vercel URL
- [ ] Backend restarted (automatic on save)
- [ ] Test backend health: `curl https://crm-customer-support-digital-fte.onrender.com/health`
- [ ] Test frontend form submission
- [ ] Check logs for errors

---

## 🎯 Your Final URLs

```bash
# Frontend (Vercel)
App: https://custora.vercel.app  # ← Check your actual URL
API Proxy: https://custora.vercel.app/api/backend/*

# Backend (Render)
API: https://crm-customer-support-digital-fte.onrender.com
Health: https://crm-customer-support-digital-fte.onrender.com/health
Docs: https://crm-customer-support-digital-fte.onrender.com/docs

# Database (Neon)
Host: ep-lively-heart-aimqvdi0-pooler.c-4.us-east-1.aws.neon.tech
```

---

## 🚀 What to Do RIGHT NOW

1. **Get Your Vercel URL:**
   - Go to: https://vercel.com/dashboard
   - Click your project
   - Go to **Domains** tab
   - Copy the URL (e.g., `https://custora-abc123.vercel.app`)

2. **Push Code:**
   ```bash
   cd D:/Hackathon5
   git add frontend/customer-support-form/vercel.json
   git commit -m "Update backend URL to Render"
   git push origin main
   ```

3. **Update Vercel Environment Variables:**
   - Go to Vercel Settings → Environment Variables
   - Update `NEXT_PUBLIC_BACKEND_URL`, `NEXT_PUBLIC_APP_URL`, `BETTER_AUTH_URL`
   - Click **Save**

4. **Update Render Environment Variables:**
   - Go to Render Dashboard → Environment
   - Update `API_CORS_ORIGINS`, `BETTER_AUTH_URL`, `FRONTEND_URL`
   - Click **Save Changes**

5. **Test:**
   ```bash
   curl https://crm-customer-support-digital-fte.onrender.com/health
   ```

---

**Estimated Time:** 5-10 minutes
**Next Step:** Push code and update environment variables!
