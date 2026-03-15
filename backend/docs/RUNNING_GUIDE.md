# TaskNest - Complete Running Guide

> Step-by-step guide to get your CRM up and running

## 📋 Table of Contents

1. [Get Credentials](#1-get-credentials)
2. [Setup Environment](#2-setup-environment)
3. [Start Services](#3-start-services)
4. [Test the CRM](#4-test-the-crm)
5. [Verify It's Working](#5-verify-its-working)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Get Credentials

### A. OpenAI API Key (Required)

**Kya Chahiye**: OpenAI API key for GPT-4o

**Kaise Milega**:
1. Go to: https://platform.openai.com/api-keys
2. Sign up / Login
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. **Important**: Save it somewhere safe, you can't see it again!

**Cost**: ~$0.01 per request (GPT-4o)

---

### B. Neon PostgreSQL (Required)

**Kya Chahiye**: PostgreSQL database with pgvector

**Kaise Milega**:
1. Go to: https://neon.tech
2. Sign up (free tier available)
3. Create new project
4. Click "Connection Details"
5. Copy:
   - Host (e.g., `ep-xxx.neon.tech`)
   - Database name (usually `neondb`)
   - Username
   - Password
   - Full connection string

**Cost**: Free tier available (0.5GB storage)

---

### C. Twilio WhatsApp (Optional)

**Kya Chahiye**: WhatsApp Business API via Twilio

**Kaise Milega**:
1. Go to: https://www.twilio.com/console
2. Sign up / Login
3. Go to "Messaging" → "Try it out" → "Send a WhatsApp message"
4. Get:
   - Account SID
   - Auth Token
   - WhatsApp number (e.g., `+14155238886`)

**Cost**: Free trial credits, then pay-as-you-go

**Note**: Agar WhatsApp nahi chahiye, to `.env` mein `WHATSAPP_ENABLED=false` set kar do

---

### D. Gmail API (Optional)

**Kya Chahiye**: Gmail OAuth2 credentials

**Kaise Milega**:
1. Go to: https://console.cloud.google.com
2. Create new project
3. Enable "Gmail API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Desktop app"
6. Download JSON file
7. Copy content to `.env` as `GMAIL_CREDENTIALS_JSON`

**Cost**: Free

**Note**: Agar Gmail nahi chahiye, to `.env` mein `GMAIL_ENABLED=false` set kar do

---

## 2. Setup Environment

### Step 1: Copy Environment Template

```bash
cd D:\Hackathon5
cp .env.example .env
```

### Step 2: Edit .env File

Open `.env` in any text editor and fill in your credentials:

```bash
# ============================================
# REQUIRED - Must Fill These
# ============================================

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# Database (Neon)
DATABASE_URL=postgresql://username:password@ep-xxx.neon.tech:5432/neondb
POSTGRES_HOST=ep-xxx.neon.tech
POSTGRES_PORT=5432
POSTGRES_DB=neondb
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-password
PROJECT_ID=your-neon-project-id

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
AGENT_MODEL=gpt-4o

# Kafka (Local)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# ============================================
# OPTIONAL - Can Skip for Now
# ============================================

# Gmail (Optional - set to false if not using)
GMAIL_ENABLED=false
GMAIL_CREDENTIALS_JSON=
GMAIL_TOKEN_JSON=

# WhatsApp (Optional - set to false if not using)
WHATSAPP_ENABLED=false
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_NUMBER=

# Web Form (Keep enabled for testing)
WEBFORM_ENABLED=true

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 3: Setup Database

```bash
# Activate UV environment
.venv\Scripts\activate

# Run database setup script
python scripts/setup_pgvector.py

# Populate knowledge base with sample data
python scripts/populate_knowledge_base.py
```

---

## 3. Start Services

### Option A: Docker Compose (Easiest - Recommended)

**Yeh sab automatically start ho jayega**:
- PostgreSQL (if not using Neon)
- Kafka + ZooKeeper
- API (3 replicas)
- Workers (2 replicas)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f worker
```

**Access**:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

### Option B: Manual Start (For Development)

#### Step 1: Start Kafka

```bash
# Start Kafka with Docker
docker-compose up -d kafka zookeeper

# Wait 30 seconds for Kafka to start
timeout 30

# Verify Kafka is running
docker-compose ps kafka
```

#### Step 2: Start API

```bash
# Activate environment
.venv\Scripts\activate

# Start API
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal open. API is now running at http://localhost:8000

#### Step 3: Start Workers (New Terminal)

```bash
# Activate environment
.venv\Scripts\activate

# Start worker service
python src/workers/service.py
```

Keep this terminal open. Workers are now processing events.

---

## 4. Test the CRM

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-..."
}
```

---

### Test 2: Submit Web Form (Customer Query)

```bash
curl -X POST http://localhost:8000/channels/webform \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "test@example.com",
    "customer_name": "Test Customer",
    "message": "How do I reset my password?"
  }'
```

**Expected Response**:
```json
{
  "status": "success",
  "message": "Your message has been received",
  "ticket_id": "xxx",
  "response": "To reset your password, go to..."
}
```

---

### Test 3: Check API Documentation

Open in browser: http://localhost:8000/docs

Yahan aap:
- All endpoints dekh sakte hain
- Interactive testing kar sakte hain
- Request/Response examples dekh sakte hain

---

### Test 4: Test Agent Tools

```bash
# Activate environment
.venv\Scripts\activate

# Run demo script
python demo_tools.py
```

Yeh script test karega:
- Knowledge base search
- Ticket creation
- Customer history
- Escalation
- Response sending

---

## 5. Verify It's Working

### Check 1: API Logs

```bash
# If using Docker Compose
docker-compose logs -f api

# If running manually
# Check the terminal where you started the API
```

**Look for**:
- `[OK] Database connected`
- `[OK] Database pool initialized`
- `Application startup complete`
- `POST /channels/webform` requests

---

### Check 2: Worker Logs

```bash
# If using Docker Compose
docker-compose logs -f worker

# If running manually
# Check the terminal where you started workers
```

**Look for**:
- `[START] Starting Kafka worker service`
- `[OK] Consumer started for topic: message.received`
- `Processing event: message.received`

---

### Check 3: Database

```bash
# Connect to Neon database
psql $DATABASE_URL

# Check tables
\dt

# Check customers
SELECT * FROM customers LIMIT 5;

# Check conversations
SELECT * FROM conversations LIMIT 5;

# Check messages
SELECT * FROM messages LIMIT 5;

# Exit
\q
```

---

### Check 4: Kafka Topics

```bash
# List Kafka topics
docker exec -it hackathon5-kafka-1 kafka-topics --list --bootstrap-server localhost:9092
```

**Expected Topics**:
- message.received
- message.sent
- escalation.created
- ticket.created
- agent.execution.completed

---

## 6. Troubleshooting

### Problem 1: API Not Starting

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Activate environment first
.venv\Scripts\activate

# Then run
python -m uvicorn src.api.main:app --reload
```

---

### Problem 2: Database Connection Failed

**Error**: `could not connect to server`

**Solution**:
1. Check `.env` file - DATABASE_URL correct hai?
2. Check Neon dashboard - database running hai?
3. Test connection:
```bash
psql $DATABASE_URL
```

---

### Problem 3: Kafka Connection Failed

**Error**: `KafkaConnectionError`

**Solution**:
```bash
# Check if Kafka is running
docker-compose ps kafka

# If not running, start it
docker-compose up -d kafka zookeeper

# Wait 30 seconds
timeout 30

# Try again
```

---

### Problem 4: OpenAI API Error

**Error**: `AuthenticationError: Invalid API key`

**Solution**:
1. Check `.env` file - OPENAI_API_KEY correct hai?
2. Verify key at: https://platform.openai.com/api-keys
3. Make sure key starts with `sk-`

---

### Problem 5: Port Already in Use

**Error**: `Address already in use: 8000`

**Solution**:
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn src.api.main:app --port 8001
```

---

## 7. Complete Testing Flow

### End-to-End Test

```bash
# 1. Start all services
docker-compose up -d

# 2. Wait for services to be ready
timeout 30

# 3. Check health
curl http://localhost:8000/health

# 4. Submit customer query
curl -X POST http://localhost:8000/channels/webform \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "john@example.com",
    "customer_name": "John Doe",
    "message": "I need help with my account"
  }'

# 5. Check logs
docker-compose logs api | tail -20
docker-compose logs worker | tail -20

# 6. Check database
psql $DATABASE_URL -c "SELECT * FROM customers WHERE email='john@example.com';"
psql $DATABASE_URL -c "SELECT * FROM messages ORDER BY created_at DESC LIMIT 5;"
```

---

## 8. Production Deployment

### Kubernetes Deployment

```bash
# 1. Build Docker images
export DOCKER_REGISTRY=your-registry
export VERSION=v1.0.0
./scripts/build_and_push.sh

# 2. Update K8s manifests
# Edit k8s/api-deployment.yaml - update image name
# Edit k8s/worker-deployment.yaml - update image name
# Edit k8s/secret.yaml - add real credentials

# 3. Deploy to Kubernetes
./scripts/deploy.sh

# 4. Check status
kubectl get pods -n tasknest
kubectl logs -f -n tasknest deployment/tasknest-api

# 5. Access API
kubectl port-forward -n tasknest svc/tasknest-api 8000:80
# Then: http://localhost:8000
```

---

## 9. Monitoring

### Check System Status

```bash
# API health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/ready

# View metrics (if enabled)
curl http://localhost:9090/metrics
```

### View Logs

```bash
# API logs
docker-compose logs -f api

# Worker logs
docker-compose logs -f worker

# Kafka logs
docker-compose logs -f kafka

# All logs
docker-compose logs -f
```

---

## 10. Common Use Cases

### Use Case 1: Customer Submits Query via Web Form

**What Happens**:
1. Customer fills form on website
2. POST request to `/channels/webform`
3. API creates customer + conversation + message
4. OpenAI agent processes query
5. Agent searches knowledge base
6. Agent generates response
7. Response sent back to customer
8. Events published to Kafka
9. Workers process events (analytics, notifications, etc.)

**Test It**:
```bash
curl -X POST http://localhost:8000/channels/webform \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "customer@example.com",
    "customer_name": "Jane Smith",
    "message": "How do I upgrade my plan?"
  }'
```

---

### Use Case 2: Customer Needs Human Support

**What Happens**:
1. Customer query is complex
2. Agent decides to escalate
3. Escalation created in database
4. Event published to Kafka
5. Human support team notified
6. Ticket assigned to human agent

**Test It**:
```bash
curl -X POST http://localhost:8000/channels/webform \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "vip@example.com",
    "customer_name": "VIP Customer",
    "message": "I want a refund immediately!"
  }'
```

---

## 11. Quick Reference

### Start Everything
```bash
docker-compose up -d
```

### Stop Everything
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart api worker
```

### View Logs
```bash
docker-compose logs -f api
```

### Check Status
```bash
docker-compose ps
curl http://localhost:8000/health
```

### Run Tests
```bash
.venv\Scripts\activate
python test_module1.py
python test_module6.py
python test_module7.py
```

---

## 12. Summary

### Minimum Required Credentials

1. **OpenAI API Key** - For AI agent
2. **Neon Database** - For data storage
3. **Kafka** - Runs locally with Docker

### Optional Credentials

1. **Twilio** - For WhatsApp (set `WHATSAPP_ENABLED=false` if not using)
2. **Gmail** - For email (set `GMAIL_ENABLED=false` if not using)

### Quick Start Commands

```bash
# 1. Setup
cp .env.example .env
# Edit .env with credentials

# 2. Install dependencies (already done with UV)
.venv\Scripts\activate

# 3. Setup database
python scripts/setup_pgvector.py
python scripts/populate_knowledge_base.py

# 4. Start services
docker-compose up -d

# 5. Test
curl http://localhost:8000/health
curl -X POST http://localhost:8000/channels/webform \
  -H "Content-Type: application/json" \
  -d '{"customer_email":"test@example.com","customer_name":"Test","message":"Hello"}'

# 6. View logs
docker-compose logs -f
```

---

## ✅ Checklist

Before going live, make sure:

- [ ] OpenAI API key added to `.env`
- [ ] Neon database credentials added to `.env`
- [ ] Database setup script run (`setup_pgvector.py`)
- [ ] Knowledge base populated (`populate_knowledge_base.py`)
- [ ] Docker Compose services running
- [ ] Health check passing (`/health`)
- [ ] Test query successful (`/channels/webform`)
- [ ] Logs showing no errors
- [ ] Workers processing events

---

**Your CRM is now running and ready to support customers!** 🎉

For issues, check the Troubleshooting section or review logs.
