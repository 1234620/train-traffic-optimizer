# Train Traffic Throughput Maximization System - API Documentation

## Overview

The Train Traffic Throughput Maximization System provides a comprehensive REST API for managing train traffic optimization, safety monitoring, slot trading, and predictive maintenance.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, implement proper authentication using JWT tokens or API keys.

## Endpoints

### Health Check

#### GET /health

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Train Data

#### GET /api/trains

Get all trains in the system.

**Response:**
```json
[
  {
    "train_id": "12345",
    "name": "Rajdhani Express",
    "type": "express",
    "status": "on_time",
    "position": {
      "latitude": 28.6139,
      "longitude": 77.2090
    },
    "speed": 120.0,
    "direction": "north",
    "zone": "Zone 1",
    "delay": 0,
    "destination": "New Delhi",
    "next_station": "Delhi Junction",
    "priority": 3,
    "atp_enabled": true,
    "kavach_enabled": true,
    "last_updated": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /api/trains/{train_id}

Get a specific train by ID.

**Parameters:**
- `train_id` (string): The unique identifier of the train

**Response:**
```json
{
  "train_id": "12345",
  "name": "Rajdhani Express",
  "type": "express",
  "status": "on_time",
  "position": {
    "latitude": 28.6139,
    "longitude": 77.2090
  },
  "speed": 120.0,
  "direction": "north",
  "zone": "Zone 1",
  "delay": 0,
  "destination": "New Delhi",
  "next_station": "Delhi Junction",
  "priority": 3,
  "atp_enabled": true,
  "kavach_enabled": true,
  "last_updated": "2024-01-01T00:00:00Z"
}
```

#### GET /api/trains/zone/{zone_id}

Get all trains in a specific zone.

**Parameters:**
- `zone_id` (string): The zone identifier

**Response:**
```json
[
  {
    "train_id": "12345",
    "name": "Rajdhani Express",
    "type": "express",
    "status": "on_time",
    "position": {
      "latitude": 28.6139,
      "longitude": 77.2090
    },
    "speed": 120.0,
    "direction": "north",
    "zone": "Zone 1",
    "delay": 0,
    "destination": "New Delhi",
    "next_station": "Delhi Junction",
    "priority": 3,
    "atp_enabled": true,
    "kavach_enabled": true,
    "last_updated": "2024-01-01T00:00:00Z"
  }
]
```

### Zone Status

#### GET /api/zones

Get all zones in the system.

**Response:**
```json
[
  {
    "zone_id": "zone_001",
    "name": "Zone 1",
    "status": "normal",
    "train_count": 15,
    "capacity": 20,
    "throughput": 85.0,
    "average_delay": 5.0,
    "headway_compliance": 95.0,
    "last_updated": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /api/zones/{zone_id}

Get a specific zone by ID.

**Parameters:**
- `zone_id` (string): The zone identifier

**Response:**
```json
{
  "zone_id": "zone_001",
  "name": "Zone 1",
  "status": "normal",
  "train_count": 15,
  "capacity": 20,
  "throughput": 85.0,
  "average_delay": 5.0,
  "headway_compliance": 95.0,
  "last_updated": "2024-01-01T00:00:00Z"
}
```

### Safety Violations

#### GET /api/safety/violations

Get all safety violations.

**Response:**
```json
[
  {
    "violation_id": "violation_001",
    "train_id": "12345",
    "violation_type": "speed_excess",
    "severity": "high",
    "description": "Speed excess: 130 km/h > 120 km/h",
    "location": {
      "latitude": 28.6139,
      "longitude": 77.2090
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "resolved": false
  }
]
```

#### GET /api/safety/violations/train/{train_id}

Get safety violations for a specific train.

**Parameters:**
- `train_id` (string): The train identifier

**Response:**
```json
[
  {
    "violation_id": "violation_001",
    "train_id": "12345",
    "violation_type": "speed_excess",
    "severity": "high",
    "description": "Speed excess: 130 km/h > 120 km/h",
    "location": {
      "latitude": 28.6139,
      "longitude": 77.2090
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "resolved": false
  }
]
```

#### POST /api/safety/violations/{violation_id}/resolve

Resolve a safety violation.

**Parameters:**
- `violation_id` (string): The violation identifier

**Response:**
```json
{
  "message": "Violation resolved"
}
```

### Slot Trading

#### GET /api/slot-trading/trades

Get all slot trades.

**Response:**
```json
[
  {
    "trade_id": "trade_001",
    "negotiation_id": "negotiation_001",
    "winning_zone": "Zone 1",
    "losing_zone": "Zone 2",
    "train_id": "12345",
    "slot_time": "2024-01-01T00:30:00Z",
    "compensation": 1000.0,
    "status": "completed",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /api/slot-trading/trades/zone/{zone_id}

Get slot trades for a specific zone.

**Parameters:**
- `zone_id` (string): The zone identifier

**Response:**
```json
[
  {
    "trade_id": "trade_001",
    "negotiation_id": "negotiation_001",
    "winning_zone": "Zone 1",
    "losing_zone": "Zone 2",
    "train_id": "12345",
    "slot_time": "2024-01-01T00:30:00Z",
    "compensation": 1000.0,
    "status": "completed",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Maintenance Alerts

#### GET /api/maintenance/alerts

Get all maintenance alerts.

**Response:**
```json
[
  {
    "alert_id": "alert_001",
    "asset_id": "track_001",
    "asset_type": "track",
    "severity": "high",
    "description": "Unusual vibration detected in track section",
    "location": {
      "latitude": 28.6139,
      "longitude": 77.2090
    },
    "section_id": "section_001",
    "detected_at": "2024-01-01T00:00:00Z",
    "confidence": 0.85,
    "maintenance_required": true
  }
]
```

#### GET /api/maintenance/alerts/zone/{zone_id}

Get maintenance alerts for a specific zone.

**Parameters:**
- `zone_id` (string): The zone identifier

**Response:**
```json
[
  {
    "alert_id": "alert_001",
    "asset_id": "track_001",
    "asset_type": "track",
    "severity": "high",
    "description": "Unusual vibration detected in track section",
    "location": {
      "latitude": 28.6139,
      "longitude": 77.2090
    },
    "section_id": "section_001",
    "detected_at": "2024-01-01T00:00:00Z",
    "confidence": 0.85,
    "maintenance_required": true
  }
]
```

### System Metrics

#### GET /api/metrics

Get system-wide metrics.

**Response:**
```json
{
  "total_trains": 100,
  "on_time_trains": 85,
  "delayed_trains": 10,
  "cancelled_trains": 5,
  "average_delay": 5.5,
  "throughput": 88.5,
  "safety_violations": 3,
  "slot_trades": 15,
  "maintenance_alerts": 8,
  "system_uptime": 99.9,
  "data_quality": 95.0,
  "last_updated": "2024-01-01T00:00:00Z"
}
```

#### GET /api/metrics/throughput

Get throughput metrics over time.

**Response:**
```json
[
  {
    "timestamp": "2024-01-01T00:00:00Z",
    "throughput": 85.0,
    "zone_1": 88.0,
    "zone_2": 82.0,
    "zone_3": 90.0
  }
]
```

#### GET /api/metrics/delays

Get delay metrics over time.

**Response:**
```json
[
  {
    "timestamp": "2024-01-01T00:00:00Z",
    "average_delay": 5.5,
    "max_delay": 15.0,
    "delayed_trains": 10
  }
]
```

## WebSocket

### /ws

WebSocket endpoint for real-time updates.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

**Message Format:**
```json
{
  "type": "update",
  "timestamp": "2024-01-01T00:00:00Z",
  "trains": 100,
  "zones": 5,
  "safety_violations": 3,
  "slot_trades": 15,
  "maintenance_alerts": 8
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a message:

```json
{
  "detail": "Train not found"
}
```

## Rate Limiting

API endpoints are rate limited:
- General API: 10 requests per second
- WebSocket: 5 connections per second

## CORS

The API supports CORS for the following origins:
- `http://localhost:3000`
- `http://localhost:3001`

## Examples

### Using curl

```bash
# Get all trains
curl http://localhost:8000/api/trains

# Get specific train
curl http://localhost:8000/api/trains/12345

# Get zone status
curl http://localhost:8000/api/zones

# Get safety violations
curl http://localhost:8000/api/safety/violations

# Resolve safety violation
curl -X POST http://localhost:8000/api/safety/violations/violation_001/resolve
```

### Using JavaScript

```javascript
// Get all trains
const response = await fetch('http://localhost:8000/api/trains');
const trains = await response.json();

// Get zone status
const zoneResponse = await fetch('http://localhost:8000/api/zones');
const zones = await zoneResponse.json();

// Resolve safety violation
await fetch('http://localhost:8000/api/safety/violations/violation_001/resolve', {
  method: 'POST'
});
```

### Using Python

```python
import requests

# Get all trains
response = requests.get('http://localhost:8000/api/trains')
trains = response.json()

# Get zone status
zone_response = requests.get('http://localhost:8000/api/zones')
zones = zone_response.json()

# Resolve safety violation
requests.post('http://localhost:8000/api/safety/violations/violation_001/resolve')
```
