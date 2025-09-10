"""
ATP/Kavach Safety Validator Service

This service ensures all train operations comply with:
- ATP (Automatic Train Protection) constraints
- Kavach system safety envelopes
- Signal aspects and interlocking
- Speed limits and braking distances
- Emergency stop protocols
"""

import asyncio
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class SafetyViolationType(Enum):
    """Types of safety violations"""
    SPEED_EXCESS = "speed_excess"
    SIGNAL_VIOLATION = "signal_violation"
    BRAKING_DISTANCE = "braking_distance"
    TRACK_OCCUPANCY = "track_occupancy"
    EMERGENCY_STOP = "emergency_stop"
    ATP_DISABLED = "atp_disabled"
    KAVACH_VIOLATION = "kavach_violation"


class SafetyLevel(Enum):
    """Safety levels for violations"""
    CRITICAL = "critical"  # Immediate stop required
    HIGH = "high"  # Reduce speed immediately
    MEDIUM = "medium"  # Caution required
    LOW = "low"  # Advisory only


@dataclass
class SafetyViolation:
    """Safety violation record"""
    violation_id: str
    train_id: str
    violation_type: SafetyViolationType
    safety_level: SafetyLevel
    description: str
    timestamp: datetime
    location: Dict[str, float]  # GPS coordinates
    section_id: str
    current_speed: float
    max_allowed_speed: float
    required_action: str
    atp_override: bool = False
    kavach_override: bool = False


class ATPSafetyEnvelope(BaseModel):
    """ATP safety envelope for a track section"""
    section_id: str
    max_speed: float = Field(..., description="Maximum speed in km/h")
    braking_distance: float = Field(..., description="Braking distance in meters")
    signal_aspect: str = Field(..., description="Current signal aspect")
    track_clear: bool = Field(..., description="Track is clear")
    atp_enabled: bool = Field(..., description="ATP is enabled")
    kavach_enabled: bool = Field(..., description="Kavach is enabled")
    weather_factor: float = Field(default=1.0, description="Weather safety factor")
    maintenance_mode: bool = Field(default=False, description="Maintenance mode active")
    
    def get_effective_max_speed(self) -> float:
        """Get effective maximum speed considering all factors"""
        effective_speed = self.max_speed
        
        # Apply weather factor
        effective_speed *= self.weather_factor
        
        # Apply maintenance mode reduction
        if self.maintenance_mode:
            effective_speed *= 0.7
        
        # Apply signal aspect restrictions
        if self.signal_aspect == "red":
            effective_speed = 0.0
        elif self.signal_aspect == "yellow":
            effective_speed = min(effective_speed, 30.0)  # 30 km/h max for yellow
        elif self.signal_aspect == "double_yellow":
            effective_speed = min(effective_speed, 60.0)  # 60 km/h max for double yellow
        
        return effective_speed


class KavachSafetyProfile(BaseModel):
    """Kavach safety profile for a train"""
    train_id: str
    train_type: str
    max_speed: float
    braking_distance: float
    acceleration: float
    atp_compatible: bool
    kavach_enabled: bool
    emergency_braking_distance: float
    service_braking_distance: float
    speed_restriction_zones: List[Dict[str, Any]] = Field(default_factory=list)
    
    def calculate_braking_distance(self, current_speed: float, target_speed: float = 0.0) -> float:
        """Calculate required braking distance"""
        if current_speed <= target_speed:
            return 0.0
        
        # Basic physics: v² = u² + 2as
        # s = (v² - u²) / (2a)
        speed_diff = current_speed - target_speed
        speed_diff_ms = speed_diff * 1000 / 3600  # Convert to m/s
        
        # Use service braking for normal operations
        braking_acceleration = self.service_braking_distance / (current_speed * 1000 / 3600) ** 2
        braking_distance = (speed_diff_ms ** 2) / (2 * braking_acceleration)
        
        return max(braking_distance, self.service_braking_distance)
    
    def calculate_emergency_braking_distance(self, current_speed: float) -> float:
        """Calculate emergency braking distance"""
        if current_speed <= 0:
            return 0.0
        
        # Use emergency braking for critical situations
        speed_ms = current_speed * 1000 / 3600  # Convert to m/s
        braking_acceleration = self.emergency_braking_distance / (speed_ms ** 2)
        braking_distance = (speed_ms ** 2) / (2 * braking_acceleration)
        
        return max(braking_distance, self.emergency_braking_distance)


