@echo off
echo Stopping Emotion Music processes on ports 8000 and 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do taskkill /PID %%a /F 2>nul
echo Done.
pause
