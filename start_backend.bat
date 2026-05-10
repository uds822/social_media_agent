@echo off
:: ============================================================
:: EduPlatform Social Media Agent — Backend Startup Script
:: Run this on Windows to start the FastAPI server.
:: ============================================================

echo.
echo  ██████╗ ██╗   ██╗███╗   ██╗██╗██╗   ██╗ █████╗  █████╗ ██████╗
echo  ██╔══██╗██║   ██║████╗  ██║██║╚██╗ ██╔╝██╔══██╗██╔══██╗██╔══██╗
echo  ██████╔╝██║   ██║██╔██╗ ██║██║ ╚████╔╝ ███████║███████║██║  ██║
echo  ██╔══██╗██║   ██║██║╚██╗██║██║  ╚██╔╝  ██╔══██║██╔══██║██║  ██║
echo  ██████╔╝╚██████╔╝██║ ╚████║██║   ██║   ██║  ██║██║  ██║██████╔╝
echo  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
echo.
echo  Social Media Agent — The Foundation, City, State
echo  ========================================================
echo.

cd /d "%~dp0backend"

:: Check if .env exists
if not exist ".env" (
  echo  [WARNING] .env file not found!
  echo  Please copy backend\.env.example to backend\.env
  echo  and fill in your API keys before starting.
  echo.
  pause
  exit /b 1
)

:: Check if venv exists, create if not
if not exist "venv\" (
  echo  [SETUP] Creating Python virtual environment...
  python -m venv venv
  echo  [SETUP] Installing dependencies...
  call venv\Scripts\activate.bat
  pip install -r requirements.txt
) else (
  call venv\Scripts\activate.bat
)

echo  [INFO] Starting backend server on http://localhost:8000
echo  [INFO] API docs at http://localhost:8000/docs
echo  [INFO] Press Ctrl+C to stop.
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
