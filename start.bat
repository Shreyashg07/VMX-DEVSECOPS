@echo off
title Frontend Dev Server

REM Always start from this bat file's folder
cd /d "%~dp0"

echo 🚀 Starting Frontend...

REM Go to frontend folder
cd frontendx

REM Start Vite/React
npm run dev

pause
