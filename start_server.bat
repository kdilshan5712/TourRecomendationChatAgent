@echo off
echo ========================================
echo Starting AI Tour System Server
echo ========================================
echo.

cd /d "%~dp0"

echo Testing imports...
python -c "import sys; sys.path.insert(0, '.'); from agent.advanced_agent import AdvancedTourAgent; print('✅ Imports OK')" 2>&1
if errorlevel 1 (
    echo ❌ Import failed! Check Python environment
    pause
    exit /b 1
)

echo.
echo Starting Flask server...
cd ui
python app.py

pause
