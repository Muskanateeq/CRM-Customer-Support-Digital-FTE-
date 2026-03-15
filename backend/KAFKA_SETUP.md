# 🚀 Kafka Setup and Testing Guide

Complete guide to enable and test Kafka for TaskNest CRM.

---

## 📋 Prerequisites

- ✅ Docker Desktop installed
- ✅ Python 3.8+ installed
- ✅ Backend dependencies installed (`pip install -r requirements.txt`)

---

## 🐳 Step 1: Start Docker Desktop

**Windows:**
1. Press `Windows Key`
2. Type "Docker Desktop"
3. Click on Docker Desktop application
4. Wait for Docker icon in system tray to turn green (2-3 minutes)

**Verify Docker is running:**
```bash
docker ps
```

If you see a table (even if empty), Docker is running! ✅

---

## 🚀 Step 2: Start Kafka

**Option A: Using the startup script (Recommended)**

```bash
# Windows
cd backend
start_kafka.bat

# Linux/Mac
cd backend
./start_kafka.sh
```

**Option B: Manual start**

```bash
cd backend
docker-compose -f docker-compose-kafka.yml up -d
```

**Wait 30 seconds** for Kafka to initialize.

**Verify Kafka is running:**
```bash
docker ps
```

You should see 2 containers:
- `backend-kafka-1` (or similar)
- `backend-zookeeper-1` (or similar)

---

## ⚙️ Step 3: Enable Kafka in .env

The `.env` file has been updated automatically with:
```bash
KAFKA_ENABLED=true
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

**Verify:**
```bash
cat .env | grep KAFKA_ENABLED
# Should show: KAFKA_ENABLED=true
```

---

## 🧪 Step 4: Test Kafka Connection

```bash
cd backend/scripts
python test_kafka.py
```

**Expected output:**
```
============================================================
Kafka Connection Test
============================================================

✅ Kafka is ENABLED
📍 Bootstrap servers: localhost:9092

🔌 Creating Kafka producer...
🚀 Starting producer...
✅ Producer started successfully

📤 Publishing test event...
✅ Event published successfully!
   Topic: message.received
   Event ID: xxx-xxx-xxx

🛑 Stopping producer...
✅ Producer stopped

============================================================
✅ Kafka Test PASSED!
============================================================
```

---

## 🎯 Step 5: Start Backend Services

### Terminal 1: Start API Server

```bash
cd backend/src
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     [OK] Database pool initialized
INFO:     [OK] Kafka producer started
```

**Test API:**
```bash
curl http://localhost:8000/health
```

### Terminal 2: Start Workers

```bash
cd backend/src
python workers/service.py
```

**Expected output:**
```
======================================================================
TaskNest Worker Service - Starting Up
======================================================================
Environment: development
Kafka Bootstrap: localhost:9092
======================================================================
[OK] Database pool initialized
[OK] Consumer created: tasknest-message-received-workers
[OK] Consumer created: tasknest-message-sent-workers
[OK] Worker Service Started - Ready to Process Events
======================================================================
```

---

## 🧪 Step 6: Test End-to-End Flow

### Test 1: Web Form Submission

**Start Frontend (Terminal 3):**
```bash
cd frontend/customer-support-form
npm run dev
```

**Open browser:**
```
http://localhost:3000/support
```

**Submit a test message:**
- Name: Test User
- Email: test@example.com
- Message: How do I reset my password?

**Expected flow:**
1. ✅ Form submits successfully
2. ✅ Chat shows AI response in real-time
3. ✅ API logs show: "Event published to Kafka"
4. ✅ Worker logs show: "Processing message.received event"
5. ✅ Database has new records in `customers`, `conversations`, `messages`

### Test 2: API Direct Test

```bash
curl -X POST http://localhost:8000/api/v1/channels/webform/message \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "message": "How do I reset my password?"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "conversation_id": "xxx-xxx-xxx",
  "customer_id": "xxx-xxx-xxx",
  "message_id": "xxx-xxx-xxx",
  "agent_response": "To reset your password...",
  "execution_time": 2.5
}
```

### Test 3: Check Database

```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM messages;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM conversations;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM customers;"
```

---

## 🔍 Monitoring Kafka

### View Kafka Topics

```bash
docker exec -it backend-kafka-1 kafka-topics --list --bootstrap-server localhost:9092
```

**Expected topics:**
- message.received
- message.sent
- ticket.created
- escalation.created
- agent.execution.completed

### View Kafka Logs

```bash
docker-compose -f docker-compose-kafka.yml logs -f kafka
```

### Check Consumer Groups

```bash
docker exec -it backend-kafka-1 kafka-consumer-groups --bootstrap-server localhost:9092 --list
```

---

## 🛑 Stopping Kafka

```bash
cd backend
docker-compose -f docker-compose-kafka.yml down
```

To also remove volumes (clean slate):
```bash
docker-compose -f docker-compose-kafka.yml down -v
```

---

## 🐛 Troubleshooting

### Issue: "Failed to connect to Kafka"

**Solution:**
1. Check Docker is running: `docker ps`
2. Check Kafka container: `docker ps | grep kafka`
3. Restart Kafka: `docker-compose -f docker-compose-kafka.yml restart`
4. Check logs: `docker-compose -f docker-compose-kafka.yml logs kafka`

### Issue: "Kafka producer not started"

**Solution:**
1. Verify `KAFKA_ENABLED=true` in `.env`
2. Restart API server
3. Check API logs for Kafka connection errors

### Issue: "Workers not processing events"

**Solution:**
1. Check workers are running: Look for "Worker Service Started" message
2. Check Kafka topics exist: `docker exec -it backend-kafka-1 kafka-topics --list --bootstrap-server localhost:9092`
3. Check consumer group lag: `docker exec -it backend-kafka-1 kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group tasknest-message-received-workers`

### Issue: "Docker Desktop not starting"

**Solution:**
1. Restart computer
2. Check Windows Subsystem for Linux (WSL) is enabled
3. Update Docker Desktop to latest version
4. Check Docker Desktop logs: Settings → Troubleshoot → View logs

---

## ✅ Success Checklist

- [ ] Docker Desktop is running
- [ ] Kafka containers are running (`docker ps`)
- [ ] `KAFKA_ENABLED=true` in `.env`
- [ ] Kafka test passes (`python test_kafka.py`)
- [ ] API server starts without errors
- [ ] Workers start and show "Ready to Process Events"
- [ ] Web form submission works end-to-end
- [ ] Database has new records after submission
- [ ] Worker logs show event processing

---

## 📊 Performance Metrics

**Expected latencies:**
- Kafka publish: <10ms
- Event processing: <100ms
- End-to-end (form → response): <3 seconds

**Kafka throughput:**
- Can handle 1000+ messages/second
- Auto-creates topics on first use
- Replication factor: 1 (single broker)

---

## 🎯 Next Steps

After Kafka is working:

1. **Test Email Channel** (if Gmail configured)
2. **Test WhatsApp Channel** (if Twilio configured)
3. **Monitor Performance** (check agent_metrics table)
4. **Deploy to Production** (use K8s manifests in `backend/k8s/`)

---

**Need help?** Check the main README or contact support.
