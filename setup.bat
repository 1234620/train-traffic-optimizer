@echo off
echo 🚂 Railway Traffic Optimization System Setup
echo ===========================================
echo.

echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo 🤖 Training ML models...
python train_ml_model.py
if %errorlevel% neq 0 (
    echo ⚠️ ML model training failed, but continuing...
)

echo.
echo 📦 Installing frontend dependencies...
cd railway-optimization
npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)

echo.
echo 🏗️ Building frontend...
npm run build
if %errorlevel% neq 0 (
    echo ❌ Failed to build frontend
    pause
    exit /b 1
)

cd ..

echo.
echo ✅ Setup complete! Starting the application...
echo.
echo 🌐 The application will be available at: http://localhost:8000
echo 📚 API documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
