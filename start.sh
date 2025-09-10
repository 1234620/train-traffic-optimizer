#!/bin/bash

echo "🚂 Train Traffic Throughput Maximization System"
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

echo "🐳 Starting services with Docker Compose..."
docker-compose up --build -d

echo ""
echo "✅ Services started successfully!"
echo ""
echo "🌐 Access the application:"
echo "   - Frontend: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/health"
echo ""
echo "📊 Monitor services:"
echo "   docker-compose ps"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