class SafetyValidator:
    """Main safety validator for ATP/Kavach compliance"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.safety_envelopes: Dict[str, ATPSafetyEnvelope] = {}
        self.kavach_profiles: Dict[str, KavachSafetyProfile] = {}
        self.violations: List[SafetyViolation] = []
        self.emergency_stops: List[str] = []  # Train IDs with emergency stops
        
        # Safety thresholds
        self.speed_tolerance = config.get('speed_tolerance', 5.0)  # km/h
        self.braking_safety_margin = config.get('braking_safety_margin', 1.5)  # 50% safety margin
        self.signal_violation_threshold = config.get('signal_violation_threshold', 10.0)  # meters
        
    async def validate_train_operation(self, train_data: Dict[str, Any]) -> List[SafetyViolation]:
        """Validate a train operation against safety constraints"""
        violations = []
        train_id = train_data['train_id']
        
        try:
            # Get train's Kavach profile
            kavach_profile = self.kavach_profiles.get(train_id)
            if not kavach_profile:
                logger.warning("No Kavach profile found for train", train_id=train_id)
                kavach_profile = self._create_default_kavach_profile(train_data)
                self.kavach_profiles[train_id] = kavach_profile
            
            # Get track section safety envelope
            section_id = train_data.get('section_id')
            if not section_id:
                logger.error("No section ID provided for train", train_id=train_id)
                return violations
            
            safety_envelope = self.safety_envelopes.get(section_id)
            if not safety_envelope:
                logger.warning("No safety envelope found for section", section_id=section_id)
                safety_envelope = self._create_default_safety_envelope(section_id)
                self.safety_envelopes[section_id] = safety_envelope
            
            # Validate speed limits
            speed_violations = await self._validate_speed_limits(train_data, kavach_profile, safety_envelope)
            violations.extend(speed_violations)
            
            # Validate signal aspects
            signal_violations = await self._validate_signal_aspects(train_data, safety_envelope)
            violations.extend(signal_violations)
            
            # Validate braking distances
            braking_violations = await self._validate_braking_distances(train_data, kavach_profile, safety_envelope)
            violations.extend(braking_violations)
            
            # Validate track occupancy
            occupancy_violations = await self._validate_track_occupancy(train_data, safety_envelope)
            violations.extend(occupancy_violations)
            
            # Validate ATP/Kavach status
            atp_violations = await self._validate_atp_kavach_status(train_data, kavach_profile, safety_envelope)
            violations.extend(atp_violations)
            
            # Store violations
            self.violations.extend(violations)
            
            # Check for critical violations requiring emergency stop
            critical_violations = [v for v in violations if v.safety_level == SafetyLevel.CRITICAL]
            if critical_violations:
                await self._trigger_emergency_stop(train_id, critical_violations)
            
            return violations
            
        except Exception as e:
            logger.error("Error validating train operation", train_id=train_id, error=str(e))
            return violations
    
    async def _validate_speed_limits(self, train_data: Dict[str, Any], 
                                   kavach_profile: KavachSafetyProfile, 
                                   safety_envelope: ATPSafetyEnvelope) -> List[SafetyViolation]:
        """Validate speed limits"""
        violations = []
        train_id = train_data['train_id']
        current_speed = train_data.get('speed', 0.0)
        
        # Get effective maximum speed
        max_allowed_speed = safety_envelope.get_effective_max_speed()
        
        # Check for speed excess
        if current_speed > max_allowed_speed + self.speed_tolerance:
            violation = SafetyViolation(
                violation_id=f"speed_{train_id}_{datetime.now().timestamp()}",
                train_id=train_id,
                violation_type=SafetyViolationType.SPEED_EXCESS,
                safety_level=SafetyLevel.CRITICAL if current_speed > max_allowed_speed * 1.2 else SafetyLevel.HIGH,
                description=f"Speed excess: {current_speed:.1f} km/h > {max_allowed_speed:.1f} km/h",
                timestamp=datetime.now(timezone.utc),
                location=train_data.get('position', {}),
                section_id=train_data.get('section_id', ''),
                current_speed=current_speed,
                max_allowed_speed=max_allowed_speed,
                required_action="Reduce speed immediately" if current_speed > max_allowed_speed * 1.2 else "Reduce speed to within limits"
            )
            violations.append(violation)
        
        return violations
    
    async def _validate_signal_aspects(self, train_data: Dict[str, Any], 
                                     safety_envelope: ATPSafetyEnvelope) -> List[SafetyViolation]:
        """Validate signal aspects"""
        violations = []
        train_id = train_data['train_id']
        current_speed = train_data.get('speed', 0.0)
        
        # Check signal aspect compliance
        if safety_envelope.signal_aspect == "red" and current_speed > 0:
            violation = SafetyViolation(
                violation_id=f"signal_{train_id}_{datetime.now().timestamp()}",
                train_id=train_id,
                violation_type=SafetyViolationType.SIGNAL_VIOLATION,
                safety_level=SafetyLevel.CRITICAL,
                description="Train moving against red signal",
                timestamp=datetime.now(timezone.utc),
                location=train_data.get('position', {}),
                section_id=train_data.get('section_id', ''),
                current_speed=current_speed,
                max_allowed_speed=0.0,
                required_action="Emergency stop - Red signal violation"
            )
            violations.append(violation)
        
        elif safety_envelope.signal_aspect == "yellow" and current_speed > 30:
            violation = SafetyViolation(
                violation_id=f"signal_{train_id}_{datetime.now().timestamp()}",
                train_id=train_id,
                violation_type=SafetyViolationType.SIGNAL_VIOLATION,
                safety_level=SafetyLevel.HIGH,
                description="Speed too high for yellow signal",
                timestamp=datetime.now(timezone.utc),
                location=train_data.get('position', {}),
                section_id=train_data.get('section_id', ''),
                current_speed=current_speed,
                max_allowed_speed=30.0,
                required_action="Reduce speed to 30 km/h for yellow signal"
            )
            violations.append(violation)
        
        return violations
    
    async def _validate_braking_distances(self, train_data: Dict[str, Any], 
                                        kavach_profile: KavachSafetyProfile, 
                                        safety_envelope: ATPSafetyEnvelope) -> List[SafetyViolation]:
        """Validate braking distances"""
        violations = []
        train_id = train_data['train_id']
        current_speed = train_data.get('speed', 0.0)
        
        # Calculate required braking distance
        required_braking_distance = kavach_profile.calculate_braking_distance(current_speed)
        required_braking_distance *= self.braking_safety_margin  # Apply safety margin
        
        # Check if there's sufficient distance to stop
        # This would need to be calculated based on track layout and upcoming signals
        available_distance = self._calculate_available_braking_distance(train_data, safety_envelope)
        
        if required_braking_distance > available_distance:
            violation = SafetyViolation(
                violation_id=f"braking_{train_id}_{datetime.now().timestamp()}",
                train_id=train_id,
                violation_type=SafetyViolationType.BRAKING_DISTANCE,
                safety_level=SafetyLevel.CRITICAL,
                description=f"Insufficient braking distance: {required_braking_distance:.1f}m required, {available_distance:.1f}m available",
                timestamp=datetime.now(timezone.utc),
                location=train_data.get('position', {}),
                section_id=train_data.get('section_id', ''),
                current_speed=current_speed,
                max_allowed_speed=safety_envelope.get_effective_max_speed(),
                required_action="Emergency braking required"
            )
            violations.append(violation)
        
        return violations
    
    async def _validate_track_occupancy(self, train_data: Dict[str, Any], 
                                      safety_envelope: ATPSafetyEnvelope) -> List[SafetyViolation]:
        """Validate track occupancy"""
        violations = []
        train_id = train_data['train_id']
        
        # Check if track is clear
        if not safety_envelope.track_clear:
            violation = SafetyViolation(
                violation_id=f"occupancy_{train_id}_{datetime.now().timestamp()}",
                train_id=train_id,
                violation_type=SafetyViolationType.TRACK_OCCUPANCY,
                safety_level=SafetyLevel.CRITICAL,
                description="Track occupied by another train",
                timestamp=datetime.now(timezone.utc),
                location=train_data.get('position', {}),
                section_id=train_data.get('section_id', ''),
                current_speed=train_data.get('speed', 0.0),
                max_allowed_speed=0.0,
                required_action="Stop - Track occupied"
            )
            violations.append(violation)
        
        return violations
    
    async def _validate_atp_kavach_status(self, train_data: Dict[str, Any], 
                                        kavach_profile: KavachSafetyProfile, 
                                        safety_envelope: ATPSafetyEnvelope) -> List[SafetyViolation]:
        """Validate ATP/Kavach status"""
        violations = []
        train_id = train_data['train_id']
        
        # Check ATP status
        if not safety_envelope.atp_enabled and kavach_profile.atp_compatible:
            violation = SafetyViolation(
                violation_id=f"atp_{train_id}_{datetime.now().timestamp()}",
                train_id=train_id,
                violation_type=SafetyViolationType.ATP_DISABLED,
                safety_level=SafetyLevel.HIGH,
                description="ATP disabled on track section",
                timestamp=datetime.now(timezone.utc),
                location=train_data.get('position', {}),
                section_id=train_data.get('section_id', ''),
                current_speed=train_data.get('speed', 0.0),
                max_allowed_speed=safety_envelope.get_effective_max_speed(),
                required_action="Proceed with caution - ATP disabled"
            )
            violations.append(violation)
        
        # Check Kavach status
        if not kavach_profile.kavach_enabled and safety_envelope.kavach_enabled:
            violation = SafetyViolation(
                violation_id=f"kavach_{train_id}_{datetime.now().timestamp()}",
                train_id=train_id,
                violation_type=SafetyViolationType.KAVACH_VIOLATION,
                safety_level=SafetyLevel.MEDIUM,
                description="Kavach not enabled on train",
                timestamp=datetime.now(timezone.utc),
                location=train_data.get('position', {}),
                section_id=train_data.get('section_id', ''),
                current_speed=train_data.get('speed', 0.0),
                max_allowed_speed=safety_envelope.get_effective_max_speed(),
                required_action="Enable Kavach system"
            )
            violations.append(violation)
        
        return violations
    
    def _calculate_available_braking_distance(self, train_data: Dict[str, Any], 
                                            safety_envelope: ATPSafetyEnvelope) -> float:
        """Calculate available braking distance to next signal or obstacle"""
        # This is a simplified calculation
        # In production, this would use track layout data and signal positions
        
        # Default available distance (would be calculated from track layout)
        base_distance = 1000.0  # 1 km default
        
        # Reduce distance based on signal aspect
        if safety_envelope.signal_aspect == "red":
            base_distance = 0.0
        elif safety_envelope.signal_aspect == "yellow":
            base_distance = min(base_distance, 500.0)  # 500m for yellow
        elif safety_envelope.signal_aspect == "double_yellow":
            base_distance = min(base_distance, 800.0)  # 800m for double yellow
        
        # Apply weather factor
        base_distance *= safety_envelope.weather_factor
        
        return base_distance
    
    def _create_default_kavach_profile(self, train_data: Dict[str, Any]) -> KavachSafetyProfile:
        """Create default Kavach profile for a train"""
        return KavachSafetyProfile(
            train_id=train_data['train_id'],
            train_type=train_data.get('train_type', 'passenger'),
            max_speed=train_data.get('max_speed', 120.0),
            braking_distance=train_data.get('braking_distance', 800.0),
            acceleration=train_data.get('acceleration', 0.5),
            atp_compatible=train_data.get('atp_compatible', True),
            kavach_enabled=train_data.get('kavach_enabled', True),
            emergency_braking_distance=train_data.get('emergency_braking_distance', 400.0),
            service_braking_distance=train_data.get('service_braking_distance', 800.0)
        )
    
    def _create_default_safety_envelope(self, section_id: str) -> ATPSafetyEnvelope:
        """Create default safety envelope for a track section"""
        return ATPSafetyEnvelope(
            section_id=section_id,
            max_speed=120.0,  # Default 120 km/h
            braking_distance=800.0,  # Default 800m
            signal_aspect="green",
            track_clear=True,
            atp_enabled=True,
            kavach_enabled=True,
            weather_factor=1.0,
            maintenance_mode=False
        )
    
    async def _trigger_emergency_stop(self, train_id: str, violations: List[SafetyViolation]):
        """Trigger emergency stop for a train"""
        if train_id not in self.emergency_stops:
            self.emergency_stops.append(train_id)
            logger.critical("Emergency stop triggered", train_id=train_id, violations=len(violations))
            
            # In production, this would send emergency stop command to the train
            # and notify control room operators
    
    async def update_safety_envelope(self, section_id: str, envelope: ATPSafetyEnvelope):
        """Update safety envelope for a track section"""
        self.safety_envelopes[section_id] = envelope
        logger.info("Safety envelope updated", section_id=section_id)
    
    async def update_kavach_profile(self, train_id: str, profile: KavachSafetyProfile):
        """Update Kavach profile for a train"""
        self.kavach_profiles[train_id] = profile
        logger.info("Kavach profile updated", train_id=train_id)
    
    def get_violations(self, train_id: Optional[str] = None) -> List[SafetyViolation]:
        """Get safety violations, optionally filtered by train ID"""
        if train_id:
            return [v for v in self.violations if v.train_id == train_id]
        return self.violations
    
    def get_emergency_stops(self) -> List[str]:
        """Get list of trains with emergency stops"""
        return self.emergency_stops.copy()
    
    def clear_emergency_stop(self, train_id: str):
        """Clear emergency stop for a train"""
        if train_id in self.emergency_stops:
            self.emergency_stops.remove(train_id)
            logger.info("Emergency stop cleared", train_id=train_id)


async def main():
    """Main entry point for the safety validator service"""
    config = {
        'speed_tolerance': 5.0,
        'braking_safety_margin': 1.5,
        'signal_violation_threshold': 10.0
    }
    
    validator = SafetyValidator(config)
    
    # Example usage
    train_data = {
        'train_id': '12345',
        'speed': 100.0,
        'section_id': 'section_001',
        'position': {'latitude': 28.6139, 'longitude': 77.2090},
        'train_type': 'express',
        'atp_compatible': True,
        'kavach_enabled': True
    }
    
    violations = await validator.validate_train_operation(train_data)
    print(f"Found {len(violations)} safety violations")
    
    for violation in violations:
        print(f"Violation: {violation.description} - Action: {violation.required_action}")


if __name__ == "__main__":
    asyncio.run(main())
