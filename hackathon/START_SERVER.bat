@echo off
REM ============================================
REM NASIKO HACKATHON - QUICK START
REM ============================================

echo.
echo =====================================
echo   NASIKO HR AI AGENT - QUICK START
echo =====================================
echo.

REM Check if .env exists
if not exist .env (
    echo [!] WARNING: .env file not found!
    echo.
    echo Please create .env file with your API keys:
    echo   1. Copy .env.example to .env
    echo   2. Edit .env and add your GROQ_API_KEY
    echo.
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found!
    echo Please install Python 3.8 or higher
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
echo [OK] .env file found
echo.
echo Starting server...
echo.
echo Dashboard will open at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
echo =====================================
echo.

REM Start the server
python main.py

REM If server exits
echo.
echo Server stopped.
pause
