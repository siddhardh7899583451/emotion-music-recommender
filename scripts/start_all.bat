@echo off
title Emotion Music Recommender - Launcher
cd /d "%~dp0\.."

echo ============================================
echo  Emotion Music Recommender - Starting both
echo ============================================
echo.

if not exist "backend\venv\Scripts\activate.bat" (
  echo [ERROR] backend\venv not found.
  echo Run setup first: scripts\setup_windows.bat
  echo Or: cd backend ^& py -3.12 -m venv venv ^& venv\Scripts\activate ^& pip install -r requirements.txt
  pause
  exit /b 1
)

if not exist "frontend\node_modules" (
  echo [ERROR] frontend\node_modules not found.
  echo Run: cd frontend ^& npm install
  pause
  exit /b 1
)

echo [1/2] Starting backend  http://127.0.0.1:8000
start "EMR Backend" cmd /k "cd /d "%~dp0\..\backend" && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting frontend http://localhost:5173
start "EMR Frontend" cmd /k "cd /d "%~dp0\..\frontend" && npm run dev"

echo.
echo Backend and frontend windows opened.
echo Open in browser: http://localhost:5173
echo API docs:        http://127.0.0.1:8000/docs
echo.
echo Close those two windows or press Ctrl+C in each to stop.
echo.
pause
