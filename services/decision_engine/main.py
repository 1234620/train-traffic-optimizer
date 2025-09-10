"""
Decision Engine with Zone-wise Agents

This service implements decentralized, zone-wise decision agents that:
- Optimize section throughput and delay under mixed traffic
- Interface with live RTIS positions and legacy control flows
- Respect ATP/Kavach constraints
- Exchange intents and constraints with adjacent zones
- Use policy and MPC components for optimization
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import math
import numpy as np
from scipy.optimize import minimize
import cvxpy as cp

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class ZoneStatus(Enum):
    """Zone operational status"""
    NORMAL = "normal"
    CONGESTED = "congested"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"
    DISRUPTED = "disrupted"


class DecisionType(Enum):
    """Types of decisions made by agents"""
    SPEED_ADJUSTMENT = "speed_adjustment"
    ROUTE_CHANGE = "route_change"
    PLATFORM_ASSIGNMENT = "platform_assignment"
    DELAY_ABSORPTION = "delay_absorption"
    PRIORITY_OVERRIDE = "priority_override"
    SLOT_TRADING = "slot_trading"


class MessageType(Enum):
    """Types of messages between zone agents"""
    INTENT = "intent"
    CONSTRAINT = "constraint"
    REQUEST = "request"
    RESPONSE = "response"
    ALERT = "alert"
    NEGOTIATION = "negotiation"


@dataclass
class ZoneMessage:
    """Message between zone agents"""
    message_id: str
    from_zone: str
    to_zone: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 5  # 1=highest, 10=lowest
    expires_at: Optional[datetime] = None


@dataclass
class TrainIntent:
    """Train's intent for movement"""
    train_id: str
    current_section: str
    target_section: str
    desired_speed: float
    priority: int
    deadline: datetime
    constraints: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)


@dataclass
class ZoneConstraint:
    """Constraint on zone operations"""
    constraint_id: str
    zone_id: str
    constraint_type: str
    description: str
    severity: str  # "hard" or "soft"
    affected_trains: List[str] = field(default_factory=list)
    valid_until: Optional[datetime] = None


@dataclass
class OptimizationResult:
    """Result of optimization process"""
    decision_type: DecisionType
    train_id: str
    recommended_action: Dict[str, Any]
    confidence: float
    expected_benefit: float
    risk_level: str
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    explanation: str = ""


