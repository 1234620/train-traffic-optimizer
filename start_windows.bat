@echo off
echo 🚂 Train Traffic Throughput Maximization System
echo ==================================================
echo.

echo 🔍 Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python found
echo.

echo 🔍 Checking if backend dependencies are installed...
python -c "import fastapi, uvicorn" 2>nul
if %errorlevel% neq 0 (
    echo 📦 Installing Python dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install Python dependencies
        pause
        exit /b 1
    )
)

echo ✅ Python dependencies ready
echo.

echo 🚀 Starting backend server...
start "Backend Server" cmd /k "python app.py"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo 🌐 Backend should be running at http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/api/docs
echo.

echo 🎉 System started successfully!
echo ==================================================
echo 🌐 Frontend: http://localhost:8000 (served by backend)
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/api/docs
echo ==================================================
echo.
echo Press any key to stop the backend server...
pause >nul

echo 🛑 Stopping backend server...
taskkill /f /im python.exe >nul 2>&1
echo ✅ Backend stopped
echo 👋 System shutdown complete
