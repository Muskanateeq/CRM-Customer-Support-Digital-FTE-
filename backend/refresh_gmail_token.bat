@echo off
REM Gmail OAuth Token Generator
REM Run this to refresh expired Gmail tokens

echo ========================================
echo Gmail OAuth Token Generator
echo ========================================
echo.

REM Activate virtual environment and run token generator
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python scripts\generate_gmail_token.py

echo.
pause
