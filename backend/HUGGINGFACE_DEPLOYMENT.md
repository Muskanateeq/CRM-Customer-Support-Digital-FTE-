# 🚀 Custora Backend - Hugging Face Spaces Deployment Guide

Complete step-by-step guide to deploy your FastAPI backend to Hugging Face Spaces (FREE tier).

---

## 📋 Prerequisites

- ✅ Hugging Face account (free)
- ✅ GitHub repository with backend code
- ✅ Neon PostgreSQL database (already configured)
- ✅ API keys (OpenAI, Groq, Twilio)

---

## 🎯 Step 1: Create Hugging Face Account

1. Go to **https://huggingface.co/join**
2. Sign up with email or GitHub
3. Verify your email address
4. Complete profile setup

---

## 🏗️ Step 2: Create New Space

1. Click your profile picture → **"New Space"**

2. **Configure Space:**
   - **Owner**: Your username
   - **Space name**: `custora-backend` (or any name you prefer)
   - **License**: Apache 2.0
   - **Select the Space SDK**: **Docker** ⚠️ **CRITICAL - Must select Docker!**
   - **Space hardware**: CPU basic - 2 vCPU, 16 GB RAM (FREE)
   - **Space visibility**: Public (required for free tier)

3. Click **"Create Space"**

---

## 🔗 Step 3: Connect GitHub Repository

### Option A: Direct Git Push (Recommended)

1. In your Space, go to **"Files and versions"** tab
2. You'll see git clone instructions like:
   ```bash
   git clone https://huggingface.co/spaces/YOUR-USERNAME/custora-backend
   ```

3. **Add Hugging Face as remote** (run in your project root):
   ```bash
   cd D:\Hackathon5
   git remote add hf https://huggingface.co/spaces/YOUR-USERNAME/custora-backend
   ```

4. **Push backend folder** (first time setup):
   ```bash
   # Create a temporary branch with only backend files
   git subtree push --prefix=backend hf main
   ```

### Option B: GitHub Sync (Alternative)

1. In Space settings → **"Repository"**
2. Click **"Connect to GitHub"**
3. Authorize Hugging Face
4. Select repository: `Hackathon5`
5. **Branch**: `main`
6. **Path in repo**: `backend` ⚠️ **IMPORTANT!**
7. Save settings

---

## 🔐 Step 4: Add Environment Variables

Go to your Space → **Settings** → **"Variables and secrets"** → **"New secret"**

Add each variable one by one:

### **Database (Neon PostgreSQL)**
```bash
DATABASE_URL
YOUR_DATABASE_URL_HERE

POSTGRES_HOST
ep-lively-heart-aimqvdi0-pooler.c-4.us-east-1.aws.neon.tech

POSTGRES_DB
neondb

POSTGRES_USER
neondb_owner

POSTGRES_PASSWORD
npg_6pbM0ZLOvNYm

POSTGRES_PORT
5432
```

### **OpenAI (for embeddings)**
```bash
OPENAI_API_KEY
sk-proj-YOUR_KEY_HERE
```

### **Groq (for AI agent)**
```bash
USE_GROQ
true

GROQ_API_KEY
YOUR_GROQ_KEY_HERE
```

### **Application Settings**
```bash
ENVIRONMENT
production

LOG_LEVEL
INFO

API_HOST
0.0.0.0

API_PORT
7860
```

### **Channel Configuration**
```bash
KAFKA_ENABLED
false

GMAIL_ENABLED
true

WHATSAPP_ENABLED
true

WEBFORM_ENABLED
true
```

### **Agent Configuration**
```bash
AGENT_MODEL
gpt-4o

AGENT_TEMPERATURE
0.7

AGENT_MAX_TOKENS
1000

AGENT_TIMEOUT_SECONDS
30
```

### **Gmail Integration (if enabled)**
```bash
GMAIL_ADDRESS
your_support_email@gmail.com

ADMIN_EMAIL
your_admin_email@gmail.com

GMAIL_CREDENTIALS_JSON
{"installed":{"client_id":"YOUR_CLIENT_ID","project_id":"YOUR_PROJECT","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"YOUR_SECRET","redirect_uris":["http://localhost"]}}

GMAIL_TOKEN_JSON
{"token":"YOUR_TOKEN","refresh_token":"YOUR_REFRESH_TOKEN","token_uri":"https://oauth2.googleapis.com/token","client_id":"YOUR_CLIENT_ID","client_secret":"YOUR_SECRET","scopes":["https://www.googleapis.com/auth/gmail.modify"],"expiry":"2026-04-26T00:00:00.000000Z"}
```

