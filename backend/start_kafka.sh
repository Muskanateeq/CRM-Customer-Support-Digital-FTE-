#!/bin/bash
# ============================================
# Kafka Setup and Test Script
# ============================================

set -e  # Exit on error

echo "============================================"
echo "TaskNest Kafka Setup"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Step 1: Check Docker
echo -e "${YELLOW}[Step 1] Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR] Docker not found. Please install Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] Docker is installed${NC}"
echo ""

# Step 2: Check if Docker is running
echo -e "${YELLOW}[Step 2] Checking if Docker is running...${NC}"
if ! docker ps &> /dev/null; then
    echo -e "${RED}[ERROR] Docker is not running!${NC}"
    echo "Please start Docker Desktop and wait for it to be ready."
    echo "Then run this script again."
    exit 1
fi
echo -e "${GREEN}[OK] Docker is running${NC}"
echo ""

# Step 3: Start Kafka
echo -e "${YELLOW}[Step 3] Starting Kafka and Zookeeper...${NC}"
echo "This may take 1-2 minutes on first run (downloading images)..."
docker-compose -f docker-compose-kafka.yml up -d
echo -e "${GREEN}[OK] Kafka started${NC}"
echo ""

# Step 4: Wait for Kafka to be ready
echo -e "${YELLOW}[Step 4] Waiting for Kafka to be ready (30 seconds)...${NC}"
sleep 30
echo -e "${GREEN}[OK] Kafka should be ready now${NC}"
echo ""

# Step 5: Verify Kafka is running
echo -e "${YELLOW}[Step 5] Verifying Kafka containers...${NC}"
docker ps | grep -E "kafka|zookeeper"
echo ""

echo "============================================"
echo -e "${GREEN}Kafka Setup Complete!${NC}"
echo "============================================"
echo ""
echo "Kafka is running on: localhost:9092"
echo "Zookeeper is running on: localhost:2181"
echo ""
echo "Next steps:"
echo "  1. Update .env file: Set KAFKA_ENABLED=true"
echo "  2. Start API: cd src && uvicorn api.main:app --reload"
echo "  3. Start Workers: cd src && python workers/service.py"
echo ""
echo "To stop Kafka:"
echo "  docker-compose -f docker-compose-kafka.yml down"
echo ""
