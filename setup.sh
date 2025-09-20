#!/bin/bash

echo "🚂 Railway Traffic Optimization System Setup"
echo "==========================================="
echo

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

echo
echo "🤖 Training ML models..."
python train_ml_model.py
if [ $? -ne 0 ]; then
    echo "⚠️ ML model training failed, but continuing..."
fi

echo
echo "📦 Installing frontend dependencies..."
cd railway-optimization
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi

echo
echo "🏗️ Building frontend..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Failed to build frontend"
    exit 1
fi

cd ..

echo
echo "✅ Setup complete! Starting the application..."
echo
echo "🌐 The application will be available at: http://localhost:8000"
echo "📚 API documentation: http://localhost:8000/docs"
echo
echo "Press Ctrl+C to stop the server"
echo

python app.py
