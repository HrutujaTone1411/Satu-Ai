@echo off
title Satish AI System Launcher
color 0B
echo ==========================================
echo      INITIALIZING SATISH AI PROTOCOL
echo ==========================================
echo.

echo [1/3] Waking up the Python Brain (Backend)...
:: We navigate to the backend, activate the virtual environment, and start FastAPI
cd backend
start cmd /k "call venv\Scripts\activate && uvicorn main:app"

:: Go back to the main folder
cd ..

echo [2/3] Booting up the React Face (Frontend)...
:: We navigate to the frontend and start Vite
cd frontend
start cmd /k "npm run dev"

echo [3/3] Opening Neural Interface (Browser)...
:: We wait 4 seconds to give the servers time to boot, then open Chrome/Edge
timeout /t 4 /nobreak >nul
start http://localhost:5173/

echo.
echo ==========================================
echo Satish AI is ONLINE. 
echo You can minimize these windows.
echo ==========================================
pause