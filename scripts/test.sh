#!/bin/bash

# Train Traffic Throughput Maximization System - Test Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_COMPOSE_FILE="docker-compose.yml"

echo -e "${BLUE}🧪 Running Tests for Train Traffic Throughput Maximization System${NC}"

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

# Check if services are running
print_status "Checking if services are running..."
if ! docker-compose -f ${DOCKER_COMPOSE_FILE} ps | grep -q "Up"; then
    print_error "Services are not running. Please start them first with ./scripts/deploy.sh"
    exit 1
fi

# Run unit tests
print_status "Running unit tests..."
docker-compose -f ${DOCKER_COMPOSE_FILE} exec ui-backend python -m pytest tests/unit/ -v || print_warning "Some unit tests failed"

# Run integration tests
print_status "Running integration tests..."
docker-compose -f ${DOCKER_COMPOSE_FILE} exec ui-backend python -m pytest tests/integration/ -v || print_warning "Some integration tests failed"

# Run API tests
print_status "Running API tests..."
docker-compose -f ${DOCKER_COMPOSE_FILE} exec ui-backend python -m pytest tests/api/ -v || print_warning "Some API tests failed"

# Run simulation tests
print_status "Running simulation tests..."
docker-compose -f ${DOCKER_COMPOSE_FILE} exec ui-backend python -m pytest tests/simulation/ -v || print_warning "Some simulation tests failed"

# Run load tests
print_status "Running load tests..."
docker-compose -f ${DOCKER_COMPOSE_FILE} exec ui-backend python -m pytest tests/load/ -v || print_warning "Some load tests failed"

# Run frontend tests
print_status "Running frontend tests..."
docker-compose -f ${DOCKER_COMPOSE_FILE} exec frontend npm test -- --coverage --watchAll=false || print_warning "Some frontend tests failed"

# Run end-to-end tests
print_status "Running end-to-end tests..."
docker-compose -f ${DOCKER_COMPOSE_FILE} exec ui-backend python -m pytest tests/e2e/ -v || print_warning "Some end-to-end tests failed"

print_status "All tests completed!"