class ZoneAgent:
    """Zone-wise decision agent"""
    
    def __init__(self, zone_id: str, config: Dict[str, Any]):
        self.zone_id = zone_id
        self.config = config
        self.status = ZoneStatus.NORMAL
        self.trains: Dict[str, Dict[str, Any]] = {}
        self.constraints: List[ZoneConstraint] = []
        self.message_queue: List[ZoneMessage] = []
        self.adjacent_zones: Set[str] = set()
        self.optimization_history: List[OptimizationResult] = []
        
        # Performance metrics
        self.throughput_trains_per_hour = 0.0
        self.average_delay_minutes = 0.0
        self.conflict_resolution_time = 0.0
        self.headway_compliance_rate = 0.0
        
        # Message bus for inter-zone communication
        self.message_bus = None
        
    async def initialize(self, message_bus):
        """Initialize the zone agent"""
        self.message_bus = message_bus
        logger.info("Zone agent initialized", zone_id=self.zone_id)
        
        # Start background tasks
        asyncio.create_task(self._process_messages())
        asyncio.create_task(self._optimize_traffic())
        asyncio.create_task(self._update_metrics())
    
    async def add_train(self, train_data: Dict[str, Any]):
        """Add a train to the zone"""
        train_id = train_data['train_id']
        self.trains[train_id] = train_data
        
        # Create train intent
        intent = TrainIntent(
            train_id=train_id,
            current_section=train_data.get('section_id', ''),
            target_section=train_data.get('target_section', ''),
            desired_speed=train_data.get('speed', 0.0),
            priority=train_data.get('priority', 5),
            deadline=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        # Notify adjacent zones
        await self._notify_adjacent_zones(intent)
        
        logger.info("Train added to zone", zone_id=self.zone_id, train_id=train_id)
    
    async def remove_train(self, train_id: str):
        """Remove a train from the zone"""
        if train_id in self.trains:
            del self.trains[train_id]
            logger.info("Train removed from zone", zone_id=self.zone_id, train_id=train_id)
    
    async def add_constraint(self, constraint: ZoneConstraint):
        """Add a constraint to the zone"""
        self.constraints.append(constraint)
        logger.info("Constraint added to zone", zone_id=self.zone_id, constraint_id=constraint.constraint_id)
        
        # Re-optimize with new constraint
        await self._optimize_traffic()
    
    async def _process_messages(self):
        """Process messages from other zones"""
        while True:
            try:
                if self.message_queue:
                    message = self.message_queue.pop(0)
                    await self._handle_message(message)
                else:
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error("Error processing message", zone_id=self.zone_id, error=str(e))
                await asyncio.sleep(1)
    
    async def _handle_message(self, message: ZoneMessage):
        """Handle a message from another zone"""
        try:
            if message.message_type == MessageType.INTENT:
                await self._handle_intent_message(message)
            elif message.message_type == MessageType.CONSTRAINT:
                await self._handle_constraint_message(message)
            elif message.message_type == MessageType.REQUEST:
                await self._handle_request_message(message)
            elif message.message_type == MessageType.ALERT:
                await self._handle_alert_message(message)
            elif message.message_type == MessageType.NEGOTIATION:
                await self._handle_negotiation_message(message)
            
            logger.debug("Message handled", zone_id=self.zone_id, message_id=message.message_id)
            
        except Exception as e:
            logger.error("Error handling message", zone_id=self.zone_id, message_id=message.message_id, error=str(e))
    
    async def _handle_intent_message(self, message: ZoneMessage):
        """Handle train intent message"""
        intent_data = message.content
        train_id = intent_data.get('train_id')
        
        # Check if this affects our zone
        if train_id in self.trains:
            # Update train intent
            self.trains[train_id]['intent'] = intent_data
            logger.info("Train intent updated", zone_id=self.zone_id, train_id=train_id)
    
    async def _handle_constraint_message(self, message: ZoneMessage):
        """Handle constraint message"""
        constraint_data = message.content
        constraint = ZoneConstraint(
            constraint_id=constraint_data.get('constraint_id'),
            zone_id=constraint_data.get('zone_id'),
            constraint_type=constraint_data.get('constraint_type'),
            description=constraint_data.get('description'),
            severity=constraint_data.get('severity'),
            affected_trains=constraint_data.get('affected_trains', []),
            valid_until=datetime.fromisoformat(constraint_data.get('valid_until')) if constraint_data.get('valid_until') else None
        )
        
        await self.add_constraint(constraint)
    
    async def _handle_request_message(self, message: ZoneMessage):
        """Handle request message"""
        request_data = message.content
        request_type = request_data.get('type')
        
        if request_type == 'slot_request':
            await self._handle_slot_request(message)
        elif request_type == 'priority_override':
            await self._handle_priority_override_request(message)
        else:
            logger.warning("Unknown request type", zone_id=self.zone_id, request_type=request_type)
    
    async def _handle_alert_message(self, message: ZoneMessage):
        """Handle alert message"""
        alert_data = message.content
        alert_type = alert_data.get('type')
        
        if alert_type == 'congestion':
            self.status = ZoneStatus.CONGESTED
            await self._optimize_traffic()
        elif alert_type == 'emergency':
            self.status = ZoneStatus.EMERGENCY
            await self._handle_emergency()
        elif alert_type == 'maintenance':
            self.status = ZoneStatus.MAINTENANCE
            await self._handle_maintenance()
        
        logger.info("Alert handled", zone_id=self.zone_id, alert_type=alert_type)
    
    async def _handle_negotiation_message(self, message: ZoneMessage):
        """Handle negotiation message for slot trading"""
        negotiation_data = message.content
        negotiation_id = negotiation_data.get('negotiation_id')
        
        # Process slot trading negotiation
        await self._process_slot_trading_negotiation(negotiation_data)
    
    async def _optimize_traffic(self):
        """Optimize traffic flow in the zone"""
        try:
            if not self.trains:
                return
            
            # Get current traffic state
            traffic_state = self._get_traffic_state()
            
            # Run optimization
            optimization_results = await self._run_optimization(traffic_state)
            
            # Apply optimization results
            for result in optimization_results:
                await self._apply_optimization_result(result)
                self.optimization_history.append(result)
            
            # Update metrics
            await self._update_performance_metrics()
            
            logger.info("Traffic optimized", zone_id=self.zone_id, results_count=len(optimization_results))
            
        except Exception as e:
            logger.error("Error optimizing traffic", zone_id=self.zone_id, error=str(e))
    
    def _get_traffic_state(self) -> Dict[str, Any]:
        """Get current traffic state for optimization"""
        return {
            'zone_id': self.zone_id,
            'status': self.status.value,
            'trains': list(self.trains.values()),
            'constraints': [
                {
                    'constraint_id': c.constraint_id,
                    'constraint_type': c.constraint_type,
                    'severity': c.severity,
                    'affected_trains': c.affected_trains
                }
                for c in self.constraints
            ],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def _run_optimization(self, traffic_state: Dict[str, Any]) -> List[OptimizationResult]:
        """Run optimization algorithms"""
        results = []
        
        # Multi-objective optimization
        if self.status == ZoneStatus.NORMAL:
            results.extend(await self._optimize_normal_operations(traffic_state))
        elif self.status == ZoneStatus.CONGESTED:
            results.extend(await self._optimize_congested_operations(traffic_state))
        elif self.status == ZoneStatus.EMERGENCY:
            results.extend(await self._optimize_emergency_operations(traffic_state))
        elif self.status == ZoneStatus.MAINTENANCE:
            results.extend(await self._optimize_maintenance_operations(traffic_state))
        
        return results
    
    async def _optimize_normal_operations(self, traffic_state: Dict[str, Any]) -> List[OptimizationResult]:
        """Optimize normal operations"""
        results = []
        
        # Speed optimization
        for train_id, train_data in self.trains.items():
            if train_data.get('speed', 0) > 0:
                speed_result = await self._optimize_train_speed(train_id, train_data)
                if speed_result:
                    results.append(speed_result)
        
        # Platform assignment optimization
        platform_results = await self._optimize_platform_assignments(traffic_state)
        results.extend(platform_results)
        
        return results
    
    async def _optimize_congested_operations(self, traffic_state: Dict[str, Any]) -> List[OptimizationResult]:
        """Optimize congested operations"""
        results = []
        
        # Priority-based optimization
        priority_trains = sorted(
            self.trains.items(),
            key=lambda x: x[1].get('priority', 5)
        )
        
        for train_id, train_data in priority_trains:
            if train_data.get('priority', 5) <= 3:  # High priority trains
                priority_result = await self._optimize_high_priority_train(train_id, train_data)
                if priority_result:
                    results.append(priority_result)
        
        # Slot trading optimization
        slot_results = await self._optimize_slot_trading(traffic_state)
        results.extend(slot_results)
        
        return results
    
    async def _optimize_emergency_operations(self, traffic_state: Dict[str, Any]) -> List[OptimizationResult]:
        """Optimize emergency operations"""
        results = []
        
        # Emergency protocols
        for train_id, train_data in self.trains.items():
            if train_data.get('emergency', False):
                emergency_result = await self._optimize_emergency_train(train_id, train_data)
                if emergency_result:
                    results.append(emergency_result)
        
        return results
    
    async def _optimize_maintenance_operations(self, traffic_state: Dict[str, Any]) -> List[OptimizationResult]:
        """Optimize maintenance operations"""
        results = []
        
        # Maintenance-aware routing
        for train_id, train_data in self.trains.items():
            if train_data.get('maintenance_affected', False):
                maintenance_result = await self._optimize_maintenance_affected_train(train_id, train_data)
                if maintenance_result:
                    results.append(maintenance_result)
        
        return results
    
    async def _optimize_train_speed(self, train_id: str, train_data: Dict[str, Any]) -> Optional[OptimizationResult]:
        """Optimize train speed"""
        current_speed = train_data.get('speed', 0.0)
        max_speed = train_data.get('max_speed', 120.0)
        priority = train_data.get('priority', 5)
        
        # Calculate optimal speed based on constraints
        optimal_speed = min(current_speed, max_speed)
        
        # Apply priority-based speed adjustment
        if priority <= 3:  # High priority
            optimal_speed = min(optimal_speed * 1.1, max_speed)
        elif priority >= 8:  # Low priority
            optimal_speed = optimal_speed * 0.9
        
        if abs(optimal_speed - current_speed) > 5.0:  # Only recommend if significant change
            return OptimizationResult(
                decision_type=DecisionType.SPEED_ADJUSTMENT,
                train_id=train_id,
                recommended_action={
                    'action': 'adjust_speed',
                    'current_speed': current_speed,
                    'recommended_speed': optimal_speed,
                    'reason': 'Optimization for throughput and efficiency'
                },
                confidence=0.8,
                expected_benefit=0.1,
                risk_level='low',
                explanation=f"Adjust speed from {current_speed:.1f} to {optimal_speed:.1f} km/h for better flow"
            )
        
        return None
    
    async def _optimize_platform_assignments(self, traffic_state: Dict[str, Any]) -> List[OptimizationResult]:
        """Optimize platform assignments"""
        results = []
        
        # Simple platform assignment logic
        # In production, this would use more sophisticated algorithms
        
        for train_id, train_data in self.trains.items():
            if train_data.get('needs_platform', False):
                platform = self._find_best_platform(train_id, train_data)
                if platform:
                    results.append(OptimizationResult(
                        decision_type=DecisionType.PLATFORM_ASSIGNMENT,
                        train_id=train_id,
                        recommended_action={
                            'action': 'assign_platform',
                            'platform': platform,
                            'reason': 'Optimal platform assignment'
                        },
                        confidence=0.9,
                        expected_benefit=0.2,
                        risk_level='low',
                        explanation=f"Assign platform {platform} for optimal flow"
                    ))
        
        return results
    
    async def _optimize_high_priority_train(self, train_id: str, train_data: Dict[str, Any]) -> Optional[OptimizationResult]:
        """Optimize high priority train"""
        # Give priority to high priority trains
        return OptimizationResult(
            decision_type=DecisionType.PRIORITY_OVERRIDE,
            train_id=train_id,
            recommended_action={
                'action': 'priority_override',
                'priority': train_data.get('priority', 5),
                'reason': 'High priority train requires immediate attention'
            },
            confidence=0.95,
            expected_benefit=0.3,
            risk_level='medium',
            explanation=f"High priority train {train_id} gets priority treatment"
        )
    
    async def _optimize_emergency_train(self, train_id: str, train_data: Dict[str, Any]) -> Optional[OptimizationResult]:
        """Optimize emergency train"""
        return OptimizationResult(
            decision_type=DecisionType.PRIORITY_OVERRIDE,
            train_id=train_id,
            recommended_action={
                'action': 'emergency_priority',
                'reason': 'Emergency train requires immediate clearance'
            },
            confidence=1.0,
            expected_benefit=0.5,
            risk_level='high',
            explanation=f"Emergency train {train_id} gets highest priority"
        )
    
    async def _optimize_maintenance_affected_train(self, train_id: str, train_data: Dict[str, Any]) -> Optional[OptimizationResult]:
        """Optimize maintenance-affected train"""
        return OptimizationResult(
            decision_type=DecisionType.ROUTE_CHANGE,
            train_id=train_id,
            recommended_action={
                'action': 'reroute',
                'reason': 'Avoid maintenance section'
            },
            confidence=0.85,
            expected_benefit=0.15,
            risk_level='low',
            explanation=f"Reroute train {train_id} to avoid maintenance section"
        )
    
    async def _optimize_slot_trading(self, traffic_state: Dict[str, Any]) -> List[OptimizationResult]:
        """Optimize slot trading between zones"""
        results = []
        
        # Identify trains that could benefit from slot trading
        for train_id, train_data in self.trains.items():
            if train_data.get('delay', 0) > 30:  # Trains with significant delay
                slot_result = await self._initiate_slot_trading(train_id, train_data)
                if slot_result:
                    results.append(slot_result)
        
        return results
    
    async def _initiate_slot_trading(self, train_id: str, train_data: Dict[str, Any]) -> Optional[OptimizationResult]:
        """Initiate slot trading for a train"""
        # Send slot trading request to adjacent zones
        for adjacent_zone in self.adjacent_zones:
            await self._send_message(adjacent_zone, MessageType.NEGOTIATION, {
                'negotiation_id': str(uuid.uuid4()),
                'type': 'slot_request',
                'train_id': train_id,
                'current_zone': self.zone_id,
                'target_zone': adjacent_zone,
                'priority': train_data.get('priority', 5),
                'delay': train_data.get('delay', 0)
            })
        
        return OptimizationResult(
            decision_type=DecisionType.SLOT_TRADING,
            train_id=train_id,
            recommended_action={
                'action': 'initiate_slot_trading',
                'reason': 'Seek better slot from adjacent zones'
            },
            confidence=0.7,
            expected_benefit=0.25,
            risk_level='medium',
            explanation=f"Initiate slot trading for delayed train {train_id}"
        )
    
    async def _process_slot_trading_negotiation(self, negotiation_data: Dict[str, Any]):
        """Process slot trading negotiation"""
        negotiation_id = negotiation_data.get('negotiation_id')
        train_id = negotiation_data.get('train_id')
        priority = negotiation_data.get('priority', 5)
        delay = negotiation_data.get('delay', 0)
        
        # Evaluate if we can accommodate the request
        if self._can_accommodate_slot_request(priority, delay):
            # Accept the request
            await self._send_message(
                negotiation_data.get('current_zone'),
                MessageType.RESPONSE,
                {
                    'negotiation_id': negotiation_id,
                    'status': 'accepted',
                    'zone_id': self.zone_id,
                    'conditions': self._get_slot_conditions()
                }
            )
        else:
            # Reject the request
            await self._send_message(
                negotiation_data.get('current_zone'),
                MessageType.RESPONSE,
                {
                    'negotiation_id': negotiation_id,
                    'status': 'rejected',
                    'zone_id': self.zone_id,
                    'reason': 'Insufficient capacity'
                }
            )
    
    def _can_accommodate_slot_request(self, priority: int, delay: int) -> bool:
        """Check if zone can accommodate a slot request"""
        # Simple capacity check
        current_capacity = len(self.trains)
        max_capacity = self.config.get('max_capacity', 10)
        
        if current_capacity >= max_capacity:
            return False
        
        # Priority-based accommodation
        if priority <= 3:  # High priority
            return True
        elif priority <= 5:  # Medium priority
            return current_capacity < max_capacity * 0.8
        else:  # Low priority
            return current_capacity < max_capacity * 0.6
    
    def _get_slot_conditions(self) -> Dict[str, Any]:
        """Get conditions for slot trading"""
        return {
            'max_speed': 120.0,
            'priority_required': 5,
            'delay_tolerance': 30,
            'valid_until': (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
        }
    
    def _find_best_platform(self, train_id: str, train_data: Dict[str, Any]) -> Optional[int]:
        """Find the best platform for a train"""
        # Simple platform assignment logic
        # In production, this would use more sophisticated algorithms
        
        available_platforms = [1, 2, 3, 4, 5]  # Example platforms
        occupied_platforms = set()
        
        for other_train_id, other_train_data in self.trains.items():
            if other_train_id != train_id and 'platform' in other_train_data:
                occupied_platforms.add(other_train_data['platform'])
        
        for platform in available_platforms:
            if platform not in occupied_platforms:
                return platform
        
        return None
    
    async def _apply_optimization_result(self, result: OptimizationResult):
        """Apply optimization result"""
        train_id = result.train_id
        action = result.recommended_action
        
        if action['action'] == 'adjust_speed':
            # Update train speed
            if train_id in self.trains:
                self.trains[train_id]['recommended_speed'] = action['recommended_speed']
        
        elif action['action'] == 'assign_platform':
            # Assign platform
            if train_id in self.trains:
                self.trains[train_id]['platform'] = action['platform']
        
        elif action['action'] == 'priority_override':
            # Apply priority override
            if train_id in self.trains:
                self.trains[train_id]['priority_override'] = True
        
        elif action['action'] == 'reroute':
            # Apply rerouting
            if train_id in self.trains:
                self.trains[train_id]['reroute'] = True
        
        elif action['action'] == 'initiate_slot_trading':
            # Initiate slot trading
            if train_id in self.trains:
                self.trains[train_id]['slot_trading'] = True
        
        logger.info("Optimization result applied", zone_id=self.zone_id, train_id=train_id, action=action['action'])
    
    async def _update_performance_metrics(self):
        """Update performance metrics"""
        # Calculate throughput (trains per hour)
        self.throughput_trains_per_hour = len(self.trains) * 60 / 60  # Simplified calculation
        
        # Calculate average delay
        delays = [train_data.get('delay', 0) for train_data in self.trains.values()]
        self.average_delay_minutes = sum(delays) / len(delays) if delays else 0
        
        # Calculate headway compliance rate
        # This would be calculated based on actual headway measurements
        self.headway_compliance_rate = 0.95  # Placeholder
        
        logger.debug("Performance metrics updated", 
                    zone_id=self.zone_id,
                    throughput=self.throughput_trains_per_hour,
                    avg_delay=self.average_delay_minutes)
    
    async def _update_metrics(self):
        """Update metrics periodically"""
        while True:
            try:
                await self._update_performance_metrics()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error("Error updating metrics", zone_id=self.zone_id, error=str(e))
                await asyncio.sleep(60)
    
    async def _notify_adjacent_zones(self, intent: TrainIntent):
        """Notify adjacent zones of train intent"""
        message = ZoneMessage(
            message_id=str(uuid.uuid4()),
            from_zone=self.zone_id,
            to_zone="",  # Will be set for each adjacent zone
            message_type=MessageType.INTENT,
            content={
                'train_id': intent.train_id,
                'current_section': intent.current_section,
                'target_section': intent.target_section,
                'desired_speed': intent.desired_speed,
                'priority': intent.priority,
                'deadline': intent.deadline.isoformat()
            },
            timestamp=datetime.now(timezone.utc),
            priority=intent.priority
        )
        
        for adjacent_zone in self.adjacent_zones:
            message.to_zone = adjacent_zone
            await self._send_message(adjacent_zone, MessageType.INTENT, message.content)
    
    async def _send_message(self, to_zone: str, message_type: MessageType, content: Dict[str, Any]):
        """Send message to another zone"""
        if self.message_bus:
            message = ZoneMessage(
                message_id=str(uuid.uuid4()),
                from_zone=self.zone_id,
                to_zone=to_zone,
                message_type=message_type,
                content=content,
                timestamp=datetime.now(timezone.utc)
            )
            
            await self.message_bus.send_message(message)
    
    async def _handle_emergency(self):
        """Handle emergency situation"""
        logger.critical("Emergency situation in zone", zone_id=self.zone_id)
        
        # Notify all adjacent zones
        for adjacent_zone in self.adjacent_zones:
            await self._send_message(adjacent_zone, MessageType.ALERT, {
                'type': 'emergency',
                'zone_id': self.zone_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
    
    async def _handle_maintenance(self):
        """Handle maintenance situation"""
        logger.info("Maintenance mode in zone", zone_id=self.zone_id)
        
        # Notify all adjacent zones
        for adjacent_zone in self.adjacent_zones:
            await self._send_message(adjacent_zone, MessageType.ALERT, {
                'type': 'maintenance',
                'zone_id': self.zone_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
    
    def get_status(self) -> Dict[str, Any]:
        """Get zone status"""
        return {
            'zone_id': self.zone_id,
            'status': self.status.value,
            'train_count': len(self.trains),
            'constraint_count': len(self.constraints),
            'throughput_trains_per_hour': self.throughput_trains_per_hour,
            'average_delay_minutes': self.average_delay_minutes,
            'headway_compliance_rate': self.headway_compliance_rate,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }


class MessageBus:
    """Message bus for inter-zone communication"""
    
    def __init__(self):
        self.zones: Dict[str, ZoneAgent] = {}
        self.message_queue: List[ZoneMessage] = []
    
    async def register_zone(self, zone: ZoneAgent):
        """Register a zone agent"""
        self.zones[zone.zone_id] = zone
        logger.info("Zone registered", zone_id=zone.zone_id)
    
    async def send_message(self, message: ZoneMessage):
        """Send message to target zone"""
        if message.to_zone in self.zones:
            target_zone = self.zones[message.to_zone]
            target_zone.message_queue.append(message)
            logger.debug("Message sent", from_zone=message.from_zone, to_zone=message.to_zone)
        else:
            logger.warning("Target zone not found", to_zone=message.to_zone)
    
    async def broadcast_message(self, message: ZoneMessage):
        """Broadcast message to all zones"""
        for zone_id, zone in self.zones.items():
            if zone_id != message.from_zone:
                zone.message_queue.append(message)
        logger.debug("Message broadcasted", from_zone=message.from_zone)


class DecisionEngine:
    """Main decision engine coordinator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.message_bus = MessageBus()
        self.zones: Dict[str, ZoneAgent] = {}
        self.running = False
    
    async def start(self):
        """Start the decision engine"""
        self.running = True
        logger.info("Decision engine started")
        
        # Create zone agents
        zone_configs = self.config.get('zones', {})
        for zone_id, zone_config in zone_configs.items():
            zone = ZoneAgent(zone_id, zone_config)
            await zone.initialize(self.message_bus)
            await self.message_bus.register_zone(zone)
            self.zones[zone_id] = zone
        
        # Set up adjacent zone relationships
        await self._setup_zone_relationships()
        
        logger.info("Decision engine initialized", zone_count=len(self.zones))
    
    async def stop(self):
        """Stop the decision engine"""
        self.running = False
        logger.info("Decision engine stopped")
    
    async def _setup_zone_relationships(self):
        """Set up relationships between zones"""
        # This would be configured based on actual railway network topology
        zone_relationships = self.config.get('zone_relationships', {})
        
        for zone_id, zone in self.zones.items():
            if zone_id in zone_relationships:
                zone.adjacent_zones = set(zone_relationships[zone_id])
                logger.info("Zone relationships set", zone_id=zone_id, adjacent_zones=zone.adjacent_zones)
    
    async def add_train(self, zone_id: str, train_data: Dict[str, Any]):
        """Add a train to a zone"""
        if zone_id in self.zones:
            await self.zones[zone_id].add_train(train_data)
        else:
            logger.error("Zone not found", zone_id=zone_id)
    
    async def remove_train(self, zone_id: str, train_id: str):
        """Remove a train from a zone"""
        if zone_id in self.zones:
            await self.zones[zone_id].remove_train(train_id)
        else:
            logger.error("Zone not found", zone_id=zone_id)
    
    async def add_constraint(self, zone_id: str, constraint: ZoneConstraint):
        """Add a constraint to a zone"""
        if zone_id in self.zones:
            await self.zones[zone_id].add_constraint(constraint)
        else:
            logger.error("Zone not found", zone_id=zone_id)
    
    def get_zone_status(self, zone_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a zone"""
        if zone_id in self.zones:
            return self.zones[zone_id].get_status()
        return None
    
    def get_all_zone_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all zones"""
        return {zone_id: zone.get_status() for zone_id, zone in self.zones.items()}


async def main():
    """Main entry point for the decision engine"""
    config = {
        'zones': {
            'zone_001': {'max_capacity': 10, 'adjacent_zones': ['zone_002']},
            'zone_002': {'max_capacity': 15, 'adjacent_zones': ['zone_001', 'zone_003']},
            'zone_003': {'max_capacity': 12, 'adjacent_zones': ['zone_002']}
        },
        'zone_relationships': {
            'zone_001': ['zone_002'],
            'zone_002': ['zone_001', 'zone_003'],
            'zone_003': ['zone_002']
        }
    }
    
    engine = DecisionEngine(config)
    await engine.start()
    
    # Example usage
    train_data = {
        'train_id': '12345',
        'speed': 100.0,
        'section_id': 'section_001',
        'priority': 3,
        'max_speed': 120.0
    }
    
    await engine.add_train('zone_001', train_data)
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await engine.stop()


if __name__ == "__main__":
    asyncio.run(main())
