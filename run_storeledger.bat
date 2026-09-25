@echo off
title StoreLedger

cd /d "%~dp0"

echo ========================================
echo          StoreLedger
echo ========================================
echo.
echo Starting application...
echo.

if not exist "venv\Scripts\python.exe" (
    echo ERROR: StoreLedger virtual environment was not found.
    echo.
    pause
    exit /b 1
)

start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

"venv\Scripts\python.exe" app.py

echo.
echo StoreLedger has stopped.
pause