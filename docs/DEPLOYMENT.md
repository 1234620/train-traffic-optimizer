# Train Traffic Throughput Maximization System - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Train Traffic Throughput Maximization System in various environments.

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows 10+
- **Memory**: Minimum 8GB RAM, Recommended 16GB RAM
- **Storage**: Minimum 50GB free space
- **CPU**: Minimum 4 cores, Recommended 8 cores
- **Network**: Stable internet connection

### Software Requirements

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: For cloning the repository
- **Make**: For running build commands (optional)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/train-traffic-optimizer.git
cd train-traffic-optimizer
```

### 2. Deploy with Docker Compose

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Deploy the system
./scripts/deploy.sh

# Or deploy with tests
./scripts/deploy.sh --test
```

### 3. Access the System

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

## Detailed Deployment

### Environment Configuration

#### 1. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
# Environment
ENVIRONMENT=production

# Database
POSTGRES_DB=train_traffic
POSTGRES_USER=train_traffic
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_PASSWORD=your_redis_password

# Kafka
KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://your-domain.com:9092

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
REACT_APP_API_URL=https://your-domain.com/api

# Monitoring
GRAFANA_ADMIN_PASSWORD=your_grafana_password
PROMETHEUS_RETENTION_TIME=200h
```

#### 2. Configure SSL/TLS (Production)

For production deployment, configure SSL certificates:

```bash
# Create SSL directory
mkdir -p ssl

# Copy your SSL certificates
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem
```

Update `nginx.conf` to use SSL:

```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... rest of configuration
}
```

### Service-Specific Deployment

#### 1. Data Ingestion Service

```bash
# Deploy only ingestion service
docker-compose up -d redis kafka postgres ingestion
```

#### 2. Decision Engine

```bash
# Deploy decision engine with dependencies
docker-compose up -d redis kafka decision-engine
```

#### 3. Safety Validator

```bash
# Deploy safety validator
docker-compose up -d redis kafka safety-validator
```

#### 4. Slot Trading Service

```bash
# Deploy slot trading service
docker-compose up -d redis kafka slot-trading
```

#### 5. Predictive Maintenance

```bash
# Deploy predictive maintenance service
docker-compose up -d redis kafka predictive-maintenance
```

#### 6. UI Backend

```bash
# Deploy UI backend
docker-compose up -d redis kafka ui-backend
```

#### 7. Frontend

```bash
# Deploy frontend
docker-compose up -d frontend
```

### Production Deployment

#### 1. Use Production Docker Compose

```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d
```

#### 2. Configure Load Balancer

For high availability, use a load balancer (e.g., Nginx, HAProxy):

```nginx
upstream api_backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    location /api/ {
        proxy_pass http://api_backend;
    }
}
```

#### 3. Configure Monitoring

Set up monitoring with Prometheus and Grafana:

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'train-traffic-api'
    static_configs:
      - targets: ['ui-backend:8000']
```

#### 4. Configure Logging

Set up centralized logging with ELK stack:

```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"

  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
```

### Kubernetes Deployment

#### 1. Create Namespace

```bash
kubectl create namespace train-traffic
```

#### 2. Deploy Services

```bash
# Deploy all services
kubectl apply -f k8s/

# Or deploy individually
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/kafka.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/ingestion.yaml
kubectl apply -f k8s/decision-engine.yaml
kubectl apply -f k8s/safety-validator.yaml
kubectl apply -f k8s/slot-trading.yaml
kubectl apply -f k8s/predictive-maintenance.yaml
kubectl apply -f k8s/ui-backend.yaml
kubectl apply -f k8s/frontend.yaml
```

#### 3. Configure Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: train-traffic-ingress
spec:
  rules:
  - host: train-traffic.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 3000
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: ui-backend-service
            port:
              number: 8000
