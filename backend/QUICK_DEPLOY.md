# Quick Start: Deploy Backend to Render in 10 Minutes

## 🚀 Fast Track Deployment

### Step 1: Push to GitHub (if not already done)
```bash
cd D:\Hackathon5
git add backend/render.yaml backend/RENDER_DEPLOYMENT.md
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Create Render Account & Connect GitHub
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Deploy from Blueprint
1. Click **"New +"** → **"Blueprint"**
2. Select your repository
3. Render detects `backend/render.yaml`
4. Click **"Apply"**

### Step 4: Add Secrets (Critical!)

Go to your service → **Environment** tab → Add these:

**Required Secrets:**
```bash
# Database (from Neon dashboard)
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/custora?sslmode=require
POSTGRES_HOST=ep-xxx.neon.tech
POSTGRES_DB=custora
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# OpenAI (from platform.openai.com)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Auth Secret (generate random 32+ chars)
BETTER_AUTH_SECRET=<generate-and-store-in-dashboard>

# Frontend URL (from Vercel)
BETTER_AUTH_URL=https://your-frontend-app.vercel.app
API_CORS_ORIGINS=https://your-frontend-app.vercel.app,http://localhost:3000
```

### Step 5: Update Frontend Environment Variables

In Vercel Dashboard:
1. Go to your project → Settings → Environment Variables
2. Add:
```bash
NEXT_PUBLIC_API_URL=https://custora-backend.onrender.com
# or
VITE_API_URL=https://custora-backend.onrender.com
```
3. Redeploy frontend

### Step 6: Test Your Deployment

```bash
# Test health endpoint
curl https://your-service-name.onrender.com/health

# Expected response:
# {"status":"healthy","environment":"production","timestamp":"..."}
```

---

## 📋 Where to Get Your Credentials

### Database URL (Neon)
1. Go to https://console.neon.tech
2. Select your project
3. Click **"Connection Details"**
4. Copy the connection string
5. Format: `postgresql://user:password@host.neon.tech/dbname?sslmode=require`

### OpenAI API Key
1. Go to https://platform.openai.com
2. Click your profile → **"API Keys"**
3. Click **"Create new secret key"**
4. Copy and save (you won't see it again!)

### Frontend URL (Vercel)
1. Go to https://vercel.com/dashboard
2. Click your project
3. Copy the **"Domains"** URL
4. Usually: `https://your-project-name.vercel.app`

### Generate Auth Secret
```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32

# Or use: https://generate-secret.vercel.app
```

---

## 🔧 Alternative: Manual Deployment

If Blueprint doesn't work:

1. **New Web Service**
   - Dashboard → New + → Web Service
   - Connect repository
   - Root Directory: `backend`

2. **Configure**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

3. **Add all environment variables from Step 4 above**

---

## ⚠️ Common Issues & Fixes

### Issue: Build Fails
**Solution:** Check requirements.txt has no syntax errors
```bash
# Test locally first
cd backend
pip install -r requirements.txt
```

### Issue: Database Connection Fails
**Solution:** Ensure DATABASE_URL includes `?sslmode=require` for Neon
```bash
DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
```

### Issue: Service Crashes After Deploy
**Solution:** Check logs in Render dashboard
- Look for missing environment variables
- Verify all secrets are set

### Issue: CORS Error from Frontend
**Solution:** Update CORS origins
```bash
API_CORS_ORIGINS=https://your-frontend.vercel.app
# No trailing slash!
# Include https:// protocol!
```

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Service deployed via Blueprint or Manual
- [ ] All environment variables added (especially secrets)
- [ ] Service shows "Live" (green status)
- [ ] Health endpoint returns 200: `/health`
- [ ] Docs accessible: `/docs`
- [ ] Frontend updated with backend URL
- [ ] Test end-to-end: frontend → backend → database

---

## 🎯 Your URLs After Deployment

```bash
# Backend API
https://custora-backend.onrender.com

# API Documentation
https://custora-backend.onrender.com/docs

# Health Check
https://custora-backend.onrender.com/health

# Frontend (Vercel)
https://your-frontend.vercel.app
```

---

## 💡 Pro Tips

1. **Free Tier Sleeps:** Service sleeps after 15 min inactivity (30-60s cold start)
   - Upgrade to Starter ($7/mo) for production

2. **Auto-Deploy:** Enable in Settings to auto-deploy on git push

3. **Custom Domain:** Settings → Custom Domain → Add your domain

4. **Monitor Logs:** Dashboard → Logs tab for real-time debugging

5. **Database Backups:** Use Neon's backup feature or Render PostgreSQL

---

## 🚨 Before Going to Production

- [ ] Upgrade to paid plan (no sleep)
- [ ] Set up custom domain
- [ ] Enable auto-deploy
- [ ] Set up monitoring/alerts
- [ ] Test all API endpoints
- [ ] Load test with expected traffic
- [ ] Set OpenAI usage limits
- [ ] Review security settings

---

## 📞 Support

- **Render Docs:** https://render.com/docs/deploy-fastapi
- **Issue?** Check logs in Render Dashboard
- **CORS Issues?** Verify frontend URL in API_CORS_ORIGINS

---

**Estimated Time:** 10-15 minutes
**Cost:** Free tier available, $7/mo for production
