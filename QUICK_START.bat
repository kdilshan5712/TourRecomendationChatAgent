@echo off
cls
echo.
echo ================================================
echo   AI TOUR SYSTEM - QUICK RESTART
echo ================================================
echo.

cd /d "%~dp0ui"

echo Starting Flask Server...
echo Server will be at: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

python app.py
