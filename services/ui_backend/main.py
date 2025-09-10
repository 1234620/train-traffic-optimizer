"""
UI Backend Service

This service provides REST APIs for the React dashboard:
- Real-time train data
- Zone status and metrics
- Safety violations and alerts
- Slot trading information
- Predictive maintenance data
- System health and monitoring
"""

import asyncio
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import structlog
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

logger = structlog.get_logger(__name__)


class TrainData(BaseModel):
    """Train data model for API"""
    train_id: str
    name: str
    type: str
    status: str
    position: Dict[str, float]
    speed: float
    direction: str
    zone: str
    delay: int
    destination: str
    next_station: str
    priority: int
    atp_enabled: bool
    kavach_enabled: bool
    last_updated: datetime


class ZoneStatus(BaseModel):
    """Zone status model for API"""
    zone_id: str
    name: str
    status: str
    train_count: int
    capacity: int
    throughput: float
    average_delay: float
    headway_compliance: float
    last_updated: datetime


class SafetyViolation(BaseModel):
    """Safety violation model for API"""
    violation_id: str
    train_id: str
    violation_type: str
    severity: str
    description: str
    location: Dict[str, float]
    timestamp: datetime
    resolved: bool


class SlotTrade(BaseModel):
    """Slot trade model for API"""
    trade_id: str
    negotiation_id: str
    winning_zone: str
    losing_zone: str
    train_id: str
    slot_time: datetime
    compensation: float
    status: str
    created_at: datetime


class MaintenanceAlert(BaseModel):
    """Maintenance alert model for API"""
    alert_id: str
    asset_id: str
    asset_type: str
    severity: str
    description: str
    location: Dict[str, float]
    section_id: str
    detected_at: datetime
    confidence: float
    maintenance_required: bool


class SystemMetrics(BaseModel):
    """System metrics model for API"""
    total_trains: int
    on_time_trains: int
    delayed_trains: int
    cancelled_trains: int
    average_delay: float
    throughput: float
    safety_violations: int
    slot_trades: int
    maintenance_alerts: int
    system_uptime: float
    data_quality: float
    last_updated: datetime


