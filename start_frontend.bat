@echo off
:: ============================================================
:: EduPlatform Social Media Agent — Frontend Startup Script
:: Opens the admin dashboard in your default browser.
:: ============================================================

echo.
echo  Opening EduPlatform Admin Dashboard in your browser...
echo  Backend must be running at http://localhost:8000
echo.

cd /d "%~dp0frontend"

:: Try to use Python's simple HTTP server for proper CORS handling
python -m http.server 3000 --bind 0.0.0.0

pause
