# 🔄 GitHub Actions CI/CD Pipeline Guide

Complete guide to set up automated deployment pipeline for Custora AI CRM.

---

## 📋 Overview

This CI/CD pipeline automates:
- ✅ **Backend deployment** to Hugging Face Spaces
- ✅ **Frontend deployment** to Vercel
- ✅ **Automated testing** on pull requests
- ✅ **Security scanning** for vulnerabilities
- ✅ **Code quality checks** (linting, type checking)

---

## 🏗️ Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│                      (Push to main)                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─────────────────┬─────────────────┐
                 ▼                 ▼                 ▼
         ┌───────────────┐ ┌──────────────┐ ┌─────────────┐
         │  Run Tests    │ │   Backend    │ │  Frontend   │
         │  (PR/Push)    │ │   Deploy     │ │   Deploy    │
         └───────────────┘ └──────┬───────┘ └──────┬──────┘
                                  │                 │
                                  ▼                 ▼
                          ┌──────────────┐  ┌─────────────┐
                          │ Hugging Face │  │   Vercel    │
                          │    Spaces    │  │  Production │
                          └──────────────┘  └─────────────┘
```

---

## 🔐 Step 1: Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### **Hugging Face Secrets**

1. **HF_TOKEN** (Required)
   - Go to: https://huggingface.co/settings/tokens
   - Click **"New token"**
   - Name: `github-actions-deploy`
   - Type: **Write** (required for pushing)
   - Click **"Generate"**
   - Copy token and add to GitHub secrets
   - Value: `hf_xxxxxxxxxxxxxxxxxxxxx`

2. **HF_USERNAME** (Required)
   - Your Hugging Face username
   - Example: `muskanateeq`

3. **HF_SPACE_NAME** (Required)
   - Your Space name (created in Phase 1)
   - Example: `custora-backend`

### **Vercel Secrets**

1. **VERCEL_TOKEN** (Required)
   - Go to: https://vercel.com/account/tokens
   - Click **"Create Token"**
   - Name: `github-actions-deploy`
   - Scope: **Full Account**
   - Expiration: **No Expiration** (or custom)
   - Click **"Create"**
   - Copy token and add to GitHub secrets
   - Value: `vercel_xxxxxxxxxxxxxxxxxxxxx`

2. **VERCEL_ORG_ID** (Required)
   - Go to: https://vercel.com/account
   - Copy your **Team ID** or **User ID**
   - Or get from project settings → **General** → **Project ID** section
   - Value: `team_xxxxxxxxxxxxxxxxxxxxx`

3. **VERCEL_PROJECT_ID** (Required)
   - Go to your Vercel project → **Settings** → **General**
   - Scroll to **Project ID**
   - Copy the ID
   - Value: `prj_xxxxxxxxxxxxxxxxxxxxx`

---

## 📁 Step 2: Verify Workflow Files

Ensure these files exist in your repository:

```
.github/
└── workflows/
    ├── backend-deploy.yml    # Backend deployment
    ├── frontend-deploy.yml   # Frontend deployment
    └── tests.yml             # Testing pipeline
