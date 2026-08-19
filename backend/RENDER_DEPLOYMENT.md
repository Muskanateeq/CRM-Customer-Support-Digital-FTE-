# Deploy Backend to Render

Complete guide to deploy your Custora FastAPI backend to Render.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **Database**: PostgreSQL database (Neon or Render PostgreSQL)
4. **OpenAI API Key**: Get from [platform.openai.com](https://platform.openai.com)

---

## 🚀 Deployment Methods

### Method 1: Using render.yaml (Recommended)

This method uses Infrastructure as Code for automated setup.

#### Step 1: Prepare the Repository

```bash
cd backend

# Ensure render.yaml is in your backend directory
# It's already created for you!

# Commit and push
git add render.yaml RENDER_DEPLOYMENT.md
git commit -m "Add Render deployment configuration"
git push origin main
```

#### Step 2: Connect to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Select your repository
5. Render will detect `render.yaml` automatically
6. Click **"Apply"**

#### Step 3: Configure Environment Secrets

After deployment starts, go to your service settings and add these **secret** environment variables:

**Required Secrets:**
```bash
DATABASE_URL=postgresql://user:password@host:5432/database
POSTGRES_HOST=your-db-host.neon.tech
POSTGRES_DB=custora
POSTGRES_USER=your-user
POSTGRES_PASSWORD=your-password
OPENAI_API_KEY=sk-your-openai-key
BETTER_AUTH_SECRET=your-secret-min-32-chars-long
BETTER_AUTH_URL=https://your-frontend.vercel.app
```

**Update CORS Origins:**
```bash
API_CORS_ORIGINS=https://your-frontend.vercel.app,https://www.your-domain.com
```

---

### Method 2: Manual Deployment (Alternative)

If you prefer manual setup through the Render dashboard:

#### Step 1: Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository and branch

#### Step 2: Configure Service

**Basic Settings:**
- **Name**: `custora-backend` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: `backend` (important!)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

**Advanced Settings:**
- **Health Check Path**: `/health`
- **Plan**: Free (for testing) or Starter (for production)

#### Step 3: Add Environment Variables

Click **"Environment"** tab and add all variables from the **Method 1, Step 3** above.

---

## 🗄️ Database Options

### Option A: Use Existing Neon Database

If you already have a Neon PostgreSQL database:

1. Get your connection string from Neon dashboard
2. Add to Render environment variables:
   ```bash
   DATABASE_URL=postgresql://user:password@host.neon.tech:5432/database
   POSTGRES_HOST=your-host.neon.tech
   POSTGRES_PORT=5432
   POSTGRES_DB=custora
   POSTGRES_USER=your-user
   POSTGRES_PASSWORD=your-password
   ```

### Option B: Create Render PostgreSQL Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Choose a name: `custora-db`
3. Select region (same as your web service)
4. Choose plan (Free for testing)
5. Click **"Create Database"**

**Connect to Web Service:**
1. Go to your web service settings
2. Click **"Environment"**
3. Click **"Add from Database"**
4. Select your `custora-db`
5. Render will automatically add `DATABASE_URL`

---

## 🔒 Security Checklist

Before going live, ensure:

- [ ] All secrets are added as **environment variables** (not in code)
- [ ] `ENVIRONMENT=production` is set
- [ ] CORS origins are set to your actual frontend URLs
- [ ] `BETTER_AUTH_SECRET` is a strong random string (32+ chars)
- [ ] Database credentials are secure
- [ ] OpenAI API key has usage limits set

---

## ✅ Verify Deployment

### 1. Check Service Status

In Render Dashboard:
- Service should show **"Live"** status (green)
- Check logs for any errors

### 2. Test Health Endpoint

```bash
# Replace with your Render URL
curl https://custora-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "production",
  "timestamp": "2024-...",
  "database": "connected"
}
```

### 3. Test API Documentation

Visit in browser:
```
https://custora-backend.onrender.com/docs
```

You should see the Swagger UI with all API endpoints.

### 4. Test a Simple Endpoint

```bash
curl https://custora-backend.onrender.com/
```

---

## 🔗 Connect Frontend to Backend

Update your Vercel frontend environment variables:

```bash
# In Vercel Dashboard → Your Project → Settings → Environment Variables
NEXT_PUBLIC_API_URL=https://custora-backend.onrender.com
VITE_API_URL=https://custora-backend.onrender.com
```

Update CORS in backend:
```bash
# In Render → Environment Variables
API_CORS_ORIGINS=https://your-frontend.vercel.app,https://custora-backend.onrender.com
```

---

## 📊 Monitoring & Logs

### View Logs

In Render Dashboard:
1. Go to your service
2. Click **"Logs"** tab
3. Real-time logs will appear

### Common Log Commands

```bash
# Filter by level
# In Render logs, search for:
ERROR
WARNING
INFO
```

### Health Checks

Render automatically:
- Pings `/health` endpoint every 60 seconds
- Restarts service if health check fails 3 times
- Shows health status in dashboard

---

## 🐛 Troubleshooting

### Issue: Service Won't Start

**Check:**
1. Build logs for dependency errors
2. Ensure `requirements.txt` has all dependencies
3. Verify Python version compatibility

**Solution:**
```bash
# Add Python version to render.yaml or environment
PYTHON_VERSION=3.11.0
```

### Issue: Database Connection Failed

**Check:**
1. `DATABASE_URL` format is correct
2. Database allows connections from Render IPs
3. Credentials are correct

**Solution for Neon:**
1. Go to Neon dashboard
2. Check "IP Allow" settings
3. Allow all IPs or add Render's IP ranges

### Issue: CORS Errors

**Check:**
1. `API_CORS_ORIGINS` includes your frontend URL
2. No trailing slashes in URLs
3. Protocol matches (https/http)

**Solution:**
```bash
API_CORS_ORIGINS=https://your-frontend.vercel.app,https://www.your-domain.com
```

### Issue: 502 Bad Gateway

**Possible Causes:**
1. Service is starting up (wait 2-3 minutes)
2. Health check is failing
3. Application crashed

**Solution:**
1. Check logs for Python errors
2. Verify start command is correct
3. Test locally first: `uvicorn src.api.main:app --host 0.0.0.0 --port 8000`

---

## 💰 Pricing

### Free Tier
- 750 hours/month of free runtime
- Service sleeps after 15 minutes of inactivity
- Cold start: 30-60 seconds

### Starter ($7/month)
- Always on (no sleep)
- Faster performance
- Better for production

### Database
- Free PostgreSQL: 256MB storage, expires after 90 days
- Starter ($7/month): 1GB storage, retained

---

## 🚀 Production Best Practices

1. **Use Starter Plan or Higher**
   - Free tier sleeps, causing slow first requests
   - Production apps need "always on"

2. **Set Up Custom Domain**
   - In Render Dashboard → Settings → Custom Domain
   - Add your domain (e.g., `api.custora.com`)
   - Update DNS with provided CNAME

3. **Enable Auto-Deploy**
   - Render can auto-deploy on git push
   - Settings → Auto-Deploy → Enable

4. **Set Up Notifications**
   - Settings → Notifications
   - Get alerts for deploy failures

5. **Monitor Performance**
   - Use Render's built-in metrics
   - Consider adding Sentry for error tracking

---

## 📝 Deployment Checklist

Before going live:

- [ ] Code pushed to GitHub
- [ ] `render.yaml` committed
- [ ] Render service created
- [ ] All environment variables set
- [ ] Database connected and tested
- [ ] Health endpoint returns 200
- [ ] API docs accessible at `/docs`
- [ ] CORS configured for frontend domain
- [ ] Frontend connected to backend URL
- [ ] Test end-to-end flow works
- [ ] Logs show no errors
- [ ] Consider upgrading to paid plan for production

---

## 🔄 Updating Your Deployment

### Automatic Updates

If auto-deploy is enabled:
```bash
git add .
git commit -m "Update backend"
git push origin main
# Render will automatically deploy
```

### Manual Deploy

In Render Dashboard:
1. Go to your service
2. Click **"Manual Deploy"**
3. Select branch
4. Click **"Deploy"**

---

## 📞 Need Help?

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Your Backend Logs**: Check Render Dashboard → Logs tab

---

## 🎉 You're Done!

Your backend should now be live at:
```
https://custora-backend.onrender.com
```

Test it and connect your frontend!
