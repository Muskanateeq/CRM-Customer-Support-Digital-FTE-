# 🚀 Quick Start - Kafka Testing

## Run These Commands in Order

### 1. Start Docker Desktop
- Open Docker Desktop application
- Wait for green icon in system tray (2-3 minutes)

### 2. Start Kafka (in backend folder)
```bash
cd D:\Hackathon5\backend
start_kafka.bat
```
Wait 30 seconds for Kafka to initialize.

### 3. Test Kafka Connection
```bash
cd D:\Hackathon5\backend\scripts
python test_kafka.py
```
Expected: "✅ Kafka Test PASSED!"

### 4. Start API Server (Terminal 1)
```bash
cd D:\Hackathon5\backend\src
uvicorn api.main:app --reload
```
Expected: "INFO: [OK] Kafka producer started"

### 5. Start Workers (Terminal 2)
```bash
cd D:\Hackathon5\backend\src
python workers/service.py
```
Expected: "[OK] Worker Service Started - Ready to Process Events"

### 6. Start Frontend (Terminal 3)
```bash
cd D:\Hackathon5\frontend\customer-support-form
npm run dev
```

### 7. Test in Browser
Open: http://localhost:3000/support

Submit a test message and watch:
- ✅ Real-time AI response in chat
- ✅ API logs show Kafka events
- ✅ Worker logs show event processing

---

## Quick Commands

**Check Kafka Status:**
```bash
docker ps | findstr kafka
```

**View Kafka Logs:**
```bash
cd D:\Hackathon5\backend
docker-compose -f docker-compose-kafka.yml logs -f
```

**Stop Kafka:**
```bash
cd D:\Hackathon5\backend
docker-compose -f docker-compose-kafka.yml down
```

**Restart Kafka:**
```bash
cd D:\Hackathon5\backend
docker-compose -f docker-compose-kafka.yml restart
```

---

## Troubleshooting

**Problem: Docker not running**
- Start Docker Desktop and wait for green icon

**Problem: Kafka test fails**
- Run: `docker ps` to verify Kafka is running
- Check logs: `docker-compose -f docker-compose-kafka.yml logs kafka`

**Problem: Workers not processing**
- Verify KAFKA_ENABLED=true in .env
- Restart workers

---

For detailed guide, see: KAFKA_SETUP.md