```

All files should already be created. Verify with:

```bash
ls -la .github/workflows/
```

---

## 🚀 Step 3: Enable GitHub Actions

1. Go to your repository → **Actions** tab
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. You should see three workflows:
   - ✅ Deploy Backend to Hugging Face
   - ✅ Deploy Frontend to Vercel
   - ✅ Run Tests

---

## 🔄 Step 4: How It Works

### **Automatic Deployments**

#### Backend Deployment
**Triggers when:**
- Push to `main` branch
- Changes in `backend/**` folder
- Manual trigger via Actions tab

**What it does:**
1. Checks out repository
2. Configures Git
3. Pushes backend folder to Hugging Face Space using `git subtree`
4. Verifies deployment health
5. Notifies success/failure

**Deployment time:** ~5-10 minutes (Hugging Face build time)

#### Frontend Deployment
**Triggers when:**
- Push to `main` branch
- Changes in `frontend/customer-support-form/**` folder
- Manual trigger via Actions tab

**What it does:**
1. Checks out repository
2. Sets up Node.js
3. Installs Vercel CLI
4. Pulls Vercel environment
5. Builds Next.js application
6. Deploys to Vercel production
7. Verifies deployment

**Deployment time:** ~2-3 minutes

#### Testing Pipeline
**Triggers when:**
- Pull request to `main` branch
- Push to `main` branch
- Manual trigger via Actions tab

**What it does:**
1. **Backend tests:**
   - Linting (flake8)
   - Code formatting (black)
   - Type checking (mypy)
   - Unit tests (pytest)
   - Dockerfile validation

2. **Frontend tests:**
   - Linting (ESLint)
   - Type checking (TypeScript)
   - Build verification
   - Unit tests (if configured)

3. **Security scan:**
   - Vulnerability scanning (Trivy)
   - Secret detection

**Test time:** ~3-5 minutes

---

## 🎯 Step 5: First Deployment

### Deploy Backend

1. **Commit workflow files:**
   ```bash
   git add .github/workflows/backend-deploy.yml
   git add backend/Dockerfile backend/.dockerignore
   git commit -m "ci: Add backend deployment workflow"
   git push origin main
   ```

2. **Monitor deployment:**
   - Go to **Actions** tab
   - Click on **"Deploy Backend to Hugging Face"** workflow
   - Watch the deployment progress
   - Check logs for any errors

3. **Verify deployment:**
   - Visit: `https://YOUR-USERNAME-custora-backend.hf.space/health`
   - Should return: `{"status": "healthy", ...}`

### Deploy Frontend

1. **Commit workflow files:**
   ```bash
   git add .github/workflows/frontend-deploy.yml
   git add frontend/customer-support-form/vercel.json
   git commit -m "ci: Add frontend deployment workflow"
   git push origin main
   ```

2. **Monitor deployment:**
   - Go to **Actions** tab
   - Click on **"Deploy Frontend to Vercel"** workflow
   - Watch the deployment progress

3. **Verify deployment:**
   - Visit your Vercel URL
   - Test homepage, login, support portal

---

## 🧪 Step 6: Test the Pipeline

### Test Automatic Deployment

1. **Make a small change:**
   ```bash
   # Backend change
   echo "# Updated" >> backend/README.md
   git add backend/README.md
   git commit -m "test: Trigger backend deployment"
   git push origin main
   ```

2. **Watch Actions tab:**
   - Backend deployment should trigger automatically
   - Only backend workflow runs (frontend skipped)

3. **Make frontend change:**
   ```bash
   # Frontend change
   echo "// Updated" >> frontend/customer-support-form/README.md
   git add frontend/customer-support-form/README.md
   git commit -m "test: Trigger frontend deployment"
   git push origin main
   ```

4. **Watch Actions tab:**
   - Frontend deployment should trigger automatically
   - Only frontend workflow runs (backend skipped)

### Test Pull Request Workflow

1. **Create feature branch:**
   ```bash
   git checkout -b feature/test-ci
   ```

2. **Make changes:**
   ```bash
   echo "# Test" >> README.md
   git add README.md
   git commit -m "test: CI pipeline"
   git push origin feature/test-ci
   ```

3. **Create Pull Request:**
   - Go to GitHub → **Pull requests** → **New pull request**
   - Base: `main`, Compare: `feature/test-ci`
   - Click **"Create pull request"**

4. **Watch tests run:**
   - Tests automatically run on PR
   - See results in PR checks section
   - Merge only if tests pass

---

## 🔧 Troubleshooting

### ❌ Backend Deployment Fails

**Problem:** "Authentication failed" or "Permission denied"

**Solutions:**
- Verify `HF_TOKEN` has **Write** permissions
- Check `HF_USERNAME` and `HF_SPACE_NAME` are correct
- Ensure Space exists on Hugging Face
- Try regenerating HF token

**Problem:** "git subtree push failed"

**Solutions:**
- Check if backend folder exists
- Verify Git history is not corrupted
- Try force push (workflow includes fallback)
- Check Hugging Face Space logs

### ❌ Frontend Deployment Fails

**Problem:** "Vercel token invalid"

**Solutions:**
- Verify `VERCEL_TOKEN` is correct
- Check token hasn't expired
- Ensure token has correct scope (Full Account)
- Regenerate token if needed

**Problem:** "Project not found"

**Solutions:**
- Verify `VERCEL_ORG_ID` is correct
- Check `VERCEL_PROJECT_ID` matches your project
- Ensure project exists on Vercel
- Try redeploying manually first

### ❌ Tests Fail

**Problem:** Linting errors

**Solutions:**
- Run linting locally: `npm run lint` or `flake8 src/`
- Fix errors before pushing
- Update linting rules if needed

**Problem:** Build fails

**Solutions:**
- Test build locally: `npm run build` or `docker build`
- Check for missing dependencies
- Verify environment variables
- Review build logs for specific errors

### ❌ Secrets Not Working

**Problem:** Secrets are undefined in workflow

**Solutions:**
- Verify secret names match exactly (case-sensitive)
- Check secrets are set at repository level (not environment)
- Re-add secrets if needed
- Restart workflow after adding secrets

---

## 📊 Monitoring Deployments

### GitHub Actions Dashboard

1. Go to **Actions** tab
2. View all workflow runs
3. Filter by:
   - Workflow name
   - Branch
   - Status (success/failure)
   - Date range

### Deployment Status Badges

Add to your README.md:

```markdown
![Backend Deploy](https://github.com/YOUR-USERNAME/Hackathon5/actions/workflows/backend-deploy.yml/badge.svg)
![Frontend Deploy](https://github.com/YOUR-USERNAME/Hackathon5/actions/workflows/frontend-deploy.yml/badge.svg)
![Tests](https://github.com/YOUR-USERNAME/Hackathon5/actions/workflows/tests.yml/badge.svg)
```

### Email Notifications

GitHub automatically sends emails for:
- ✅ Workflow failures
- ✅ First workflow run
- ✅ Workflow re-enabled

Configure in: **Settings** → **Notifications** → **Actions**

---

## 🔄 Advanced Configuration

### Deploy to Staging

Create staging workflows:

1. **Create staging branch:**
   ```bash
   git checkout -b staging
   git push origin staging
   ```

2. **Duplicate workflows:**
   - Copy `backend-deploy.yml` → `backend-deploy-staging.yml`
   - Copy `frontend-deploy.yml` → `frontend-deploy-staging.yml`

3. **Update triggers:**
   ```yaml
   on:
     push:
       branches:
         - staging  # Changed from main
   ```

4. **Add staging secrets:**
   - `HF_SPACE_NAME_STAGING`
   - `VERCEL_PROJECT_ID_STAGING`

### Deployment Approvals

For production deployments, add manual approval:

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://your-app.vercel.app
    runs-on: ubuntu-latest
    # ... rest of job
```

Then configure in: **Settings** → **Environments** → **production** → **Required reviewers**

### Slack Notifications

Add Slack notifications on deployment:

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 💰 Cost & Limits

### GitHub Actions (Free Tier)

**Public Repositories:**
- ✅ Unlimited minutes
- ✅ Unlimited workflows
- ✅ 20 concurrent jobs

**Private Repositories:**
- ✅ 2,000 minutes/month
- ✅ 500 MB storage
- ✅ 20 concurrent jobs

**Paid Plans:**
- Pro: $4/month (3,000 minutes)
- Team: $21/month (10,000 minutes)
- Enterprise: Custom pricing

### Workflow Optimization

**Reduce build time:**
- Use caching for dependencies
- Skip unnecessary steps
- Run jobs in parallel
- Use smaller runners

**Reduce minutes usage:**
- Only trigger on relevant paths
- Skip workflows for docs changes
- Use manual triggers for non-critical deployments

---

## ✅ CI/CD Checklist

Setup complete when:

- [ ] All GitHub secrets configured
- [ ] Workflow files committed
- [ ] GitHub Actions enabled
- [ ] Backend deployment successful
- [ ] Frontend deployment successful
- [ ] Tests running on PRs
- [ ] Deployment badges added to README
- [ ] Team notified of CI/CD setup
- [ ] Documentation updated
- [ ] Monitoring configured

---

## 🎉 Success!

Your CI/CD pipeline is now fully automated! 🚀

**What happens now:**
1. Push code to `main` → Automatic deployment
2. Create PR → Automatic testing
3. Merge PR → Automatic deployment
4. Zero manual deployment steps needed!

**Best Practices:**
- Always create PRs for changes
- Wait for tests to pass before merging
- Monitor deployment logs
- Keep secrets secure and rotated
- Document deployment process

---

## 📞 Support

- **GitHub Actions Docs**: https://docs.github.com/actions
- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **Vercel Docs**: https://vercel.com/docs
- **Your Repository Issues**: Create issues for pipeline problems

---

**Your complete CI/CD pipeline is ready! 🎊**