### **Twilio WhatsApp (if enabled)**
```bash
TWILIO_ACCOUNT_SID
YOUR_ACCOUNT_SID

TWILIO_AUTH_TOKEN
YOUR_AUTH_TOKEN

TWILIO_WHATSAPP_NUMBER
whatsapp:+14155238886
```

### **Better Auth (for JWT validation)**
```bash
BETTER_AUTH_SECRET
YzYuynKxZ5ch2RNZCXMusrwMscgZ95df

BETTER_AUTH_URL
https://your-frontend.vercel.app
```

### **Frontend URL (for CORS)**
```bash
FRONTEND_URL
https://your-frontend.vercel.app

API_CORS_ORIGINS
https://your-frontend.vercel.app,http://localhost:3000
```

---

## 🚀 Step 5: Deploy

### Automatic Deployment

1. **Push code to GitHub** (if using GitHub sync):
   ```bash
   git add backend/Dockerfile backend/.dockerignore
   git commit -m "Add Hugging Face deployment files"
   git push origin main
   ```

2. **Or push directly to Hugging Face**:
   ```bash
   git subtree push --prefix=backend hf main
   ```

3. **Monitor build**:
   - Go to your Space → **"Logs"** tab
   - Watch the Docker build process (5-10 minutes)
   - Build stages:
     - ✓ Pulling base image
     - ✓ Installing system dependencies
     - ✓ Installing Python packages
     - ✓ Copying application code
     - ✓ Starting application

4. **Wait for "Running"** status in Space header

---

## 🌐 Step 6: Get Your Backend URL

Once deployed, your backend will be available at:

```
https://YOUR-USERNAME-custora-backend.hf.space
```

Example:
```
https://muskanateeq-custora-backend.hf.space
```

**Save this URL** - you'll need it for frontend configuration!

---

## ✅ Step 7: Test Deployment

### Test 1: Health Check
```bash
curl https://YOUR-USERNAME-custora-backend.hf.space/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-25T12:00:00.000000Z",
  "database": "connected",
  "version": "2.0.0"
}
```

### Test 2: API Documentation
Visit in browser:
```
https://YOUR-USERNAME-custora-backend.hf.space/docs
```

You should see Swagger UI with all API endpoints.

### Test 3: Database Connection
```bash
curl https://YOUR-USERNAME-custora-backend.hf.space/ready
```

**Expected Response:**
```json
{
  "status": "ready",
  "database": "connected",
  "channels": {
    "webform": "enabled",
    "email": "enabled",
    "whatsapp": "enabled"
  }
}
```

---

## 🗄️ Step 8: Initialize Database (One-time)

After first deployment, initialize the database:

### Option A: Run Locally (Recommended)

```bash
cd D:\Hackathon5\backend

# Setup pgvector extension
python scripts/setup_pgvector.py

# Populate knowledge base
python scripts/populate_knowledge_base.py
```

These scripts connect to your Neon database remotely.

### Option B: Using Hugging Face Terminal (if available)

Some Spaces have terminal access:
1. Go to Space → **"Files"** tab
2. Click **"Terminal"** button
3. Run:
   ```bash
   python scripts/setup_pgvector.py
   python scripts/populate_knowledge_base.py
   ```

---

## 🔧 Troubleshooting

### ❌ Build Fails

**Problem**: Docker build fails with errors

**Solutions**:
- Check Dockerfile syntax
- Verify all files are committed to GitHub
- Review build logs in Space → Logs tab
- Ensure `backend/` folder structure is correct

### ❌ App Crashes on Startup

**Problem**: App starts but immediately crashes

**Solutions**:
- Verify ALL environment variables are set in Space settings
- Check database connection string (must include `?sslmode=require`)
- Review application logs in Space
- Test database connection: `python scripts/wake_database.py`

### ❌ Database Connection Timeout

**Problem**: "Connection timeout" or "Database unavailable"

**Solutions**:
- Neon database may be sleeping - run `wake_database.py` locally
- Verify connection string is correct
- Check Neon dashboard for database status
- Ensure Neon project is not suspended

### ❌ CORS Errors from Frontend

**Problem**: Frontend can't connect to backend

**Solutions**:
- Add frontend URL to `API_CORS_ORIGINS` environment variable
- Format: `https://your-app.vercel.app,http://localhost:3000`
- Restart Space after adding variable
- Verify `FRONTEND_URL` is set correctly

