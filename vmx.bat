@echo off
title AI CI/CD Security Tool Launcher

REM Always start from project root
cd /d "%~dp0"

echo 🚀 Starting Backend and Frontend...

REM Start Backend in new terminal
start "Backend" cmd /k start1.bat

REM Start Frontend in new terminal
start "Frontend" cmd /k start.bat

echo.
echo ✅ Backend and Frontend launched successfully
