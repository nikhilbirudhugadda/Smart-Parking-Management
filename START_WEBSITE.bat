@echo off
title SmartPark - Parking Management System
cd /d "%~dp0"

echo.
echo  =====================================================
echo    SmartPark - Parking Management System
echo  =====================================================
echo.

:: Kill any old server running on port 5000
echo  Stopping any old server...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":5000 " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: Short wait
ping 127.0.0.1 -n 2 >nul

:: Start fresh Flask server in background
echo  Starting fresh server...
start "" /B ".venv\Scripts\python.exe" app.py

:: Wait for it to fully start
ping 127.0.0.1 -n 4 >nul

:: Open browser
start "" "http://127.0.0.1:5000"

echo  Server running at: http://127.0.0.1:5000
echo.
echo  Keep this window open. Close it to stop the server.
echo.
pause
