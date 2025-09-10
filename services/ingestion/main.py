"""
RTIS/COA Data Ingestion Service

This service handles real-time data ingestion from:
- RTIS (Real Time Information System) devices
- COA (Control Office Applications) feeds
- NTES (National Train Enquiry System) data
- Weather and disruption feeds
- Sensor data from tracks and signals
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import redis
import kafka
from kafka import KafkaProducer, KafkaConsumer
import structlog
from pydantic import BaseModel, Field

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class TrainEventType(Enum):
    """Types of train events from RTIS/COA"""
    ARRIVAL = "arrival"
    DEPARTURE = "departure"
    RUN_THROUGH = "run_through"
    SPEED_CHANGE = "speed_change"
    EMERGENCY_STOP = "emergency_stop"
    SIGNAL_ASPECT = "signal_aspect"
    TRACK_OCCUPANCY = "track_occupancy"


class TrainStatus(Enum):
    """Train operational status"""
    ON_TIME = "on_time"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    DIVERTED = "diverted"
    TERMINATED = "terminated"


@dataclass
class TrainPosition:
    """Train position data from RTIS"""
    train_id: str
    latitude: float
    longitude: float
    speed: float  # km/h
    direction: str  # "up" or "down"
    section_id: str
    station_id: Optional[str]
    timestamp: datetime
    accuracy: float  # GPS accuracy in meters


@dataclass
class TrainEvent:
    """Train event from RTIS/COA"""
    event_id: str
    train_id: str
    event_type: TrainEventType
    station_id: str
    platform: Optional[int]
    scheduled_time: datetime
    actual_time: datetime
    delay_minutes: int
    status: TrainStatus
    additional_data: Dict[str, Any]


class RTISDataModel(BaseModel):
    """Pydantic model for RTIS data validation"""
    train_id: str = Field(..., description="Unique train identifier")
    position: TrainPosition
    events: List[TrainEvent]
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data_quality: float = Field(ge=0.0, le=1.0, description="Data quality score 0-1")


class DataIngestionService:
    """Main service for ingesting RTIS/COA data"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            decode_responses=True
        )
        
        # Kafka setup for real-time data streaming
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=config.get('kafka_servers', ['localhost:9092']),
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        self.kafka_consumer = KafkaConsumer(
            'rtis_events',
            bootstrap_servers=config.get('kafka_servers', ['localhost:9092']),
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='ingestion_service'
        )
        
        # Data quality thresholds
        self.position_accuracy_threshold = config.get('position_accuracy_threshold', 50.0)  # meters
        self.max_delay_threshold = config.get('max_delay_threshold', 300)  # 5 minutes
        
    async def start_ingestion(self):
        """Start the data ingestion process"""
        logger.info("Starting RTIS/COA data ingestion service")
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._consume_rtis_events()),
            asyncio.create_task(self._consume_coa_events()),
            asyncio.create_task(self._consume_weather_events()),
            asyncio.create_task(self._consume_disruption_events()),
            asyncio.create_task(self._data_quality_monitor()),
        ]
        
        await asyncio.gather(*tasks)
    
    async def _consume_rtis_events(self):
        """Consume and process RTIS events"""
        logger.info("Starting RTIS event consumption")
        
        for message in self.kafka_consumer:
            try:
                event_data = message.value
                await self._process_rtis_event(event_data)
            except Exception as e:
                logger.error("Error processing RTIS event", error=str(e), event=message.value)
    
    async def _consume_coa_events(self):
        """Consume and process COA control events"""
        logger.info("Starting COA event consumption")
        
        # Simulate COA event consumption
        while True:
            try:
                # In production, this would connect to actual COA feeds
                await asyncio.sleep(1)
                # Process COA events here
            except Exception as e:
                logger.error("Error processing COA event", error=str(e))
                await asyncio.sleep(5)
    
    async def _consume_weather_events(self):
        """Consume weather and environmental data"""
        logger.info("Starting weather event consumption")
        
        while True:
            try:
                # In production, this would connect to weather APIs
                await asyncio.sleep(30)
                # Process weather events here
            except Exception as e:
                logger.error("Error processing weather event", error=str(e))
                await asyncio.sleep(30)
    
    async def _consume_disruption_events(self):
        """Consume disruption and incident data"""
        logger.info("Starting disruption event consumption")
        
        while True:
            try:
                # In production, this would connect to incident reporting systems
                await asyncio.sleep(10)
                # Process disruption events here
            except Exception as e:
                logger.error("Error processing disruption event", error=str(e))
                await asyncio.sleep(10)
    
    async def _process_rtis_event(self, event_data: Dict[str, Any]):
        """Process individual RTIS event"""
        try:
            # Validate event data
            rtis_data = RTISDataModel(**event_data)
            
            # Check data quality
            if not self._validate_data_quality(rtis_data):
                logger.warning("Low quality RTIS data received", train_id=rtis_data.train_id)
                return
            
            # Store in Redis for real-time access
            await self._store_realtime_data(rtis_data)
            
            # Publish to decision engine
            await self._publish_to_decision_engine(rtis_data)
            
            # Update metrics
            await self._update_metrics(rtis_data)
            
            logger.info("RTIS event processed successfully", 
                       train_id=rtis_data.train_id,
                       events_count=len(rtis_data.events))
            
        except Exception as e:
            logger.error("Error processing RTIS event", error=str(e), event=event_data)
    
    def _validate_data_quality(self, rtis_data: RTISDataModel) -> bool:
        """Validate data quality based on thresholds"""
        # Check position accuracy
        if rtis_data.position.accuracy > self.position_accuracy_threshold:
            return False
        
        # Check for stale data
        time_diff = datetime.now(timezone.utc) - rtis_data.last_updated
        if time_diff.total_seconds() > self.max_delay_threshold:
            return False
        
        # Check for missing critical data
        if not rtis_data.train_id or not rtis_data.position:
            return False
        
        return True
    
    async def _store_realtime_data(self, rtis_data: RTISDataModel):
        """Store data in Redis for real-time access"""
        key = f"train:{rtis_data.train_id}:position"
        data = {
            "train_id": rtis_data.train_id,
            "latitude": rtis_data.position.latitude,
            "longitude": rtis_data.position.longitude,
            "speed": rtis_data.position.speed,
            "direction": rtis_data.position.direction,
            "section_id": rtis_data.position.section_id,
            "station_id": rtis_data.position.station_id,
            "timestamp": rtis_data.position.timestamp.isoformat(),
            "accuracy": rtis_data.position.accuracy,
            "data_quality": rtis_data.data_quality
        }
        
        self.redis_client.hset(key, mapping=data)
        self.redis_client.expire(key, 3600)  # Expire after 1 hour
    
    async def _publish_to_decision_engine(self, rtis_data: RTISDataModel):
        """Publish processed data to decision engine"""
        topic = "train_events_processed"
        message = {
            "train_id": rtis_data.train_id,
            "position": {
                "latitude": rtis_data.position.latitude,
                "longitude": rtis_data.position.longitude,
                "speed": rtis_data.position.speed,
                "direction": rtis_data.position.direction,
                "section_id": rtis_data.position.section_id,
                "station_id": rtis_data.position.station_id,
                "timestamp": rtis_data.position.timestamp.isoformat(),
                "accuracy": rtis_data.position.accuracy
            },
            "events": [
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "station_id": event.station_id,
                    "platform": event.platform,
                    "scheduled_time": event.scheduled_time.isoformat(),
                    "actual_time": event.actual_time.isoformat(),
                    "delay_minutes": event.delay_minutes,
                    "status": event.status.value,
                    "additional_data": event.additional_data
                }
                for event in rtis_data.events
            ],
            "data_quality": rtis_data.data_quality,
            "last_updated": rtis_data.last_updated.isoformat()
        }
        
        self.kafka_producer.send(topic, value=message, key=rtis_data.train_id)
    
    async def _update_metrics(self, rtis_data: RTISDataModel):
        """Update monitoring metrics"""
        # Update train count
        self.redis_client.incr("metrics:trains_processed")
        
        # Update data quality metrics
        self.redis_client.lpush("metrics:data_quality", rtis_data.data_quality)
        self.redis_client.ltrim("metrics:data_quality", 0, 999)  # Keep last 1000 values
        
        # Update delay metrics
        for event in rtis_data.events:
            if event.delay_minutes > 0:
                self.redis_client.lpush("metrics:delays", event.delay_minutes)
                self.redis_client.ltrim("metrics:delays", 0, 999)
    
    async def _data_quality_monitor(self):
        """Monitor data quality and alert on issues"""
        while True:
            try:
                # Check average data quality
                quality_scores = self.redis_client.lrange("metrics:data_quality", 0, -1)
                if quality_scores:
                    avg_quality = sum(float(score) for score in quality_scores) / len(quality_scores)
                    if avg_quality < 0.8:
                        logger.warning("Low data quality detected", average_quality=avg_quality)
                
                # Check for stale data
                train_keys = self.redis_client.keys("train:*:position")
                current_time = datetime.now(timezone.utc)
                
                for key in train_keys:
                    data = self.redis_client.hgetall(key)
                    if data and 'timestamp' in data:
                        last_update = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                        if (current_time - last_update).total_seconds() > 300:  # 5 minutes
                            logger.warning("Stale train data detected", train_id=data.get('train_id'))
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error("Error in data quality monitor", error=str(e))
                await asyncio.sleep(60)


async def main():
    """Main entry point for the ingestion service"""
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'kafka_servers': ['localhost:9092'],
        'position_accuracy_threshold': 50.0,
        'max_delay_threshold': 300
    }
    
    service = DataIngestionService(config)
    await service.start_ingestion()


if __name__ == "__main__":
    asyncio.run(main())