### ❌ Port Binding Error

**Problem**: "Address already in use" or port errors

**Solutions**:
- Ensure Dockerfile uses port 7860 (Hugging Face default)
- Don't change `API_PORT` from 7860
- Restart Space if needed

---

## 📊 Monitoring & Maintenance

### View Logs
1. Go to Space → **"Logs"** tab
2. Real-time logs show:
   - Application startup
   - API requests
   - Errors and warnings
   - Database queries

### Check Metrics
- **CPU Usage**: Visible in Space dashboard
- **Memory Usage**: Visible in Space dashboard
- **Request Count**: Check logs
- **Response Times**: Monitor `/metrics` endpoint

### Health Monitoring
Set up external monitoring (optional):
- **UptimeRobot**: https://uptimerobot.com (free)
- **Pingdom**: https://www.pingdom.com
- Monitor: `https://YOUR-SPACE.hf.space/health`

---

## 💰 Cost & Limits

### Free Tier (CPU Basic)
- ✅ 2 vCPU
- ✅ 16 GB RAM
- ✅ Always-on (no sleep)
- ✅ Unlimited requests
- ✅ Unlimited bandwidth
- ⚠️ Public visibility required

### Paid Tiers
- **CPU Upgrade**: $0.03/hour (4 vCPU, 32 GB RAM)
- **GPU T4**: $0.60/hour (for ML workloads)
- **Private Spaces**: Available on paid plans

### External Costs
- **Neon Database**: Free tier (3 GB storage)
- **OpenAI API**: Pay per token (~$0.002/1K tokens)
- **Groq API**: Free tier available
- **Twilio WhatsApp**: Pay per message (~$0.005/message)

---

## 🔄 Updates & Redeployment

### Update Application Code

1. **Make changes** to your backend code
2. **Commit changes**:
   ```bash
   git add .
   git commit -m "Update: description of changes"
   ```
3. **Push to Hugging Face**:
   ```bash
   git subtree push --prefix=backend hf main
   ```
4. **Automatic rebuild** starts (3-5 minutes)
5. **Zero-downtime deployment** (old version runs until new one is ready)

### Update Environment Variables

1. Go to Space → **Settings** → **Variables and secrets**
2. Edit or add new variables
3. **Restart Space** for changes to take effect:
   - Click **"Factory reboot"** button in Space settings

---

## 🔐 Security Best Practices

- ✅ Never commit secrets to GitHub
- ✅ Use Hugging Face Secrets for all sensitive data
- ✅ Rotate API keys regularly (every 90 days)
- ✅ Enable HTTPS (automatic on Hugging Face)
- ✅ Monitor access logs for suspicious activity
- ✅ Use strong database passwords
- ✅ Limit CORS origins to specific domains
- ✅ Keep dependencies updated

---

## 📞 Support & Resources

### Documentation
- **Hugging Face Spaces**: https://huggingface.co/docs/hub/spaces
- **Docker Spaces**: https://huggingface.co/docs/hub/spaces-sdks-docker
- **FastAPI**: https://fastapi.tiangolo.com

### Community
- **Hugging Face Discord**: https://discord.gg/huggingface
- **Hugging Face Forum**: https://discuss.huggingface.co

### Your Project
- **GitHub Issues**: Create issues in your repository
- **Backend Logs**: Check Space logs for errors

---

## ✅ Deployment Checklist

Before going live:

- [ ] Hugging Face Space created (Docker SDK)
- [ ] All environment variables added
- [ ] Dockerfile and .dockerignore committed
- [ ] Code pushed to Hugging Face
- [ ] Build completed successfully
- [ ] Health check returns 200 OK
- [ ] Database connection working
- [ ] pgvector extension installed
- [ ] Knowledge base populated
- [ ] API documentation accessible
- [ ] CORS configured for frontend
- [ ] Backend URL saved for frontend config
- [ ] Monitoring set up (optional)

---

## 🎉 Next Steps

After backend is deployed:

1. **Save Backend URL**: `https://YOUR-USERNAME-custora-backend.hf.space`
2. **Test all endpoints** using Swagger UI
3. **Deploy Frontend** to Vercel (next phase)
4. **Configure OAuth** redirects
5. **Test end-to-end** flow
6. **Set up monitoring** and alerts

---

**Your backend is now live on Hugging Face Spaces! 🚀**
