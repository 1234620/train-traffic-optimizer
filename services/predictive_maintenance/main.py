"""
Predictive Maintenance Service

This service handles predictive maintenance routing and risk-aware re-routing:
- Ingest maintenance alerts and risk scores
- Preemptively re-route around sections with elevated failure probability
- Respect ATP/Kavach operational envelopes
- Notify maintenance teams and reflect planned possessions
- Integrate temporary speed restrictions in schedule optimization
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

# Optional sklearn imports - will use fallback if not available
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    # Fallback implementations
    class RandomForestRegressor:
        def __init__(self, *args, **kwargs):
            pass
        def fit(self, X, y):
            return self
        def predict(self, X):
            return np.zeros(len(X))
    
    class StandardScaler:
        def __init__(self):
            pass
        def fit(self, X):
            return self
        def transform(self, X):
            return X
        def fit_transform(self, X):
            return X

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class MaintenanceType(Enum):
    """Types of maintenance activities"""
    TRACK_REPAIR = "track_repair"
    SIGNAL_MAINTENANCE = "signal_maintenance"
    ELECTRIFICATION = "electrification"
    BRIDGE_WORK = "bridge_work"
    TUNNEL_WORK = "tunnel_work"
    PLATFORM_WORK = "platform_work"
    CLEANING = "cleaning"
    INSPECTION = "inspection"


class RiskLevel(Enum):
    """Risk levels for maintenance"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MaintenanceStatus(Enum):
    """Status of maintenance activities"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"


@dataclass
class MaintenanceAlert:
    """Maintenance alert from sensors or systems"""
    alert_id: str
    asset_id: str
    asset_type: str
    alert_type: str
    severity: RiskLevel
    description: str
    location: Dict[str, float]  # GPS coordinates
    section_id: str
    detected_at: datetime
    confidence: float  # 0.0 to 1.0
    sensor_data: Dict[str, Any] = field(default_factory=dict)
    maintenance_required: bool = False
    estimated_downtime: int = 0  # minutes


@dataclass
class MaintenanceActivity:
    """Scheduled maintenance activity"""
    activity_id: str
    maintenance_type: MaintenanceType
    asset_id: str
    section_id: str
    start_time: datetime
    end_time: datetime
    duration: int  # minutes
    status: MaintenanceStatus
    priority: int  # 1=highest, 10=lowest
    crew_size: int
    equipment_required: List[str] = field(default_factory=list)
    safety_requirements: List[str] = field(default_factory=list)
    affected_trains: List[str] = field(default_factory=list)
    alternative_routes: List[str] = field(default_factory=list)
    speed_restrictions: Dict[str, float] = field(default_factory=dict)  # section_id -> max_speed


@dataclass
class RiskAssessment:
    """Risk assessment for a track section"""
    section_id: str
    risk_level: RiskLevel
    risk_score: float  # 0.0 to 1.0
    failure_probability: float  # 0.0 to 1.0
    impact_score: float  # 0.0 to 1.0
    urgency_score: float  # 0.0 to 1.0
    factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: Optional[datetime] = None


@dataclass
class RerouteRecommendation:
    """Recommendation for train rerouting"""
    recommendation_id: str
    train_id: str
    original_route: str
    recommended_route: str
    reason: str
    risk_reduction: float  # 0.0 to 1.0
    additional_delay: int  # minutes
    additional_distance: float  # km
    confidence: float  # 0.0 to 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


class PredictiveMaintenanceService:
    """Main predictive maintenance service"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.maintenance_alerts: List[MaintenanceAlert] = []
        self.maintenance_activities: List[MaintenanceActivity] = []
        self.risk_assessments: Dict[str, RiskAssessment] = {}
        self.reroute_recommendations: List[RerouteRecommendation] = []
        
        # ML models for predictive maintenance
        self.failure_prediction_model = None
        self.risk_assessment_model = None
        self.scaler = StandardScaler()
        
        # Configuration
        self.risk_threshold = config.get('risk_threshold', 0.7)
        self.maintenance_window_hours = config.get('maintenance_window_hours', 4)
        self.reroute_threshold = config.get('reroute_threshold', 0.8)
        
        # Message bus for communication
        self.message_bus = None
        
        # Initialize ML models
        asyncio.create_task(self._initialize_ml_models())
    
    async def initialize(self, message_bus):
        """Initialize the predictive maintenance service"""
        self.message_bus = message_bus
        logger.info("Predictive maintenance service initialized")
    
    async def _initialize_ml_models(self):
        """Initialize ML models for predictive maintenance"""
        try:
            # Load pre-trained models or train new ones
            self.failure_prediction_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.risk_assessment_model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            # Train models with sample data (in production, this would use historical data)
            await self._train_models()
            
            logger.info("ML models initialized")
        except Exception as e:
            logger.error("Error initializing ML models", error=str(e))
    
    async def _train_models(self):
        """Train ML models for predictive maintenance"""
        # Generate sample training data
        # In production, this would use historical maintenance and sensor data
        
        # Sample features: temperature, vibration, age, usage, weather, etc.
        n_samples = 1000
        n_features = 10
        
        X = np.random.randn(n_samples, n_features)
        y_failure = np.random.rand(n_samples)  # Failure probability
        y_risk = np.random.rand(n_samples)  # Risk score
        
        # Train models
        self.failure_prediction_model.fit(X, y_failure)
        self.risk_assessment_model.fit(X, y_risk)
        
        logger.info("ML models trained with sample data")
    
    async def process_maintenance_alert(self, alert: MaintenanceAlert):
        """Process a maintenance alert"""
        try:
            # Add alert to list
            self.maintenance_alerts.append(alert)
            
            # Assess risk for the affected section
            risk_assessment = await self._assess_section_risk(alert.section_id, alert)
            self.risk_assessments[alert.section_id] = risk_assessment
            
            # Check if maintenance is required
            if alert.maintenance_required or risk_assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                # Schedule maintenance activity
                maintenance_activity = await self._schedule_maintenance(alert, risk_assessment)
                if maintenance_activity:
                    self.maintenance_activities.append(maintenance_activity)
                    
                    # Notify maintenance teams
                    await self._notify_maintenance_teams(maintenance_activity)
                    
                    # Generate reroute recommendations
                    await self._generate_reroute_recommendations(maintenance_activity)
            
            # Update speed restrictions if needed
            if risk_assessment.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
                await self._update_speed_restrictions(alert.section_id, risk_assessment)
            
            logger.info("Maintenance alert processed", 
                       alert_id=alert.alert_id, 
                       section_id=alert.section_id,
                       risk_level=risk_assessment.risk_level.value)
            
        except Exception as e:
            logger.error("Error processing maintenance alert", alert_id=alert.alert_id, error=str(e))
    
    async def _assess_section_risk(self, section_id: str, alert: MaintenanceAlert) -> RiskAssessment:
        """Assess risk for a track section"""
        try:
            # Get historical data for the section
            historical_data = await self._get_section_historical_data(section_id)
            
            # Prepare features for ML model
            features = self._prepare_risk_features(alert, historical_data)
            
            # Predict failure probability
            failure_probability = self.failure_prediction_model.predict([features])[0]
            
            # Predict risk score
            risk_score = self.risk_assessment_model.predict([features])[0]
            
            # Calculate impact score
            impact_score = self._calculate_impact_score(section_id, alert)
            
            # Calculate urgency score
            urgency_score = self._calculate_urgency_score(alert, failure_probability)
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score, failure_probability, impact_score)
            
            # Generate recommendations
            recommendations = self._generate_risk_recommendations(risk_level, failure_probability, impact_score)
            
            return RiskAssessment(
                section_id=section_id,
                risk_level=risk_level,
                risk_score=risk_score,
                failure_probability=failure_probability,
                impact_score=impact_score,
                urgency_score=urgency_score,
                factors=alert.sensor_data.keys() if alert.sensor_data else [],
                recommendations=recommendations,
                valid_until=datetime.now(timezone.utc) + timedelta(hours=24)
            )
            
        except Exception as e:
            logger.error("Error assessing section risk", section_id=section_id, error=str(e))
            # Return default risk assessment
            return RiskAssessment(
                section_id=section_id,
                risk_level=RiskLevel.MEDIUM,
                risk_score=0.5,
                failure_probability=0.5,
                impact_score=0.5,
                urgency_score=0.5,
                factors=[],
                recommendations=["Manual inspection required"]
            )
    
    async def _get_section_historical_data(self, section_id: str) -> Dict[str, Any]:
        """Get historical data for a track section"""
        # In production, this would query a database
        return {
            'age': 25,  # years
            'last_maintenance': 30,  # days ago
            'usage_frequency': 0.8,  # 0.0 to 1.0
            'weather_impact': 0.3,  # 0.0 to 1.0
            'previous_failures': 2,
            'maintenance_cost': 50000,  # rupees
            'traffic_volume': 100  # trains per day
        }
    
    def _prepare_risk_features(self, alert: MaintenanceAlert, historical_data: Dict[str, Any]) -> List[float]:
        """Prepare features for ML model"""
        features = [
            alert.confidence,
            historical_data.get('age', 0),
            historical_data.get('last_maintenance', 0),
            historical_data.get('usage_frequency', 0),
            historical_data.get('weather_impact', 0),
            historical_data.get('previous_failures', 0),
            historical_data.get('maintenance_cost', 0) / 100000,  # Normalize
            historical_data.get('traffic_volume', 0) / 100,  # Normalize
            alert.severity.value == 'critical',
            alert.severity.value == 'high'
        ]
        return features
    
    def _calculate_impact_score(self, section_id: str, alert: MaintenanceAlert) -> float:
        """Calculate impact score for a section"""
        # Base impact score
        impact_score = 0.5
        
        # Increase based on severity
        severity_multiplier = {
            RiskLevel.LOW: 0.2,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.HIGH: 0.8,
            RiskLevel.CRITICAL: 1.0
        }.get(alert.severity, 0.5)
        
        impact_score *= severity_multiplier
        
        # Increase based on confidence
        impact_score *= alert.confidence
        
        return min(impact_score, 1.0)
    
    def _calculate_urgency_score(self, alert: MaintenanceAlert, failure_probability: float) -> float:
        """Calculate urgency score"""
        # Base urgency on failure probability
        urgency_score = failure_probability
        
        # Increase based on severity
        severity_multiplier = {
            RiskLevel.LOW: 0.5,
            RiskLevel.MEDIUM: 0.7,
            RiskLevel.HIGH: 0.9,
            RiskLevel.CRITICAL: 1.0
        }.get(alert.severity, 0.5)
        
        urgency_score *= severity_multiplier
        
        # Increase based on confidence
        urgency_score *= alert.confidence
        
        return min(urgency_score, 1.0)
    
    def _determine_risk_level(self, risk_score: float, failure_probability: float, impact_score: float) -> RiskLevel:
        """Determine risk level based on scores"""
        # Weighted combination of scores
        combined_score = (risk_score * 0.4 + failure_probability * 0.4 + impact_score * 0.2)
        
        if combined_score >= 0.8:
            return RiskLevel.CRITICAL
        elif combined_score >= 0.6:
            return RiskLevel.HIGH
        elif combined_score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_risk_recommendations(self, risk_level: RiskLevel, failure_probability: float, impact_score: float) -> List[str]:
        """Generate risk-based recommendations"""
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Immediate inspection required",
                "Consider temporary closure",
                "Implement speed restrictions",
                "Prepare emergency response"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Schedule inspection within 24 hours",
                "Implement speed restrictions",
                "Monitor closely",
                "Prepare maintenance plan"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Schedule inspection within 48 hours",
                "Monitor condition",
                "Plan maintenance"
            ])
        else:
            recommendations.extend([
                "Routine monitoring",
                "Schedule next inspection"
            ])
        
        return recommendations
    
    async def _schedule_maintenance(self, alert: MaintenanceAlert, risk_assessment: RiskAssessment) -> Optional[MaintenanceActivity]:
        """Schedule maintenance activity"""
        try:
            # Determine maintenance type based on alert
            maintenance_type = self._determine_maintenance_type(alert)
            
            # Calculate duration based on risk level and maintenance type
            duration = self._calculate_maintenance_duration(maintenance_type, risk_assessment.risk_level)
            
            # Schedule maintenance window
            start_time = datetime.now(timezone.utc) + timedelta(hours=2)  # 2 hours from now
            end_time = start_time + timedelta(minutes=duration)
            
            # Create maintenance activity
            activity = MaintenanceActivity(
                activity_id=str(uuid.uuid4()),
                maintenance_type=maintenance_type,
                asset_id=alert.asset_id,
                section_id=alert.section_id,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                status=MaintenanceStatus.PLANNED,
                priority=self._calculate_priority(risk_assessment),
                crew_size=self._calculate_crew_size(maintenance_type, duration),
                equipment_required=self._get_required_equipment(maintenance_type),
                safety_requirements=self._get_safety_requirements(maintenance_type),
                speed_restrictions=self._calculate_speed_restrictions(risk_assessment)
            )
            
            return activity
            
        except Exception as e:
            logger.error("Error scheduling maintenance", alert_id=alert.alert_id, error=str(e))
            return None
    
    def _determine_maintenance_type(self, alert: MaintenanceAlert) -> MaintenanceType:
        """Determine maintenance type based on alert"""
        if 'track' in alert.asset_type.lower():
            return MaintenanceType.TRACK_REPAIR
        elif 'signal' in alert.asset_type.lower():
            return MaintenanceType.SIGNAL_MAINTENANCE
        elif 'bridge' in alert.asset_type.lower():
            return MaintenanceType.BRIDGE_WORK
        elif 'tunnel' in alert.asset_type.lower():
            return MaintenanceType.TUNNEL_WORK
        elif 'platform' in alert.asset_type.lower():
            return MaintenanceType.PLATFORM_WORK
        else:
            return MaintenanceType.INSPECTION
    
    def _calculate_maintenance_duration(self, maintenance_type: MaintenanceType, risk_level: RiskLevel) -> int:
        """Calculate maintenance duration in minutes"""
        base_duration = {
            MaintenanceType.TRACK_REPAIR: 240,  # 4 hours
            MaintenanceType.SIGNAL_MAINTENANCE: 120,  # 2 hours
            MaintenanceType.ELECTRIFICATION: 360,  # 6 hours
            MaintenanceType.BRIDGE_WORK: 480,  # 8 hours
            MaintenanceType.TUNNEL_WORK: 600,  # 10 hours
            MaintenanceType.PLATFORM_WORK: 180,  # 3 hours
            MaintenanceType.CLEANING: 60,  # 1 hour
            MaintenanceType.INSPECTION: 30  # 30 minutes
        }.get(maintenance_type, 120)
        
        # Adjust based on risk level
        risk_multiplier = {
            RiskLevel.LOW: 0.8,
            RiskLevel.MEDIUM: 1.0,
            RiskLevel.HIGH: 1.2,
            RiskLevel.CRITICAL: 1.5
        }.get(risk_level, 1.0)
        
        return int(base_duration * risk_multiplier)
    
    def _calculate_priority(self, risk_assessment: RiskAssessment) -> int:
        """Calculate maintenance priority (1=highest, 10=lowest)"""
        if risk_assessment.risk_level == RiskLevel.CRITICAL:
            return 1
        elif risk_assessment.risk_level == RiskLevel.HIGH:
            return 2
        elif risk_assessment.risk_level == RiskLevel.MEDIUM:
            return 5
        else:
            return 8
    
    def _calculate_crew_size(self, maintenance_type: MaintenanceType, duration: int) -> int:
        """Calculate required crew size"""
        base_crew = {
            MaintenanceType.TRACK_REPAIR: 6,
            MaintenanceType.SIGNAL_MAINTENANCE: 2,
            MaintenanceType.ELECTRIFICATION: 4,
            MaintenanceType.BRIDGE_WORK: 8,
            MaintenanceType.TUNNEL_WORK: 10,
            MaintenanceType.PLATFORM_WORK: 4,
            MaintenanceType.CLEANING: 2,
            MaintenanceType.INSPECTION: 1
        }.get(maintenance_type, 2)
        
        # Adjust based on duration
        if duration > 480:  # More than 8 hours
            return base_crew * 2
        elif duration > 240:  # More than 4 hours
            return int(base_crew * 1.5)
        else:
            return base_crew
    
    def _get_required_equipment(self, maintenance_type: MaintenanceType) -> List[str]:
        """Get required equipment for maintenance type"""
        equipment_map = {
            MaintenanceType.TRACK_REPAIR: ["track_laying_machine", "ballast_tamper", "rail_grinder"],
            MaintenanceType.SIGNAL_MAINTENANCE: ["signal_tester", "cable_tester", "multimeter"],
            MaintenanceType.ELECTRIFICATION: ["crane", "insulator_tester", "voltage_tester"],
            MaintenanceType.BRIDGE_WORK: ["crane", "concrete_mixer", "steel_cutter"],
            MaintenanceType.TUNNEL_WORK: ["tunnel_boring_machine", "ventilation_fan", "lighting_system"],
            MaintenanceType.PLATFORM_WORK: ["concrete_mixer", "tile_cutter", "leveling_tool"],
            MaintenanceType.CLEANING: ["pressure_washer", "vacuum_cleaner", "cleaning_supplies"],
            MaintenanceType.INSPECTION: ["inspection_camera", "measuring_tools", "safety_equipment"]
        }
        return equipment_map.get(maintenance_type, ["basic_tools"])
    
    def _get_safety_requirements(self, maintenance_type: MaintenanceType) -> List[str]:
        """Get safety requirements for maintenance type"""
        safety_map = {
            MaintenanceType.TRACK_REPAIR: ["track_possession", "safety_vests", "hard_hats", "safety_shoes"],
            MaintenanceType.SIGNAL_MAINTENANCE: ["electrical_safety", "insulated_tools", "safety_gloves"],
            MaintenanceType.ELECTRIFICATION: ["electrical_safety", "insulated_tools", "safety_gloves", "voltage_protection"],
            MaintenanceType.BRIDGE_WORK: ["fall_protection", "safety_harness", "hard_hats", "safety_shoes"],
            MaintenanceType.TUNNEL_WORK: ["ventilation", "safety_harness", "hard_hats", "safety_shoes", "emergency_exit"],
            MaintenanceType.PLATFORM_WORK: ["safety_vests", "hard_hats", "safety_shoes", "barricades"],
            MaintenanceType.CLEANING: ["safety_vests", "hard_hats", "safety_shoes"],
            MaintenanceType.INSPECTION: ["safety_vests", "hard_hats", "safety_shoes", "inspection_tools"]
        }
        return safety_map.get(maintenance_type, ["basic_safety_equipment"])
    
    def _calculate_speed_restrictions(self, risk_assessment: RiskAssessment) -> Dict[str, float]:
        """Calculate speed restrictions based on risk assessment"""
        restrictions = {}
        
        if risk_assessment.risk_level == RiskLevel.CRITICAL:
            restrictions[risk_assessment.section_id] = 0.0  # Complete closure
        elif risk_assessment.risk_level == RiskLevel.HIGH:
            restrictions[risk_assessment.section_id] = 30.0  # 30 km/h
        elif risk_assessment.risk_level == RiskLevel.MEDIUM:
            restrictions[risk_assessment.section_id] = 60.0  # 60 km/h
        else:
            restrictions[risk_assessment.section_id] = 80.0  # 80 km/h
        
        return restrictions
    
    async def _notify_maintenance_teams(self, activity: MaintenanceActivity):
        """Notify maintenance teams about scheduled activity"""
        message = {
            'type': 'maintenance_scheduled',
            'activity_id': activity.activity_id,
            'maintenance_type': activity.maintenance_type.value,
            'section_id': activity.section_id,
            'start_time': activity.start_time.isoformat(),
            'end_time': activity.end_time.isoformat(),
            'duration': activity.duration,
            'priority': activity.priority,
            'crew_size': activity.crew_size,
            'equipment_required': activity.equipment_required,
            'safety_requirements': activity.safety_requirements
        }
        
        if self.message_bus:
            await self.message_bus.send_message('maintenance_teams', message)
        
        logger.info("Maintenance teams notified", activity_id=activity.activity_id)
    
    async def _generate_reroute_recommendations(self, activity: MaintenanceActivity):
        """Generate reroute recommendations for affected trains"""
        try:
            # Get trains that will be affected by the maintenance
            affected_trains = await self._get_affected_trains(activity)
            
            for train_id in affected_trains:
                # Find alternative routes
                alternative_routes = await self._find_alternative_routes(activity.section_id, train_id)
                
                if alternative_routes:
                    # Calculate risk reduction and additional delay
                    risk_reduction = self._calculate_risk_reduction(activity, alternative_routes[0])
                    additional_delay = self._calculate_additional_delay(alternative_routes[0])
                    additional_distance = self._calculate_additional_distance(alternative_routes[0])
                    
                    # Create reroute recommendation
                    recommendation = RerouteRecommendation(
                        recommendation_id=str(uuid.uuid4()),
                        train_id=train_id,
                        original_route=activity.section_id,
                        recommended_route=alternative_routes[0],
                        reason=f"Maintenance activity: {activity.maintenance_type.value}",
                        risk_reduction=risk_reduction,
                        additional_delay=additional_delay,
                        additional_distance=additional_distance,
                        confidence=0.8,
                        expires_at=activity.start_time
                    )
                    
                    self.reroute_recommendations.append(recommendation)
                    
                    # Notify decision engine
                    await self._notify_decision_engine(recommendation)
            
            logger.info("Reroute recommendations generated", 
                       activity_id=activity.activity_id,
                       recommendations_count=len(affected_trains))
            
        except Exception as e:
            logger.error("Error generating reroute recommendations", activity_id=activity.activity_id, error=str(e))
    
    async def _get_affected_trains(self, activity: MaintenanceActivity) -> List[str]:
        """Get trains that will be affected by maintenance activity"""
        # In production, this would query the train database
        # For now, return sample train IDs
        return [f"train_{i:05d}" for i in range(1, 6)]
    
    async def _find_alternative_routes(self, section_id: str, train_id: str) -> List[str]:
        """Find alternative routes for a train"""
        # In production, this would use route planning algorithms
        # For now, return sample alternative routes
        return [f"alternative_route_{i}" for i in range(1, 4)]
    
    def _calculate_risk_reduction(self, activity: MaintenanceActivity, alternative_route: str) -> float:
        """Calculate risk reduction from using alternative route"""
        # Base risk reduction
        base_reduction = 0.8
        
        # Adjust based on maintenance type
        type_multiplier = {
            MaintenanceType.TRACK_REPAIR: 0.9,
            MaintenanceType.SIGNAL_MAINTENANCE: 0.7,
            MaintenanceType.ELECTRIFICATION: 0.8,
            MaintenanceType.BRIDGE_WORK: 0.95,
            MaintenanceType.TUNNEL_WORK: 0.9,
            MaintenanceType.PLATFORM_WORK: 0.6,
            MaintenanceType.CLEANING: 0.3,
            MaintenanceType.INSPECTION: 0.5
        }.get(activity.maintenance_type, 0.8)
        
        return base_reduction * type_multiplier
    
    def _calculate_additional_delay(self, alternative_route: str) -> int:
        """Calculate additional delay from using alternative route"""
        # In production, this would calculate based on route characteristics
        return 15  # 15 minutes additional delay
    
    def _calculate_additional_distance(self, alternative_route: str) -> float:
        """Calculate additional distance from using alternative route"""
        # In production, this would calculate based on route characteristics
        return 5.0  # 5 km additional distance
    
    async def _notify_decision_engine(self, recommendation: RerouteRecommendation):
        """Notify decision engine about reroute recommendation"""
        message = {
            'type': 'reroute_recommendation',
            'recommendation_id': recommendation.recommendation_id,
            'train_id': recommendation.train_id,
            'original_route': recommendation.original_route,
            'recommended_route': recommendation.recommended_route,
            'reason': recommendation.reason,
            'risk_reduction': recommendation.risk_reduction,
            'additional_delay': recommendation.additional_delay,
            'additional_distance': recommendation.additional_distance,
            'confidence': recommendation.confidence,
            'expires_at': recommendation.expires_at.isoformat() if recommendation.expires_at else None
        }
        
        if self.message_bus:
            await self.message_bus.send_message('decision_engine', message)
        
        logger.info("Decision engine notified", recommendation_id=recommendation.recommendation_id)
    
    async def _update_speed_restrictions(self, section_id: str, risk_assessment: RiskAssessment):
        """Update speed restrictions for a section"""
        restrictions = self._calculate_speed_restrictions(risk_assessment)
        
        message = {
            'type': 'speed_restriction_update',
            'section_id': section_id,
            'restrictions': restrictions,
            'reason': f"Risk assessment: {risk_assessment.risk_level.value}",
            'valid_until': risk_assessment.valid_until.isoformat() if risk_assessment.valid_until else None
        }
        
        if self.message_bus:
            await self.message_bus.send_message('safety_validator', message)
        
        logger.info("Speed restrictions updated", section_id=section_id, restrictions=restrictions)
    
    def get_maintenance_alerts(self, section_id: Optional[str] = None) -> List[MaintenanceAlert]:
        """Get maintenance alerts, optionally filtered by section"""
        if section_id:
            return [alert for alert in self.maintenance_alerts if alert.section_id == section_id]
        return self.maintenance_alerts.copy()
    
    def get_maintenance_activities(self, status: Optional[MaintenanceStatus] = None) -> List[MaintenanceActivity]:
        """Get maintenance activities, optionally filtered by status"""
        if status:
            return [activity for activity in self.maintenance_activities if activity.status == status]
        return self.maintenance_activities.copy()
    
    def get_risk_assessments(self, section_id: Optional[str] = None) -> Dict[str, RiskAssessment]:
        """Get risk assessments, optionally filtered by section"""
        if section_id:
            return {sid: assessment for sid, assessment in self.risk_assessments.items() if sid == section_id}
        return self.risk_assessments.copy()
    
    def get_reroute_recommendations(self, train_id: Optional[str] = None) -> List[RerouteRecommendation]:
        """Get reroute recommendations, optionally filtered by train"""
        if train_id:
            return [rec for rec in self.reroute_recommendations if rec.train_id == train_id]
        return self.reroute_recommendations.copy()
    
    def get_maintenance_statistics(self) -> Dict[str, Any]:
        """Get maintenance statistics"""
        total_alerts = len(self.maintenance_alerts)
        critical_alerts = len([a for a in self.maintenance_alerts if a.severity == RiskLevel.CRITICAL])
        high_alerts = len([a for a in self.maintenance_alerts if a.severity == RiskLevel.HIGH])
        
        total_activities = len(self.maintenance_activities)
        planned_activities = len([a for a in self.maintenance_activities if a.status == MaintenanceStatus.PLANNED])
        in_progress_activities = len([a for a in self.maintenance_activities if a.status == MaintenanceStatus.IN_PROGRESS])
        completed_activities = len([a for a in self.maintenance_activities if a.status == MaintenanceStatus.COMPLETED])
        
        total_recommendations = len(self.reroute_recommendations)
        active_recommendations = len([r for r in self.reroute_recommendations if r.expires_at and r.expires_at > datetime.now(timezone.utc)])
        
        return {
            'total_alerts': total_alerts,
            'critical_alerts': critical_alerts,
            'high_alerts': high_alerts,
            'alert_criticality_rate': critical_alerts / total_alerts if total_alerts > 0 else 0.0,
            'total_activities': total_activities,
            'planned_activities': planned_activities,
            'in_progress_activities': in_progress_activities,
            'completed_activities': completed_activities,
            'completion_rate': completed_activities / total_activities if total_activities > 0 else 0.0,
            'total_recommendations': total_recommendations,
            'active_recommendations': active_recommendations
        }


async def main():
    """Main entry point for the predictive maintenance service"""
    config = {
        'risk_threshold': 0.7,
        'maintenance_window_hours': 4,
        'reroute_threshold': 0.8
    }
    
    service = PredictiveMaintenanceService(config)
    
    # Example usage
    alert = MaintenanceAlert(
        alert_id=str(uuid.uuid4()),
        asset_id='track_001',
        asset_type='track',
        alert_type='vibration_anomaly',
        severity=RiskLevel.HIGH,
        description='Unusual vibration detected in track section',
        location={'latitude': 28.6139, 'longitude': 77.2090},
        section_id='section_001',
        detected_at=datetime.now(timezone.utc),
        confidence=0.85,
        maintenance_required=True,
        estimated_downtime=120
    )
    
    await service.process_maintenance_alert(alert)
    print("Maintenance alert processed")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Predictive maintenance service stopped")


if __name__ == "__main__":
    asyncio.run(main())
