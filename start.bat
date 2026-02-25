@echo off
REM AI Personal Finance Copilot - Windows Startup Script (Fixed)

echo ========================================
echo AI Personal Finance Copilot - Quick Start
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from python.org
    pause
    exit /b 1
)

echo [OK] Python found

REM Upgrade pip first (fixes most installation issues)
echo.
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel

REM Install backend dependencies
echo.
echo Installing backend dependencies...
cd backend

REM Try to install packages one by one to identify issues
echo Installing FastAPI...
pip install fastapi==0.104.1
echo Installing Uvicorn...
pip install uvicorn==0.24.0
echo Installing Pandas (this may take a minute)...
pip install pandas
echo Installing remaining packages...
pip install python-multipart pydantic python-dotenv

if errorlevel 1 (
    echo.
    echo [WARNING] Some packages may have failed to install
    echo The app might still work. Let's try to start it...
    echo.
)

echo [OK] Installation complete

REM Start backend
echo.
echo Starting backend server on http://localhost:8000...
start "Finance Copilot Backend" cmd /k python main.py

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend server on http://localhost:3000...
cd ..\frontend
start "Finance Copilot Frontend" cmd /k python -m http.server 3000

echo.
echo ========================================
echo [SUCCESS] Application is running!
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Sample data: ..\data\sample_transactions.csv
echo.
echo Close the command windows to stop servers
echo ========================================
echo.
pause
