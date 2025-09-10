#!/bin/bash

# Train Traffic Throughput Maximization System - Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="train-traffic-optimizer"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENVIRONMENT=${1:-development}

echo -e "${BLUE}🚀 Deploying Train Traffic Throughput Maximization System${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data/redis
mkdir -p data/postgres
mkdir -p data/kafka
mkdir -p data/prometheus
mkdir -p data/grafana
mkdir -p logs

# Set permissions
chmod 755 data/
chmod 755 logs/

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file..."
    cat > .env << EOF
# Environment
ENVIRONMENT=${ENVIRONMENT}

# Database
POSTGRES_DB=train_traffic
POSTGRES_USER=train_traffic
POSTGRES_PASSWORD=train_traffic_password

# Redis
REDIS_PASSWORD=

# Kafka
KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
REACT_APP_API_URL=http://localhost:8000

# Monitoring
GRAFANA_ADMIN_PASSWORD=admin
PROMETHEUS_RETENTION_TIME=200h
EOF
    print_warning "Please review and update the .env file with your specific configuration."
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f ${DOCKER_COMPOSE_FILE} down --remove-orphans || true

# Remove unused images
print_status "Cleaning up unused Docker images..."
docker image prune -f || true

# Build and start services
print_status "Building and starting services..."
docker-compose -f ${DOCKER_COMPOSE_FILE} up --build -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check Redis
if docker-compose -f ${DOCKER_COMPOSE_FILE} exec -T redis redis-cli ping | grep -q "PONG"; then
    print_status "Redis is healthy"
else
    print_error "Redis is not responding"
fi

# Check PostgreSQL
if docker-compose -f ${DOCKER_COMPOSE_FILE} exec -T postgres pg_isready -U train_traffic; then
    print_status "PostgreSQL is healthy"
else
    print_error "PostgreSQL is not responding"
fi

# Check Kafka
if docker-compose -f ${DOCKER_COMPOSE_FILE} exec -T kafka kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1; then
    print_status "Kafka is healthy"
else
    print_error "Kafka is not responding"
fi

# Check API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "API is healthy"
else
    print_error "API is not responding"
fi

# Check Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_status "Frontend is healthy"
else
    print_error "Frontend is not responding"
fi

# Display service URLs
echo -e "\n${BLUE}🌐 Service URLs:${NC}"
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}API:${NC} http://localhost:8000"
echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
echo -e "${GREEN}Prometheus:${NC} http://localhost:9090"
echo -e "${GREEN}Grafana:${NC} http://localhost:3001 (admin/admin)"

# Display container status
echo -e "\n${BLUE}📊 Container Status:${NC}"
docker-compose -f ${DOCKER_COMPOSE_FILE} ps

# Display logs
echo -e "\n${BLUE}📝 Recent Logs:${NC}"
docker-compose -f ${DOCKER_COMPOSE_FILE} logs --tail=10

print_status "Deployment completed successfully!"
print_warning "Please check the service URLs above to ensure everything is working correctly."

# Optional: Run tests
if [ "$2" = "--test" ]; then
    print_status "Running tests..."
    docker-compose -f ${DOCKER_COMPOSE_FILE} exec ui-backend python -m pytest tests/ || print_warning "Some tests failed"
fi

echo -e "\n${BLUE}🎉 Train Traffic Throughput Maximization System is now running!${NC}"
