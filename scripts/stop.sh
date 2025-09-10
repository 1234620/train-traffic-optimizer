#!/bin/bash

# Train Traffic Throughput Maximization System - Stop Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_COMPOSE_FILE="docker-compose.yml"

echo -e "${BLUE}🛑 Stopping Train Traffic Throughput Maximization System${NC}"

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

# Stop all services
print_status "Stopping all services..."
docker-compose -f ${DOCKER_COMPOSE_FILE} down

# Remove containers
print_status "Removing containers..."
docker-compose -f ${DOCKER_COMPOSE_FILE} rm -f

# Optional: Remove volumes (uncomment if you want to remove all data)
# print_warning "Removing volumes..."
# docker-compose -f ${DOCKER_COMPOSE_FILE} down -v

# Optional: Remove images (uncomment if you want to remove all images)
# print_warning "Removing images..."
# docker-compose -f ${DOCKER_COMPOSE_FILE} down --rmi all

print_status "All services stopped successfully!"
