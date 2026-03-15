@echo off
REM Email Polling Service for Custora AI
REM Runs the email polling script

echo ========================================
echo Custora AI - Email Polling Service
echo ========================================
echo.

REM Check if backend is running
curl -s http://localhost:8001/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend is not running!
    echo Please start the backend first:
    echo   cd backend
    echo   python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001
    echo.
    pause
    exit /b 1
)

echo [OK] Backend is running
echo.
echo Starting email polling service...
echo Press Ctrl+C to stop
echo.

REM Activate virtual environment and run polling script
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python scripts\poll_emails.py

pause
