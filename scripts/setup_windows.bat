@echo off
echo ============================================
echo  Emotion Music Recommender - Windows Setup
echo ============================================
cd /d "%~dp0\.."

echo.
echo [1/6] Creating Python virtual environment...
python -m venv backend\venv
if errorlevel 1 (
  echo Failed to create venv. Ensure Python 3.10+ is installed and on PATH.
  pause
  exit /b 1
)

echo.
echo [2/6] Activating venv and upgrading pip...
call backend\venv\Scripts\activate.bat
python -m pip install --upgrade pip

echo.
echo [3/6] Installing Python dependencies...
pip install -r backend\requirements.txt
if errorlevel 1 (
  echo Dependency install failed.
  pause
  exit /b 1
)

echo.
echo [4/6] Copying .env if missing...
if not exist backend\.env copy backend\.env.example backend\.env

echo.
echo [5/6] Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
  echo npm install failed. Ensure Node.js 18+ is installed.
  cd ..
  pause
  exit /b 1
)
cd ..

echo.
echo [6/6] Setup complete!
echo.
echo To start the app:
echo   1. Backend:  scripts\start_backend.bat
echo   2. Frontend: scripts\start_frontend.bat
echo.
echo Then open http://localhost:5173
pause