```

### Cloud Deployment

#### AWS ECS

1. **Create ECS Cluster**
```bash
aws ecs create-cluster --cluster-name train-traffic
```

2. **Deploy with ECS Compose**
```bash
ecs-cli compose up --cluster train-traffic
```

#### Google Cloud Run

1. **Build and Push Images**
```bash
gcloud builds submit --tag gcr.io/your-project/train-traffic-api
```

2. **Deploy Services**
```bash
gcloud run deploy train-traffic-api --image gcr.io/your-project/train-traffic-api
```

#### Azure Container Instances

1. **Create Resource Group**
```bash
az group create --name train-traffic --location eastus
```

2. **Deploy Container Group**
```bash
az container create --resource-group train-traffic --name train-traffic --image your-registry/train-traffic:latest
```

### Database Setup

#### 1. Initialize Database

```bash
# Run database migrations
docker-compose exec ui-backend python -m alembic upgrade head
```

#### 2. Seed Initial Data

```bash
# Load sample data
docker-compose exec ui-backend python scripts/seed_data.py
```

### Security Configuration

#### 1. Network Security

```bash
# Create custom network
docker network create train-traffic-network

# Update docker-compose.yml to use custom network
networks:
  train-traffic-network:
    external: true
```

#### 2. Secrets Management

```bash
# Create secrets
docker secret create postgres_password your_password
docker secret create redis_password your_redis_password
```

#### 3. SSL/TLS Configuration

```bash
# Generate self-signed certificate for development
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

### Monitoring and Alerting

#### 1. Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'train-traffic'
    static_configs:
      - targets: ['ui-backend:8000']
```

#### 2. Grafana Dashboards

Import pre-configured dashboards:

```bash
# Import dashboards
curl -X POST http://localhost:3001/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @monitoring/grafana/dashboards/train-traffic.json
```

#### 3. Alert Rules

```yaml
# monitoring/rules/alerts.yml
groups:
- name: train-traffic
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
```

### Backup and Recovery

#### 1. Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U train_traffic train_traffic > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U train_traffic train_traffic < backup.sql
```

#### 2. Configuration Backup

```bash
# Backup configuration
tar -czf config-backup.tar.gz config.json .env docker-compose.yml
```

#### 3. Data Backup

```bash
# Backup all data
docker-compose exec redis redis-cli BGSAVE
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list > kafka-topics.txt
```

### Troubleshooting

#### 1. Check Service Status

```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs ui-backend
```

#### 2. Common Issues

**Service not starting:**
```bash
# Check logs
docker-compose logs service-name

# Restart service
docker-compose restart service-name
```

**Database connection issues:**
```bash
# Check database status
docker-compose exec postgres pg_isready -U train_traffic

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

**Memory issues:**
```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

#### 3. Performance Tuning

**Database optimization:**
```sql
-- Increase shared_buffers
ALTER SYSTEM SET shared_buffers = '256MB';

-- Increase work_mem
ALTER SYSTEM SET work_mem = '4MB';
```

**Redis optimization:**
```bash
# Increase memory limit
echo "maxmemory 512mb" >> redis.conf
echo "maxmemory-policy allkeys-lru" >> redis.conf
```

### Maintenance

#### 1. Regular Updates

```bash
# Update images
docker-compose pull
docker-compose up -d

# Update application code
git pull
docker-compose build
docker-compose up -d
```

#### 2. Log Rotation

```bash
# Configure log rotation
echo "*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}" > /etc/logrotate.d/train-traffic
```

#### 3. Health Checks

```bash
# Add health checks to docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Scaling

#### 1. Horizontal Scaling

```bash
# Scale services
docker-compose up -d --scale ui-backend=3
docker-compose up -d --scale frontend=2
```

#### 2. Load Balancing

```nginx
upstream api_backend {
    server api1:8000 weight=1;
    server api2:8000 weight=1;
    server api3:8000 weight=1;
}
```

#### 3. Database Scaling

```bash
# Add read replicas
docker-compose up -d postgres-read1 postgres-read2
```

### Disaster Recovery

#### 1. Backup Strategy

- **Daily**: Database backups
- **Weekly**: Configuration backups
- **Monthly**: Full system backups

#### 2. Recovery Procedures

```bash
# Full system recovery
docker-compose down
docker-compose up -d postgres
# Restore database
docker-compose up -d
```

#### 3. Failover Procedures

```bash
# Switch to backup system
docker-compose -f docker-compose.backup.yml up -d
```

## Support

For deployment issues, contact:
- **Email**: support@train-traffic-optimizer.com
- **Documentation**: https://docs.train-traffic-optimizer.com
- **Issues**: https://github.com/your-org/train-traffic-optimizer/issues