class UIBackendService:
    """Main UI backend service"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.app = FastAPI(
            title="Train Traffic Throughput Maximization System API",
            description="REST API for the Train Traffic Throughput Maximization System",
            version="1.0.0"
        )
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://localhost:3001"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # WebSocket connections
        self.active_connections: List[WebSocket] = []
        
        # Sample data (in production, this would connect to actual services)
        self.trains: Dict[str, TrainData] = {}
        self.zones: Dict[str, ZoneStatus] = {}
        self.safety_violations: List[SafetyViolation] = []
        self.slot_trades: List[SlotTrade] = []
        self.maintenance_alerts: List[MaintenanceAlert] = []
        self.system_metrics: SystemMetrics = SystemMetrics(
            total_trains=0,
            on_time_trains=0,
            delayed_trains=0,
            cancelled_trains=0,
            average_delay=0.0,
            throughput=0.0,
            safety_violations=0,
            slot_trades=0,
            maintenance_alerts=0,
            system_uptime=0.0,
            data_quality=0.0,
            last_updated=datetime.now(timezone.utc)
        )
        
        # Setup routes
        self._setup_routes()
        
        # Start background tasks
        asyncio.create_task(self._update_data())
        asyncio.create_task(self._broadcast_updates())
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            return {"message": "Train Traffic Throughput Maximization System API", "version": "1.0.0"}
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
        
        # Train data endpoints
        @self.app.get("/api/trains", response_model=List[TrainData])
        async def get_trains():
            """Get all trains"""
            return list(self.trains.values())
        
        @self.app.get("/api/trains/{train_id}", response_model=TrainData)
        async def get_train(train_id: str):
            """Get specific train"""
            if train_id not in self.trains:
                raise HTTPException(status_code=404, detail="Train not found")
            return self.trains[train_id]
        
        @self.app.get("/api/trains/zone/{zone_id}", response_model=List[TrainData])
        async def get_trains_by_zone(zone_id: str):
            """Get trains by zone"""
            return [train for train in self.trains.values() if train.zone == zone_id]
        
        # Zone status endpoints
        @self.app.get("/api/zones", response_model=List[ZoneStatus])
        async def get_zones():
            """Get all zones"""
            return list(self.zones.values())
        
        @self.app.get("/api/zones/{zone_id}", response_model=ZoneStatus)
        async def get_zone(zone_id: str):
            """Get specific zone"""
            if zone_id not in self.zones:
                raise HTTPException(status_code=404, detail="Zone not found")
            return self.zones[zone_id]
        
        # Safety violations endpoints
        @self.app.get("/api/safety/violations", response_model=List[SafetyViolation])
        async def get_safety_violations():
            """Get safety violations"""
            return self.safety_violations
        
        @self.app.get("/api/safety/violations/train/{train_id}", response_model=List[SafetyViolation])
        async def get_safety_violations_by_train(train_id: str):
            """Get safety violations for specific train"""
            return [v for v in self.safety_violations if v.train_id == train_id]
        
        @self.app.post("/api/safety/violations/{violation_id}/resolve")
        async def resolve_safety_violation(violation_id: str):
            """Resolve safety violation"""
            for violation in self.safety_violations:
                if violation.violation_id == violation_id:
                    violation.resolved = True
                    return {"message": "Violation resolved"}
            raise HTTPException(status_code=404, detail="Violation not found")
        
        # Slot trading endpoints
        @self.app.get("/api/slot-trading/trades", response_model=List[SlotTrade])
        async def get_slot_trades():
            """Get slot trades"""
            return self.slot_trades
        
        @self.app.get("/api/slot-trading/trades/zone/{zone_id}", response_model=List[SlotTrade])
        async def get_slot_trades_by_zone(zone_id: str):
            """Get slot trades by zone"""
            return [trade for trade in self.slot_trades 
                   if trade.winning_zone == zone_id or trade.losing_zone == zone_id]
        
        # Maintenance alerts endpoints
        @self.app.get("/api/maintenance/alerts", response_model=List[MaintenanceAlert])
        async def get_maintenance_alerts():
            """Get maintenance alerts"""
            return self.maintenance_alerts
        
        @self.app.get("/api/maintenance/alerts/zone/{zone_id}", response_model=List[MaintenanceAlert])
        async def get_maintenance_alerts_by_zone(zone_id: str):
            """Get maintenance alerts by zone"""
            return [alert for alert in self.maintenance_alerts 
                   if alert.section_id.startswith(zone_id)]
        
        # System metrics endpoints
        @self.app.get("/api/metrics", response_model=SystemMetrics)
        async def get_system_metrics():
            """Get system metrics"""
            return self.system_metrics
        
        @self.app.get("/api/metrics/throughput")
        async def get_throughput_metrics():
            """Get throughput metrics over time"""
            # Generate sample throughput data
            now = datetime.now(timezone.utc)
            data = []
            for i in range(24):
                timestamp = now - timedelta(hours=i)
                data.append({
                    "timestamp": timestamp.isoformat(),
                    "throughput": 80 + (i % 10) * 2,
                    "zone_1": 85 + (i % 8) * 2,
                    "zone_2": 75 + (i % 12) * 2,
                    "zone_3": 90 + (i % 6) * 2
                })
            return data
        
        @self.app.get("/api/metrics/delays")
        async def get_delay_metrics():
            """Get delay metrics over time"""
            # Generate sample delay data
            now = datetime.now(timezone.utc)
            data = []
            for i in range(24):
                timestamp = now - timedelta(hours=i)
                data.append({
                    "timestamp": timestamp.isoformat(),
                    "average_delay": 5 + (i % 8) * 2,
                    "max_delay": 15 + (i % 12) * 3,
                    "delayed_trains": 10 + (i % 6) * 2
                })
            return data
        
        # WebSocket endpoint for real-time updates
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)
            try:
                while True:
                    # Keep connection alive
                    await websocket.receive_text()
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
    
    async def _update_data(self):
        """Update sample data periodically"""
        while True:
            try:
                # Update trains
                await self._update_trains()
                
                # Update zones
                await self._update_zones()
                
                # Update safety violations
                await self._update_safety_violations()
                
                # Update slot trades
                await self._update_slot_trades()
                
                # Update maintenance alerts
                await self._update_maintenance_alerts()
                
                # Update system metrics
                await self._update_system_metrics()
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error("Error updating data", error=str(e))
                await asyncio.sleep(5)
    
    async def _update_trains(self):
        """Update train data"""
        # Generate sample train data
        train_types = ['express', 'superfast', 'freight', 'local', 'mail']
        statuses = ['on_time', 'delayed', 'emergency', 'maintenance']
        zones = ['Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5']
        
        for i in range(20):  # 20 sample trains
            train_id = f"train_{i:05d}"
            if train_id not in self.trains:
                self.trains[train_id] = TrainData(
                    train_id=train_id,
                    name=f"Train {i+1}",
                    type=train_types[i % len(train_types)],
                    status=statuses[i % len(statuses)],
                    position={
                        "latitude": 28.6139 + (i * 0.01),
                        "longitude": 77.2090 + (i * 0.01)
                    },
                    speed=80 + (i * 5),
                    direction="north" if i % 2 == 0 else "south",
                    zone=zones[i % len(zones)],
                    delay=i * 2,
                    destination=f"Destination {i+1}",
                    next_station=f"Station {i+1}",
                    priority=i % 10 + 1,
                    atp_enabled=True,
                    kavach_enabled=True,
                    last_updated=datetime.now(timezone.utc)
                )
            else:
                # Update existing train
                train = self.trains[train_id]
                train.speed = max(0, train.speed + (i % 3 - 1) * 5)
                train.delay = max(0, train.delay + (i % 5 - 2))
                train.last_updated = datetime.now(timezone.utc)
    
    async def _update_zones(self):
        """Update zone data"""
        zones = ['Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5']
        statuses = ['normal', 'congested', 'maintenance', 'emergency']
        
        for i, zone_name in enumerate(zones):
            zone_id = f"zone_{i+1:03d}"
            if zone_id not in self.zones:
                self.zones[zone_id] = ZoneStatus(
                    zone_id=zone_id,
                    name=zone_name,
                    status=statuses[i % len(statuses)],
                    train_count=10 + i * 2,
                    capacity=20 + i * 5,
                    throughput=80 + i * 3,
                    average_delay=5 + i * 2,
                    headway_compliance=90 + i * 2,
                    last_updated=datetime.now(timezone.utc)
                )
            else:
                # Update existing zone
                zone = self.zones[zone_id]
                zone.train_count = max(0, zone.train_count + (i % 3 - 1))
                zone.throughput = max(0, min(100, zone.throughput + (i % 5 - 2)))
                zone.average_delay = max(0, zone.average_delay + (i % 4 - 2))
                zone.last_updated = datetime.now(timezone.utc)
    
    async def _update_safety_violations(self):
        """Update safety violations"""
        # Generate sample safety violations
        if len(self.safety_violations) < 5:
            violation_types = ['speed_excess', 'signal_violation', 'braking_distance', 'track_occupancy']
            severities = ['low', 'medium', 'high', 'critical']
            
            for i in range(3):
                violation = SafetyViolation(
                    violation_id=f"violation_{len(self.safety_violations) + 1:05d}",
                    train_id=f"train_{i:05d}",
                    violation_type=violation_types[i % len(violation_types)],
                    severity=severities[i % len(severities)],
                    description=f"Safety violation {i+1}",
                    location={
                        "latitude": 28.6139 + i * 0.01,
                        "longitude": 77.2090 + i * 0.01
                    },
                    timestamp=datetime.now(timezone.utc),
                    resolved=False
                )
                self.safety_violations.append(violation)
    
    async def _update_slot_trades(self):
        """Update slot trades"""
        # Generate sample slot trades
        if len(self.slot_trades) < 10:
            zones = ['Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5']
            statuses = ['pending', 'accepted', 'completed', 'rejected']
            
            for i in range(5):
                trade = SlotTrade(
                    trade_id=f"trade_{len(self.slot_trades) + 1:05d}",
                    negotiation_id=f"negotiation_{i:05d}",
                    winning_zone=zones[i % len(zones)],
                    losing_zone=zones[(i + 1) % len(zones)],
                    train_id=f"train_{i:05d}",
                    slot_time=datetime.now(timezone.utc) + timedelta(minutes=30),
                    compensation=1000 + i * 500,
                    status=statuses[i % len(statuses)],
                    created_at=datetime.now(timezone.utc)
                )
                self.slot_trades.append(trade)
    
    async def _update_maintenance_alerts(self):
        """Update maintenance alerts"""
        # Generate sample maintenance alerts
        if len(self.maintenance_alerts) < 8:
            asset_types = ['track', 'signal', 'bridge', 'tunnel', 'platform']
            severities = ['low', 'medium', 'high', 'critical']
            
            for i in range(4):
                alert = MaintenanceAlert(
                    alert_id=f"alert_{len(self.maintenance_alerts) + 1:05d}",
                    asset_id=f"asset_{i:05d}",
                    asset_type=asset_types[i % len(asset_types)],
                    severity=severities[i % len(severities)],
                    description=f"Maintenance alert {i+1}",
                    location={
                        "latitude": 28.6139 + i * 0.01,
                        "longitude": 77.2090 + i * 0.01
                    },
                    section_id=f"section_{i:03d}",
                    detected_at=datetime.now(timezone.utc),
                    confidence=0.8 + i * 0.05,
                    maintenance_required=i % 2 == 0
                )
                self.maintenance_alerts.append(alert)
    
    async def _update_system_metrics(self):
        """Update system metrics"""
        # Calculate metrics from current data
        total_trains = len(self.trains)
        on_time_trains = len([t for t in self.trains.values() if t.status == 'on_time'])
        delayed_trains = len([t for t in self.trains.values() if t.status == 'delayed'])
        cancelled_trains = len([t for t in self.trains.values() if t.status == 'cancelled'])
        
        average_delay = sum(t.delay for t in self.trains.values()) / max(total_trains, 1)
        throughput = sum(z.throughput for z in self.zones.values()) / max(len(self.zones), 1)
        
        self.system_metrics = SystemMetrics(
            total_trains=total_trains,
            on_time_trains=on_time_trains,
            delayed_trains=delayed_trains,
            cancelled_trains=cancelled_trains,
            average_delay=average_delay,
            throughput=throughput,
            safety_violations=len(self.safety_violations),
            slot_trades=len(self.slot_trades),
            maintenance_alerts=len(self.maintenance_alerts),
            system_uptime=99.9,  # Placeholder
            data_quality=95.0,  # Placeholder
            last_updated=datetime.now(timezone.utc)
        )
    
    async def _broadcast_updates(self):
        """Broadcast updates to WebSocket connections"""
        while True:
            try:
                if self.active_connections:
                    # Prepare update data
                    update_data = {
                        "type": "update",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "trains": len(self.trains),
                        "zones": len(self.zones),
                        "safety_violations": len(self.safety_violations),
                        "slot_trades": len(self.slot_trades),
                        "maintenance_alerts": len(self.maintenance_alerts)
                    }
                    
                    # Send to all connected clients
                    for connection in self.active_connections.copy():
                        try:
                            await connection.send_text(json.dumps(update_data))
                        except:
                            self.active_connections.remove(connection)
                
                await asyncio.sleep(10)  # Broadcast every 10 seconds
                
            except Exception as e:
                logger.error("Error broadcasting updates", error=str(e))
                await asyncio.sleep(10)
    
    async def start(self):
        """Start the UI backend service"""
        logger.info("Starting UI backend service")
        
        # Start the FastAPI server
        config = uvicorn.Config(
            app=self.app,
            host=self.config.get('host', '0.0.0.0'),
            port=self.config.get('port', 8000),
            log_level='info'
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    async def stop(self):
        """Stop the UI backend service"""
        logger.info("Stopping UI backend service")
        # Close all WebSocket connections
        for connection in self.active_connections:
            await connection.close()
        self.active_connections.clear()


async def main():
    """Main entry point for UI backend service"""
    config = {
        'host': '0.0.0.0',
        'port': 8000
    }
    
    service = UIBackendService(config)
    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
