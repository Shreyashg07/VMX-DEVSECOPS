@echo off
title Backend Server

REM Go to backend folder
cd /d "%~dp0\backend"

echo 🚀 Activating virtual environment...
call .\.venv\Scripts\activate

echo 🚀 Starting backend...
python app.py

pause
