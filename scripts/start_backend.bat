@echo off
cd /d "%~dp0\..\backend"
call venv\Scripts\activate.bat
echo Starting FastAPI on http://127.0.0.1:8000
echo API docs: http://127.0.0.1:8000/docs
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
