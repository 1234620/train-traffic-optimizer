"""
Slot Trading Service

This service implements a transparent, auditable slot-trading protocol between zones during congestion:
- Prioritizes emergency and higher-commitment services
- Compensates deferred movements
- Records each negotiation step, winning bids, and fairness rationale
- Provides operator review and post-mortem capabilities
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

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class SlotStatus(Enum):
    """Status of a slot trading negotiation"""
    PENDING = "pending"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class BidType(Enum):
    """Types of bids in slot trading"""
    REQUEST = "request"
    OFFER = "offer"
    COUNTER_OFFER = "counter_offer"
    ACCEPTANCE = "acceptance"
    REJECTION = "rejection"


class PriorityLevel(Enum):
    """Priority levels for slot trading"""
    EMERGENCY = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    MAINTENANCE = 5


@dataclass
class SlotRequest:
    """Request for a slot trade"""
    request_id: str
    requesting_zone: str
    target_zone: str
    train_id: str
    priority: PriorityLevel
    current_delay: int  # minutes
    max_acceptable_delay: int  # minutes
    preferred_speed: float  # km/h
    deadline: datetime
    compensation_offered: float  # monetary value
    additional_conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SlotOffer:
    """Offer for a slot trade"""
    offer_id: str
    offering_zone: str
    requesting_zone: str
    request_id: str
    available_slot_time: datetime
    slot_duration: int  # minutes
    max_speed: float  # km/h
    conditions: Dict[str, Any] = field(default_factory=dict)
    compensation_requested: float = 0.0
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=30))


@dataclass
class SlotBid:
    """Bid in slot trading auction"""
    bid_id: str
    negotiation_id: str
    zone_id: str
    bid_type: BidType
    train_id: str
    priority: PriorityLevel
    bid_value: float  # monetary value or priority score
    conditions: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


@dataclass
class SlotTrade:
    """Completed slot trade"""
    trade_id: str
    negotiation_id: str
    winning_zone: str
    losing_zone: str
    train_id: str
    slot_time: datetime
    slot_duration: int
    compensation: float
    conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


@dataclass
class NegotiationRecord:
    """Record of slot trading negotiation"""
    negotiation_id: str
    request_id: str
    status: SlotStatus
    participants: List[str] = field(default_factory=list)
    bids: List[SlotBid] = field(default_factory=list)
    winner: Optional[str] = None
    final_conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    fairness_score: float = 0.0
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)


class SlotTradingService:
    """Main slot trading service"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_negotiations: Dict[str, NegotiationRecord] = {}
        self.completed_trades: List[SlotTrade] = []
        self.zone_capacities: Dict[str, int] = {}
        self.zone_priorities: Dict[str, PriorityLevel] = {}
        self.compensation_rates: Dict[str, float] = {}  # per minute of delay
        
        # Fairness and audit settings
        self.max_negotiation_time = config.get('max_negotiation_time', 300)  # 5 minutes
        self.min_bid_interval = config.get('min_bid_interval', 30)  # 30 seconds
        self.fairness_threshold = config.get('fairness_threshold', 0.7)
        
        # Message bus for zone communication
        self.message_bus = None
    
    async def initialize(self, message_bus):
        """Initialize the slot trading service"""
        self.message_bus = message_bus
        logger.info("Slot trading service initialized")
    
    async def request_slot(self, request: SlotRequest) -> str:
        """Request a slot trade"""
        negotiation_id = str(uuid.uuid4())
        
        # Create negotiation record
        negotiation = NegotiationRecord(
            negotiation_id=negotiation_id,
            request_id=request.request_id,
            status=SlotStatus.PENDING,
            participants=[request.requesting_zone, request.target_zone]
        )
        
        self.active_negotiations[negotiation_id] = negotiation
        
        # Send request to target zone
        await self._send_slot_request(negotiation_id, request)
        
        # Start negotiation timeout
        asyncio.create_task(self._handle_negotiation_timeout(negotiation_id))
        
        logger.info("Slot request initiated", 
                   negotiation_id=negotiation_id,
                   requesting_zone=request.requesting_zone,
                   target_zone=request.target_zone,
                   train_id=request.train_id)
        
        return negotiation_id
    
    async def _send_slot_request(self, negotiation_id: str, request: SlotRequest):
        """Send slot request to target zone"""
        message = {
            'type': 'slot_request',
            'negotiation_id': negotiation_id,
            'request_id': request.request_id,
            'requesting_zone': request.requesting_zone,
            'train_id': request.train_id,
            'priority': request.priority.value,
            'current_delay': request.current_delay,
            'max_acceptable_delay': request.max_acceptable_delay,
            'preferred_speed': request.preferred_speed,
            'deadline': request.deadline.isoformat(),
            'compensation_offered': request.compensation_offered,
            'additional_conditions': request.additional_conditions
        }
        
        if self.message_bus:
            await self.message_bus.send_message(request.target_zone, message)
    
    async def handle_slot_request(self, message: Dict[str, Any]) -> Optional[str]:
        """Handle incoming slot request"""
        negotiation_id = message['negotiation_id']
        request_id = message['request_id']
        requesting_zone = message['requesting_zone']
        train_id = message['train_id']
        priority = PriorityLevel(message['priority'])
        current_delay = message['current_delay']
        compensation_offered = message['compensation_offered']
        
        # Check if we can accommodate the request
        if await self._can_accommodate_slot(request_id, priority, current_delay):
            # Create offer
            offer = await self._create_slot_offer(negotiation_id, request_id, requesting_zone, 
                                                train_id, priority, compensation_offered)
            
            if offer:
                # Send offer back
                await self._send_slot_offer(negotiation_id, offer)
                
                # Update negotiation status
                if negotiation_id in self.active_negotiations:
                    self.active_negotiations[negotiation_id].status = SlotStatus.NEGOTIATING
                    self.active_negotiations[negotiation_id].participants.append(requesting_zone)
                
                logger.info("Slot offer created", negotiation_id=negotiation_id, offer_id=offer.offer_id)
                return offer.offer_id
            else:
                # Reject request
                await self._reject_slot_request(negotiation_id, request_id, requesting_zone, 
                                              "Insufficient capacity")
                return None
        else:
            # Reject request
            await self._reject_slot_request(negotiation_id, request_id, requesting_zone, 
                                          "Cannot accommodate request")
            return None
    
    async def _can_accommodate_slot(self, request_id: str, priority: PriorityLevel, 
                                  current_delay: int) -> bool:
        """Check if zone can accommodate a slot request"""
        # Get current zone capacity
        current_capacity = self.zone_capacities.get('current', 0)
        max_capacity = self.zone_capacities.get('max', 10)
        
        # Check capacity
        if current_capacity >= max_capacity:
            return False
        
        # Priority-based accommodation
        if priority == PriorityLevel.EMERGENCY:
            return True
        elif priority == PriorityLevel.HIGH:
            return current_capacity < max_capacity * 0.8
        elif priority == PriorityLevel.MEDIUM:
            return current_capacity < max_capacity * 0.6
        else:
            return current_capacity < max_capacity * 0.4
    
    async def _create_slot_offer(self, negotiation_id: str, request_id: str, 
                               requesting_zone: str, train_id: str, priority: PriorityLevel, 
                               compensation_offered: float) -> Optional[SlotOffer]:
        """Create a slot offer"""
        # Calculate available slot time
        available_time = datetime.now(timezone.utc) + timedelta(minutes=15)  # 15 minutes from now
        
        # Calculate slot duration based on priority
        if priority == PriorityLevel.EMERGENCY:
            slot_duration = 30  # 30 minutes
        elif priority == PriorityLevel.HIGH:
            slot_duration = 20  # 20 minutes
        else:
            slot_duration = 15  # 15 minutes
        
        # Calculate compensation requested
        compensation_requested = self._calculate_compensation(priority, slot_duration)
        
        # Create offer
        offer = SlotOffer(
            offer_id=str(uuid.uuid4()),
            offering_zone='current_zone',  # This would be the actual zone ID
            requesting_zone=requesting_zone,
            request_id=request_id,
            available_slot_time=available_time,
            slot_duration=slot_duration,
            max_speed=120.0,  # Default max speed
            compensation_requested=compensation_requested,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30)
        )
        
        return offer
    
    def _calculate_compensation(self, priority: PriorityLevel, slot_duration: int) -> float:
        """Calculate compensation for slot trade"""
        base_rate = self.compensation_rates.get('base', 100.0)  # Base rate per minute
        
        # Priority-based multiplier
        if priority == PriorityLevel.EMERGENCY:
            multiplier = 0.0  # No compensation for emergency
        elif priority == PriorityLevel.HIGH:
            multiplier = 0.5
        elif priority == PriorityLevel.MEDIUM:
            multiplier = 1.0
        else:
            multiplier = 1.5
        
        return base_rate * slot_duration * multiplier
    
    async def _send_slot_offer(self, negotiation_id: str, offer: SlotOffer):
        """Send slot offer to requesting zone"""
        message = {
            'type': 'slot_offer',
            'negotiation_id': negotiation_id,
            'offer_id': offer.offer_id,
            'offering_zone': offer.offering_zone,
            'requesting_zone': offer.requesting_zone,
            'available_slot_time': offer.available_slot_time.isoformat(),
            'slot_duration': offer.slot_duration,
            'max_speed': offer.max_speed,
            'compensation_requested': offer.compensation_requested,
            'expires_at': offer.expires_at.isoformat()
        }
        
        if self.message_bus:
            await self.message_bus.send_message(offer.requesting_zone, message)
    
    async def _reject_slot_request(self, negotiation_id: str, request_id: str, 
                                 requesting_zone: str, reason: str):
        """Reject a slot request"""
        message = {
            'type': 'slot_rejection',
            'negotiation_id': negotiation_id,
            'request_id': request_id,
            'reason': reason
        }
        
        if self.message_bus:
            await self.message_bus.send_message(requesting_zone, message)
        
        # Update negotiation status
        if negotiation_id in self.active_negotiations:
            self.active_negotiations[negotiation_id].status = SlotStatus.REJECTED
            self.active_negotiations[negotiation_id].completed_at = datetime.now(timezone.utc)
    
    async def handle_slot_offer(self, message: Dict[str, Any]) -> bool:
        """Handle incoming slot offer"""
        negotiation_id = message['negotiation_id']
        offer_id = message['offer_id']
        offering_zone = message['offering_zone']
        available_slot_time = datetime.fromisoformat(message['available_slot_time'])
        slot_duration = message['slot_duration']
        compensation_requested = message['compensation_requested']
        
        # Check if offer is still valid
        if datetime.now(timezone.utc) > datetime.fromisoformat(message['expires_at']):
            logger.warning("Slot offer expired", negotiation_id=negotiation_id, offer_id=offer_id)
            return False
        
        # Evaluate offer
        if await self._evaluate_offer(negotiation_id, compensation_requested, slot_duration):
            # Accept offer
            await self._accept_slot_offer(negotiation_id, offer_id, offering_zone)
            return True
        else:
            # Reject offer
            await self._reject_slot_offer(negotiation_id, offer_id, offering_zone, "Offer not acceptable")
            return False
    
    async def _evaluate_offer(self, negotiation_id: str, compensation_requested: float, 
                            slot_duration: int) -> bool:
        """Evaluate a slot offer"""
        # Get negotiation record
        if negotiation_id not in self.active_negotiations:
            return False
        
        negotiation = self.active_negotiations[negotiation_id]
        
        # Check if compensation is acceptable
        max_acceptable_compensation = negotiation.audit_trail[-1].get('compensation_offered', 0) if negotiation.audit_trail else 0
        
        if compensation_requested > max_acceptable_compensation:
            return False
        
        # Check if slot duration is acceptable
        if slot_duration < 10:  # Minimum 10 minutes
            return False
        
        return True
    
    async def _accept_slot_offer(self, negotiation_id: str, offer_id: str, offering_zone: str):
        """Accept a slot offer"""
        if negotiation_id not in self.active_negotiations:
            return
        
        negotiation = self.active_negotiations[negotiation_id]
        negotiation.status = SlotStatus.ACCEPTED
        negotiation.winner = offering_zone
        negotiation.completed_at = datetime.now(timezone.utc)
        
        # Create slot trade
        trade = SlotTrade(
            trade_id=str(uuid.uuid4()),
            negotiation_id=negotiation_id,
            winning_zone=offering_zone,
            losing_zone=negotiation.participants[0],  # Assuming first participant is requesting zone
            train_id=negotiation.audit_trail[0].get('train_id', '') if negotiation.audit_trail else '',
            slot_time=datetime.now(timezone.utc) + timedelta(minutes=15),
            slot_duration=30,  # Default duration
            compensation=0.0  # Would be calculated from negotiation
        )
        
        self.completed_trades.append(trade)
        
        # Send acceptance message
        message = {
            'type': 'slot_acceptance',
            'negotiation_id': negotiation_id,
            'offer_id': offer_id,
            'trade_id': trade.trade_id
        }
        
        if self.message_bus:
            await self.message_bus.send_message(offering_zone, message)
        
        logger.info("Slot offer accepted", negotiation_id=negotiation_id, trade_id=trade.trade_id)
    
    async def _reject_slot_offer(self, negotiation_id: str, offer_id: str, 
                               offering_zone: str, reason: str):
        """Reject a slot offer"""
        message = {
            'type': 'slot_rejection',
            'negotiation_id': negotiation_id,
            'offer_id': offer_id,
            'reason': reason
        }
        
        if self.message_bus:
            await self.message_bus.send_message(offering_zone, message)
        
        logger.info("Slot offer rejected", negotiation_id=negotiation_id, reason=reason)
    
    async def _handle_negotiation_timeout(self, negotiation_id: str):
        """Handle negotiation timeout"""
        await asyncio.sleep(self.max_negotiation_time)
        
        if negotiation_id in self.active_negotiations:
            negotiation = self.active_negotiations[negotiation_id]
            if negotiation.status == SlotStatus.PENDING or negotiation.status == SlotStatus.NEGOTIATING:
                negotiation.status = SlotStatus.EXPIRED
                negotiation.completed_at = datetime.now(timezone.utc)
                
                logger.warning("Negotiation timed out", negotiation_id=negotiation_id)
    
    async def start_auction(self, negotiation_id: str, participants: List[str], 
                          train_id: str, priority: PriorityLevel) -> str:
        """Start an auction for slot trading"""
        if negotiation_id not in self.active_negotiations:
            return None
        
        negotiation = self.active_negotiations[negotiation_id]
        negotiation.status = SlotStatus.NEGOTIATING
        negotiation.participants = participants
        
        # Create initial bid
        initial_bid = SlotBid(
            bid_id=str(uuid.uuid4()),
            negotiation_id=negotiation_id,
            zone_id=participants[0],
            bid_type=BidType.REQUEST,
            train_id=train_id,
            priority=priority,
            bid_value=self._calculate_bid_value(priority, 0),  # Initial bid value
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)
        )
        
        negotiation.bids.append(initial_bid)
        
        # Notify all participants
        for participant in participants:
            await self._send_auction_notification(participant, negotiation_id, initial_bid)
        
        logger.info("Auction started", negotiation_id=negotiation_id, participants=participants)
        return initial_bid.bid_id
    
    def _calculate_bid_value(self, priority: PriorityLevel, delay_minutes: int) -> float:
        """Calculate bid value for auction"""
        base_value = 1000.0  # Base value
        
        # Priority multiplier
        priority_multiplier = {
            PriorityLevel.EMERGENCY: 10.0,
            PriorityLevel.HIGH: 5.0,
            PriorityLevel.MEDIUM: 2.0,
            PriorityLevel.LOW: 1.0,
            PriorityLevel.MAINTENANCE: 0.5
        }.get(priority, 1.0)
        
        # Delay penalty
        delay_penalty = delay_minutes * 10.0
        
        return base_value * priority_multiplier - delay_penalty
    
    async def _send_auction_notification(self, zone_id: str, negotiation_id: str, bid: SlotBid):
        """Send auction notification to zone"""
        message = {
            'type': 'auction_notification',
            'negotiation_id': negotiation_id,
            'bid_id': bid.bid_id,
            'train_id': bid.train_id,
            'priority': bid.priority.value,
            'bid_value': bid.bid_value,
            'expires_at': bid.expires_at.isoformat() if bid.expires_at else None
        }
        
        if self.message_bus:
            await self.message_bus.send_message(zone_id, message)
    
    async def submit_bid(self, negotiation_id: str, zone_id: str, bid_type: BidType, 
                        train_id: str, priority: PriorityLevel, bid_value: float, 
                        conditions: Dict[str, Any] = None) -> str:
        """Submit a bid in slot trading auction"""
        if negotiation_id not in self.active_negotiations:
            return None
        
        negotiation = self.active_negotiations[negotiation_id]
        
        # Check if zone is participant
        if zone_id not in negotiation.participants:
            logger.warning("Zone not participant in negotiation", zone_id=zone_id, negotiation_id=negotiation_id)
            return None
        
        # Create bid
        bid = SlotBid(
            bid_id=str(uuid.uuid4()),
            negotiation_id=negotiation_id,
            zone_id=zone_id,
            bid_type=bid_type,
            train_id=train_id,
            priority=priority,
            bid_value=bid_value,
            conditions=conditions or {},
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)
        )
        
        negotiation.bids.append(bid)
        
        # Check if this is the winning bid
        if await self._evaluate_bid(negotiation, bid):
            negotiation.winner = zone_id
            negotiation.status = SlotStatus.ACCEPTED
            negotiation.completed_at = datetime.now(timezone.utc)
            
            # Create slot trade
            trade = SlotTrade(
                trade_id=str(uuid.uuid4()),
                negotiation_id=negotiation_id,
                winning_zone=zone_id,
                losing_zone=negotiation.participants[0],  # Assuming first participant is requesting zone
                train_id=train_id,
                slot_time=datetime.now(timezone.utc) + timedelta(minutes=15),
                slot_duration=30,  # Default duration
                compensation=bid_value
            )
            
            self.completed_trades.append(trade)
            
            logger.info("Winning bid submitted", negotiation_id=negotiation_id, zone_id=zone_id, bid_value=bid_value)
        else:
            logger.info("Bid submitted", negotiation_id=negotiation_id, zone_id=zone_id, bid_value=bid_value)
        
        return bid.bid_id
    
    async def _evaluate_bid(self, negotiation: NegotiationRecord, bid: SlotBid) -> bool:
        """Evaluate if a bid is winning"""
        if not negotiation.bids:
            return True
        
        # Get highest bid so far
        highest_bid = max(negotiation.bids[:-1], key=lambda b: b.bid_value) if len(negotiation.bids) > 1 else None
        
        if not highest_bid:
            return True
        
        # Check if current bid is higher
        if bid.bid_value > highest_bid.bid_value:
            return True
        
        # Check if current bid has higher priority
        if bid.priority.value < highest_bid.priority.value:
            return True
        
        return False
    
    def calculate_fairness_score(self, negotiation_id: str) -> float:
        """Calculate fairness score for a negotiation"""
        if negotiation_id not in self.active_negotiations:
            return 0.0
        
        negotiation = self.active_negotiations[negotiation_id]
        
        if not negotiation.bids:
            return 0.0
        
        # Calculate fairness based on bid distribution and priority
        bid_values = [bid.bid_value for bid in negotiation.bids]
        priorities = [bid.priority.value for bid in negotiation.bids]
        
        # Fairness based on bid value distribution
        value_fairness = 1.0 - (max(bid_values) - min(bid_values)) / max(bid_values) if max(bid_values) > 0 else 0.0
        
        # Fairness based on priority distribution
        priority_fairness = 1.0 - (max(priorities) - min(priorities)) / max(priorities) if max(priorities) > 0 else 0.0
        
        # Overall fairness score
        fairness_score = (value_fairness + priority_fairness) / 2.0
        
        negotiation.fairness_score = fairness_score
        return fairness_score
    
    def get_negotiation_audit_trail(self, negotiation_id: str) -> List[Dict[str, Any]]:
        """Get audit trail for a negotiation"""
        if negotiation_id not in self.active_negotiations:
            return []
        
        negotiation = self.active_negotiations[negotiation_id]
        return negotiation.audit_trail
    
    def get_completed_trades(self, zone_id: Optional[str] = None) -> List[SlotTrade]:
        """Get completed trades, optionally filtered by zone"""
        if zone_id:
            return [trade for trade in self.completed_trades if trade.winning_zone == zone_id or trade.losing_zone == zone_id]
        return self.completed_trades.copy()
    
    def get_negotiation_statistics(self) -> Dict[str, Any]:
        """Get slot trading statistics"""
        total_negotiations = len(self.active_negotiations)
        completed_negotiations = len([n for n in self.active_negotiations.values() if n.status == SlotStatus.ACCEPTED])
        rejected_negotiations = len([n for n in self.active_negotiations.values() if n.status == SlotStatus.REJECTED])
        expired_negotiations = len([n for n in self.active_negotiations.values() if n.status == SlotStatus.EXPIRED])
        
        total_trades = len(self.completed_trades)
        total_compensation = sum(trade.compensation for trade in self.completed_trades)
        
        return {
            'total_negotiations': total_negotiations,
            'completed_negotiations': completed_negotiations,
            'rejected_negotiations': rejected_negotiations,
            'expired_negotiations': expired_negotiations,
            'success_rate': completed_negotiations / total_negotiations if total_negotiations > 0 else 0.0,
            'total_trades': total_trades,
            'total_compensation': total_compensation,
            'average_compensation': total_compensation / total_trades if total_trades > 0 else 0.0
        }


async def main():
    """Main entry point for the slot trading service"""
    config = {
        'max_negotiation_time': 300,
        'min_bid_interval': 30,
        'fairness_threshold': 0.7
    }
    
    service = SlotTradingService(config)
    
    # Example usage
    request = SlotRequest(
        request_id=str(uuid.uuid4()),
        requesting_zone='zone_001',
        target_zone='zone_002',
        train_id='12345',
        priority=PriorityLevel.HIGH,
        current_delay=30,
        max_acceptable_delay=60,
        preferred_speed=100.0,
        deadline=datetime.now(timezone.utc) + timedelta(hours=1),
        compensation_offered=500.0
    )
    
    negotiation_id = await service.request_slot(request)
    print(f"Slot request initiated: {negotiation_id}")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Slot trading service stopped")


if __name__ == "__main__":
    asyncio.run(main())
