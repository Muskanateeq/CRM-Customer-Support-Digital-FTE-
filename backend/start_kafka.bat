@echo off
REM ============================================
REM Kafka Setup and Test Script for Windows
REM ============================================

echo ============================================
echo TaskNest Kafka Setup
echo ============================================
echo.

REM Step 1: Check Docker
echo [Step 1] Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker not found. Please install Docker Desktop.
    exit /b 1
)
echo [OK] Docker is installed
echo.

REM Step 2: Check if Docker is running
echo [Step 2] Checking if Docker is running...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and wait for it to be ready.
    echo Then run this script again.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

REM Step 3: Start Kafka
echo [Step 3] Starting Kafka and Zookeeper...
echo This may take 1-2 minutes on first run (downloading images)...
docker-compose -f docker-compose-kafka.yml up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Kafka
    pause
    exit /b 1
)
echo [OK] Kafka started
echo.

REM Step 4: Wait for Kafka to be ready
echo [Step 4] Waiting for Kafka to be ready (30 seconds)...
timeout /t 30 /nobreak >nul
echo [OK] Kafka should be ready now
echo.

REM Step 5: Verify Kafka is running
echo [Step 5] Verifying Kafka containers...
docker ps | findstr kafka
docker ps | findstr zookeeper
echo.

echo ============================================
echo Kafka Setup Complete!
echo ============================================
echo.
echo Kafka is running on: localhost:9092
echo Zookeeper is running on: localhost:2181
echo.
echo Next steps:
echo   1. Update .env file: Set KAFKA_ENABLED=true
echo   2. Start API: cd src ^&^& uvicorn api.main:app --reload
echo   3. Start Workers: cd src ^&^& python workers/service.py
echo.
echo To stop Kafka:
echo   docker-compose -f docker-compose-kafka.yml down
echo.
pause
