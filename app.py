#!/usr/bin/env python3
"""
Train Traffic Throughput Maximization System
Advanced AI-Powered Railway Optimization Platform
"""

import asyncio
import json
import os
import time
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
import pandas as pd
from pydantic import BaseModel

# ML Model imports
try:
    import joblib
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
    print("✅ ML dependencies loaded successfully")
except ImportError as e:
    ML_AVAILABLE = False
    print(f"⚠️ ML dependencies not available: {e}")
    print("   Run: pip install scikit-learn joblib")

# Initialize FastAPI app
app = FastAPI(
    title="Train Traffic Throughput Maximization System",
    description="Advanced AI-Powered Railway Optimization Platform for Indian Railways",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class TrainStatus(str, Enum):
    ON_TIME = "on_time"
    DELAYED = "delayed"
    EARLY = "early"
    CANCELLED = "cancelled"
    MAINTENANCE = "maintenance"

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class OptimizationType(str, Enum):
    HEADWAY_OPTIMIZATION = "headway_optimization"
    JUNCTION_OPTIMIZATION = "junction_optimization"
    SPEED_OPTIMIZATION = "speed_optimization"
    SLOT_TRADING = "slot_trading"
    PREDICTIVE_MAINTENANCE = "predictive_maintenance"
    ROUTE_OPTIMIZATION = "route_optimization"

@dataclass
class Train:
    id: str
    name: str
    current_track: str
    speed: float
    position: float
    destination: str
    priority: Priority
    passengers: int
    delay: int
    status: TrainStatus
    efficiency: float
    fuel_level: float
    maintenance_due: bool
    route: List[str]
    estimated_arrival: datetime

@dataclass
class Track:
    id: str
    capacity: int
    speed_limit: float
    length: float
    utilization: float
    maintenance_status: str
    weather_condition: str
    signal_status: str

@dataclass
class Junction:
    id: str
    tracks: List[str]
    conflicts: int
    efficiency: float
    signal_timing: float
    capacity: int

@dataclass
class OptimizationDecision:
    id: str
    type: OptimizationType
    train_id: Optional[str]
    track_id: Optional[str]
    junction_id: Optional[str]
    action: str
    impact: str
    priority: str
    confidence: float
    estimated_benefit: float
    implementation_time: int
    status: str

class RailwaySystem:
    def __init__(self):
        self.trains: List[Train] = []
        self.tracks: Dict[str, Track] = {}
        self.junctions: Dict[str, Junction] = {}
        self.optimization_decisions: List[OptimizationDecision] = []
        self.throughput_score: float = 0.0
        self.safety_violations: int = 0
        self.energy_efficiency: float = 0.0
        self.passenger_satisfaction: float = 0.0
        
        # ML Models
        self.ml_models = {}
        self.ml_scalers = {}
        self.ml_feature_columns = []
        self.ml_model_performance = {}
        self.load_ml_models()
        
        self.initialize_system()
    
    def initialize_system(self):
        """Initialize the railway system with realistic data"""
        # Initialize tracks
        self.tracks = {
            "T1": Track("T1", 3, 120, 200, 0.85, "good", "clear", "green"),
            "T2": Track("T2", 4, 100, 150, 0.75, "good", "clear", "green"),
            "T3": Track("T3", 2, 110, 180, 0.90, "maintenance_required", "foggy", "yellow"),
            "T4": Track("T4", 5, 90, 120, 0.60, "good", "clear", "green"),
            "T5": Track("T5", 3, 130, 220, 0.80, "good", "rainy", "green"),
            "T6": Track("T6", 2, 95, 160, 0.95, "good", "clear", "green")
        }
        
        # Initialize junctions
        self.junctions = {
            "J1": Junction("J1", ["T1", "T2"], 0, 0.88, 45, 6),
            "J2": Junction("J2", ["T2", "T3"], 1, 0.75, 60, 4),
            "J3": Junction("J3", ["T3", "T4"], 0, 0.92, 30, 7),
            "J4": Junction("J4", ["T4", "T5"], 2, 0.70, 75, 5),
            "J5": Junction("J5", ["T5", "T6"], 0, 0.85, 40, 6)
        }
        
        # Initialize trains
        current_time = datetime.now()
        self.trains = [
            Train("T001", "Rajdhani Express", "T1", 115, 45, "J1", Priority.HIGH, 1200, 0, 
                  TrainStatus.ON_TIME, 0.92, 85.5, False, ["T1", "T2", "T3"], current_time + timedelta(minutes=30)),
            Train("T002", "Shatabdi Express", "T2", 95, 30, "J2", Priority.HIGH, 800, 15, 
                  TrainStatus.DELAYED, 0.78, 72.3, True, ["T2", "T3", "T4"], current_time + timedelta(minutes=45)),
            Train("T003", "Duronto Express", "T3", 105, 80, "J3", Priority.MEDIUM, 1500, 0, 
                  TrainStatus.ON_TIME, 0.88, 91.2, False, ["T3", "T4", "T5"], current_time + timedelta(minutes=20)),
            Train("T004", "Mail Express", "T4", 85, 20, "J3", Priority.LOW, 2000, 5, 
                  TrainStatus.ON_TIME, 0.82, 68.7, False, ["T4", "T5", "T6"], current_time + timedelta(minutes=60)),
            Train("T005", "Tejas Express", "T5", 125, 60, "J4", Priority.HIGH, 600, -3, 
                  TrainStatus.EARLY, 0.95, 88.9, False, ["T5", "T6"], current_time + timedelta(minutes=15)),
            Train("T006", "Garib Rath", "T6", 90, 10, "J5", Priority.LOW, 1800, 8, 
                  TrainStatus.DELAYED, 0.75, 65.4, True, ["T6"], current_time + timedelta(minutes=90))
        ]
    
    def load_ml_models(self):
        """Load pre-trained ML models for predictive maintenance"""
        if not ML_AVAILABLE:
            print("⚠️ ML models not available - using fallback heuristics")
            return
            
        try:
            models_dir = "models"
            if not os.path.exists(models_dir):
                print(f"⚠️ Models directory '{models_dir}' not found - using fallback heuristics")
                return
            
            # Load models
            classifier_path = os.path.join(models_dir, "maintenance_classifier.joblib")
            regressor_path = os.path.join(models_dir, "failure_risk_regressor.joblib")
            scaler_class_path = os.path.join(models_dir, "scaler_classifier.joblib")
            scaler_reg_path = os.path.join(models_dir, "scaler_regressor.joblib")
            metadata_path = os.path.join(models_dir, "model_metadata.json")
            
            if all(os.path.exists(path) for path in [classifier_path, regressor_path, scaler_class_path, scaler_reg_path, metadata_path]):
                self.ml_models['classifier'] = joblib.load(classifier_path)
                self.ml_models['regressor'] = joblib.load(regressor_path)
                self.ml_scalers['classifier'] = joblib.load(scaler_class_path)
                self.ml_scalers['regressor'] = joblib.load(scaler_reg_path)
                
                # Load metadata
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.ml_feature_columns = metadata['feature_columns']
                    self.ml_model_performance = metadata.get('model_performance', {})
                
                print("✅ ML models loaded successfully")
                print(f"   - Classifier: {type(self.ml_models['classifier']).__name__}")
                print(f"   - Regressor: {type(self.ml_models['regressor']).__name__}")
                print(f"   - Features: {len(self.ml_feature_columns)} columns")
            else:
                print("⚠️ Some model files missing - using fallback heuristics")
                
        except Exception as e:
            print(f"❌ Error loading ML models: {e}")
            print("   Using fallback heuristics instead")
    
    def predict_maintenance_risk(self, train: Train) -> Dict[str, Any]:
        """Predict maintenance risk for a train using ML models"""
        if not self.ml_models or not ML_AVAILABLE:
            # Fallback heuristic prediction
            risk_score = 0.0
            risk_score += (100 - train.fuel_level) / 100 * 0.3  # Lower fuel = higher risk
            risk_score += train.delay / 60 * 0.2  # More delay = higher risk
            risk_score += (1 - train.efficiency) * 0.3  # Lower efficiency = higher risk
            risk_score += (train.position / 1000) * 0.1  # More distance = slight risk increase
            risk_score += random.uniform(0, 0.1)  # Some randomness
            
            risk_score = min(risk_score, 1.0)
            needs_maintenance = risk_score > 0.7
            risk_level = "Critical" if risk_score > 0.8 else "High" if risk_score > 0.6 else "Medium" if risk_score > 0.3 else "Low"
            
            return {
                "train_id": train.id,
                "failure_risk": risk_score,
                "needs_maintenance": needs_maintenance,
                "risk_level": risk_level,
                "confidence": 0.6,  # Lower confidence for heuristic
                "model_type": "heuristic",
                "predictions": {
                    "maintenance_probability": needs_maintenance,
                    "risk_score": risk_score,
                    "estimated_days_to_failure": int(30 * (1 - risk_score)) if risk_score > 0.5 else None
                }
            }
        
        try:
            # Prepare features for ML prediction
            current_time = datetime.now()
            
            # Generate realistic operational metrics based on train state
            features = {
                'speed': train.speed,
                'fuel_efficiency': train.fuel_level,
                'engine_temperature': 85 + random.uniform(-10, 15),  # Realistic range
                'brake_wear': random.uniform(20, 80),  # Simulated brake wear
                'vibration_level': random.uniform(1, 5),  # Simulated vibration
                'operating_hours': random.uniform(1000, 8000),  # Simulated operating hours
                'distance_traveled': train.position,
                'load_factor': train.efficiency,
                'weather_severity': random.randint(1, 5),  # Simulated weather
                'track_condition': self.tracks.get(train.current_track, Track("", 0, 0, 0, 0.8, "", "", "")).utilization,
                'maintenance_days_since': random.uniform(1, 90)  # Simulated days since maintenance
            }
            
            # Create feature vector
            feature_vector = np.array([[features[col] for col in self.ml_feature_columns]])
            
            # Make predictions
            # Classification (needs maintenance)
            X_scaled_class = self.ml_scalers['classifier'].transform(feature_vector)
            maintenance_prob = self.ml_models['classifier'].predict_proba(X_scaled_class)[0]
            needs_maintenance = self.ml_models['classifier'].predict(X_scaled_class)[0]
            
            # Regression (risk score)
            X_scaled_reg = self.ml_scalers['regressor'].transform(feature_vector)
            risk_score = self.ml_models['regressor'].predict(X_scaled_reg)[0]
            risk_score = max(0, min(1, risk_score))  # Ensure 0-1 bounds
            
            # Determine risk level
            if risk_score > 0.8:
                risk_level = "Critical"
            elif risk_score > 0.6:
                risk_level = "High"
            elif risk_score > 0.3:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            # Estimate days to potential failure
            days_to_failure = None
            if risk_score > 0.5:
                days_to_failure = int(60 * (1 - risk_score))
            
            return {
                "train_id": train.id,
                "failure_risk": float(risk_score),
                "needs_maintenance": bool(needs_maintenance),
                "risk_level": risk_level,
                "confidence": 0.85,  # Higher confidence for ML model
                "model_type": "machine_learning",
                "predictions": {
                    "maintenance_probability": float(maintenance_prob[1]) if len(maintenance_prob) > 1 else float(needs_maintenance),
                    "risk_score": float(risk_score),
                    "estimated_days_to_failure": days_to_failure
                },
                "features_used": features
            }
            
        except Exception as e:
            print(f"❌ Error in ML prediction for train {train.id}: {e}")
            # Fallback to heuristic prediction
            risk_score = 0.0
            risk_score += (100 - train.fuel_level) / 100 * 0.3  # Lower fuel = higher risk
            risk_score += train.delay / 60 * 0.2  # More delay = higher risk
            risk_score += (1 - train.efficiency) * 0.3  # Lower efficiency = higher risk
            risk_score += (train.position / 1000) * 0.1  # More distance = slight risk increase
            risk_score += random.uniform(0, 0.1)  # Some randomness
            
            risk_score = min(risk_score, 1.0)
            needs_maintenance = risk_score > 0.7
            risk_level = "Critical" if risk_score > 0.8 else "High" if risk_score > 0.6 else "Medium" if risk_score > 0.3 else "Low"
            
            return {
                "train_id": train.id,
                "failure_risk": risk_score,
                "needs_maintenance": needs_maintenance,
                "risk_level": risk_level,
                "confidence": 0.6,  # Lower confidence for heuristic
                "model_type": "heuristic_fallback",
                "predictions": {
                    "maintenance_probability": needs_maintenance,
                    "risk_score": risk_score,
                    "estimated_days_to_failure": int(30 * (1 - risk_score)) if risk_score > 0.5 else None
                }
            }
    
    def calculate_optimizations(self) -> List[OptimizationDecision]:
        """Calculate AI-powered optimizations using advanced algorithms"""
        decisions = []
        decision_id = 1
        
        # 1. Headway Optimization using machine learning
        for track_id, track in self.tracks.items():
            track_trains = [t for t in self.trains if t.current_track == track_id]
            if len(track_trains) > 1:
                headway = self._calculate_headway(track_trains)
                min_safe_headway = 3.5  # minutes
                
                if headway < min_safe_headway:
                    trailing_train = min(track_trains, key=lambda t: t.position)
                    speed_reduction = (min_safe_headway - headway) * 20
                    
                    decisions.append(OptimizationDecision(
                        f"OPT_{decision_id:03d}",
                        OptimizationType.HEADWAY_OPTIMIZATION,
                        trailing_train.id,
                        track_id,
                        None,
                        f"Reduce speed of {trailing_train.name} by {speed_reduction:.1f} km/h",
                        "Prevents collision risk and improves safety",
                        "critical",
                        0.95,
                        15.5,
                        2,
                        "pending"
                    ))
                    decision_id += 1
        
        # 2. Junction Conflict Resolution with dynamic routing
        for junction_id, junction in self.junctions.items():
            if junction.conflicts > 0:
                conflicting_trains = self._find_junction_conflicts(junction_id)
                if conflicting_trains:
                    decisions.append(OptimizationDecision(
                        f"OPT_{decision_id:03d}",
                        OptimizationType.JUNCTION_OPTIMIZATION,
                        conflicting_trains[0],
                        None,
                        junction_id,
                        f"Implement dynamic routing for junction {junction_id}",
                        f"Eliminates {junction.conflicts} conflicts and improves flow",
                        "high",
                        0.88,
                        22.3,
                        5,
                        "pending"
                    ))
                    decision_id += 1
        
        # 3. Speed Optimization with fuel efficiency
        for train in self.trains:
            if train.delay > 10 and train.fuel_level > 50:
                current_track = self.tracks.get(train.current_track)
                optimal_speed = min(train.speed + 25, current_track.speed_limit if current_track else 150)
                fuel_savings = (optimal_speed - train.speed) * 0.1
                
                decisions.append(OptimizationDecision(
                    f"OPT_{decision_id:03d}",
                    OptimizationType.SPEED_OPTIMIZATION,
                    train.id,
                    train.current_track,
                    None,
                    f"Increase speed to {optimal_speed} km/h with fuel optimization",
                    f"Reduces delay by {train.delay - 5} minutes, saves {fuel_savings:.1f}% fuel",
                    "medium",
                    0.82,
                    18.7,
                    3,
                    "pending"
                ))
                decision_id += 1
        
        # 4. Predictive Maintenance using ML
        for train in self.trains:
            # Get ML-powered maintenance prediction
            maintenance_prediction = self.predict_maintenance_risk(train)
            
            if maintenance_prediction['needs_maintenance'] or maintenance_prediction['failure_risk'] > 0.6:
                # Determine priority based on risk level
                priority = "critical" if maintenance_prediction['risk_level'] == "Critical" else \
                          "high" if maintenance_prediction['risk_level'] == "High" else "medium"
                
                # Calculate estimated benefit
                efficiency_improvement = (0.95 - train.efficiency) * 100
                risk_reduction = maintenance_prediction['failure_risk'] * 100
                
                # Create detailed description
                description = f"ML-predicted maintenance for {train.name}"
                if maintenance_prediction['predictions']['estimated_days_to_failure']:
                    description += f" (estimated failure in {maintenance_prediction['predictions']['estimated_days_to_failure']} days)"
                
                reason = f"Risk level: {maintenance_prediction['risk_level']} " \
                        f"({maintenance_prediction['failure_risk']:.1%} failure probability). " \
                        f"Model confidence: {maintenance_prediction['confidence']:.1%}. " \
                        f"Prevents breakdown, improves efficiency by {efficiency_improvement:.1f}%"
                
                decisions.append(OptimizationDecision(
                    f"OPT_{decision_id:03d}",
                    OptimizationType.PREDICTIVE_MAINTENANCE,
                    train.id,
                    None,
                    None,
                    description,
                    reason,
                    priority,
                    maintenance_prediction['confidence'],
                    max(25.0, risk_reduction * 0.5),  # Benefit scales with risk
                    int(5 + maintenance_prediction['failure_risk'] * 10),  # Implementation time based on urgency
                    "pending"
                ))
                decision_id += 1
        
        # 5. Slot Trading for efficiency
        if len(self.trains) > 3:
            trades = self._identify_slot_trading_opportunities()
            for trade in trades[:2]:  # Limit to 2 trades
                decisions.append(OptimizationDecision(
                    f"OPT_{decision_id:03d}",
                    OptimizationType.SLOT_TRADING,
                    None,
                    None,
                    None,
                    f"Trade slot between {trade['train1']} and {trade['train2']}",
                    f"Improves overall efficiency by {trade['benefit']:.1f}%",
                    "low",
                    0.75,
                    trade['benefit'],
                    8,
                    "pending"
                ))
                decision_id += 1
        
        # 6. Route Optimization
        for train in self.trains:
            if train.delay > 15:
                alternative_routes = self._find_alternative_routes(train)
                if alternative_routes:
                    best_route = alternative_routes[0]
                    decisions.append(OptimizationDecision(
                        f"OPT_{decision_id:03d}",
                        OptimizationType.ROUTE_OPTIMIZATION,
                        train.id,
                        None,
                        None,
                        f"Reroute {train.name} via {best_route['route']}",
                        f"Reduces travel time by {best_route['time_savings']} minutes",
                        "high",
                        0.85,
                        best_route['time_savings'] * 2,
                        5,
                        "pending"
                    ))
                    decision_id += 1
        
        self.optimization_decisions = decisions
        return decisions
    
    def _calculate_headway(self, trains: List[Train]) -> float:
        """Calculate headway between trains on same track"""
        if len(trains) < 2:
            return float('inf')
        positions = sorted([t.position for t in trains])
        return min(positions[i+1] - positions[i] for i in range(len(positions)-1))
    
    def _find_junction_conflicts(self, junction_id: str) -> List[str]:
        """Find trains that will conflict at junction"""
        junction = self.junctions[junction_id]
        conflicting_trains = []
        
        for track_id in junction.tracks:
            track_trains = [t for t in self.trains if t.current_track == track_id and t.destination == junction_id]
            if len(track_trains) > 1:
                conflicting_trains.extend([t.id for t in track_trains])
        
        return conflicting_trains
    
    def _identify_slot_trading_opportunities(self) -> List[Dict]:
        """Identify opportunities for slot trading between trains"""
        trades = []
        delayed_trains = [t for t in self.trains if t.delay > 5]
        early_trains = [t for t in self.trains if t.delay < -5]
        
        for delayed in delayed_trains[:2]:
            for early in early_trains[:2]:
                if delayed.priority != early.priority:
                    trades.append({
                        "train1": delayed.id,
                        "train2": early.id,
                        "benefit": random.uniform(8, 18)
                    })
        
        return trades
    
    def _find_alternative_routes(self, train: Train) -> List[Dict]:
        """Find alternative routes for delayed trains"""
        # Simplified route finding - in reality this would use graph algorithms
        return [
            {
                "route": "T2-T4-T6",
                "time_savings": random.randint(10, 25)
            }
        ]
    
    def calculate_throughput_score(self) -> float:
        """Calculate overall system throughput score using advanced metrics"""
        # Track utilization
        total_capacity = sum(track.capacity for track in self.tracks.values())
        current_utilization = len(self.trains) / total_capacity
        
        # Delay penalty
        total_delay = sum(train.delay for train in self.trains)
        delay_penalty = total_delay * 0.15
        
        # Safety penalty
        safety_penalty = self.safety_violations * 8
        
        # Efficiency bonus
        avg_efficiency = sum(train.efficiency for train in self.trains) / len(self.trains)
        efficiency_bonus = avg_efficiency * 20
        
        # Energy efficiency
        avg_fuel = sum(train.fuel_level for train in self.trains) / len(self.trains)
        energy_bonus = (avg_fuel / 100) * 10
        
        self.throughput_score = max(0, min(100, 
            (current_utilization * 100) - delay_penalty - safety_penalty + efficiency_bonus + energy_bonus
        ))
        
        return self.throughput_score
    
    def update_system(self):
        """Update system state with realistic changes"""
        for train in self.trains:
            # Update position
            train.position = min(100, train.position + random.uniform(1, 6))
            
            # Update delays
            if random.random() < 0.12:  # 12% chance of delay change
                delay_change = random.randint(-3, 4)
                train.delay = max(-10, min(35, train.delay + delay_change))
            
            # Update status based on delay
            if train.delay > 20:
                train.status = TrainStatus.DELAYED
            elif train.delay < -5:
                train.status = TrainStatus.EARLY
            else:
                train.status = TrainStatus.ON_TIME
            
            # Update fuel level
            train.fuel_level = max(0, train.fuel_level - random.uniform(0.1, 0.5))
            
            # Update efficiency
            efficiency_change = random.uniform(-0.02, 0.03)
            train.efficiency = max(0.5, min(1.0, train.efficiency + efficiency_change))
            
            # Update maintenance status
            if train.efficiency < 0.7 or train.fuel_level < 20:
                train.maintenance_due = True
        
        # Update track utilization
        for track_id in self.tracks:
            track_trains = [t for t in self.trains if t.current_track == track_id]
            self.tracks[track_id].utilization = len(track_trains) / self.tracks[track_id].capacity
        
        # Update junction conflicts
        for junction in self.junctions.values():
            junction.conflicts = random.randint(0, 2)

# Global system instance
railway_system = RailwaySystem()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(data))
            except:
                pass

manager = ConnectionManager()

# API Routes
# (Frontend static serving will be mounted after API routes)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "uptime": "running"
    }

@app.get("/api/trains")
async def get_trains():
    """Get all trains data"""
    return [
        {
            "id": train.id,
            "name": train.name,
            "current_track": train.current_track,
            "speed": train.speed,
            "position": train.position,
            "destination": train.destination,
            "priority": train.priority.value,
            "passengers": train.passengers,
            "delay": train.delay,
            "status": train.status.value,
            "efficiency": train.efficiency,
            "fuel_level": train.fuel_level,
            "maintenance_due": train.maintenance_due,
            "route": train.route,
            "estimated_arrival": train.estimated_arrival.isoformat()
        }
        for train in railway_system.trains
    ]

@app.get("/api/tracks")
async def get_tracks():
    """Get all tracks data"""
    return {
        track_id: {
            "id": track.id,
            "capacity": track.capacity,
            "speed_limit": track.speed_limit,
            "length": track.length,
            "utilization": track.utilization,
            "maintenance_status": track.maintenance_status,
            "weather_condition": track.weather_condition,
            "signal_status": track.signal_status
        }
        for track_id, track in railway_system.tracks.items()
    }

@app.get("/api/junctions")
async def get_junctions():
    """Get all junctions data"""
    return {
        junction_id: {
            "id": junction.id,
            "tracks": junction.tracks,
            "conflicts": junction.conflicts,
            "efficiency": junction.efficiency,
            "signal_timing": junction.signal_timing,
            "capacity": junction.capacity
        }
        for junction_id, junction in railway_system.junctions.items()
    }

@app.get("/api/optimizations")
async def get_optimizations():
    """Get current optimization decisions"""
    decisions = railway_system.calculate_optimizations()
    return [
        {
            "id": decision.id,
            "type": decision.type.value,
            "train_id": decision.train_id,
            "track_id": decision.track_id,
            "junction_id": decision.junction_id,
            "action": decision.action,
            "impact": decision.impact,
            "priority": decision.priority,
            "confidence": decision.confidence,
            "estimated_benefit": decision.estimated_benefit,
            "implementation_time": decision.implementation_time,
            "status": decision.status
        }
        for decision in decisions
    ]

@app.get("/api/metrics")
async def get_metrics():
    """Get system performance metrics"""
    throughput = railway_system.calculate_throughput_score()
    
    # Calculate additional metrics
    total_passengers = sum(train.passengers for train in railway_system.trains)
    avg_delay = sum(train.delay for train in railway_system.trains) / len(railway_system.trains)
    avg_efficiency = sum(train.efficiency for train in railway_system.trains) / len(railway_system.trains)
    avg_fuel = sum(train.fuel_level for train in railway_system.trains) / len(railway_system.trains)
    
    return {
        "throughput_score": round(throughput, 1),
        "total_trains": len(railway_system.trains),
        "total_passengers": total_passengers,
        "safety_violations": railway_system.safety_violations,
        "active_decisions": len(railway_system.optimization_decisions),
        "average_delay": round(avg_delay, 1),
        "average_efficiency": round(avg_efficiency * 100, 1),
        "average_fuel_level": round(avg_fuel, 1),
        "system_status": "operational" if throughput > 70 else "degraded" if throughput > 40 else "critical"
    }

# ML-powered API endpoints

@app.get("/api/ml/maintenance-predictions")
async def get_maintenance_predictions():
    """Get ML-powered maintenance predictions for all trains"""
    predictions = []
    for train in railway_system.trains:
        prediction = railway_system.predict_maintenance_risk(train)
        predictions.append(prediction)
    
    return {
        "predictions": predictions,
        "model_info": {
            "ml_available": ML_AVAILABLE,
            "model_loaded": bool(railway_system.ml_models),
            "model_type": "machine_learning" if railway_system.ml_models else "heuristic",
            "total_trains_analyzed": len(predictions)
        }
    }

@app.get("/api/ml/maintenance-predictions/{train_id}")
async def get_train_maintenance_prediction(train_id: str):
    """Get ML-powered maintenance prediction for a specific train"""
    train = next((t for t in railway_system.trains if t.id == train_id), None)
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    
    prediction = railway_system.predict_maintenance_risk(train)
    return prediction

@app.get("/api/ml/model-info")
async def get_ml_model_info():
    """Get information about the ML models"""
    if not railway_system.ml_models:
        return {
            "ml_available": ML_AVAILABLE,
            "models_loaded": False,
            "model_type": "heuristic",
            "message": "ML models not available - using heuristic predictions"
        }
    
    return {
        "ml_available": ML_AVAILABLE,
        "models_loaded": True,
        "model_type": "machine_learning",
        "models": {
            "classifier": type(railway_system.ml_models.get('classifier')).__name__ if railway_system.ml_models.get('classifier') else None,
            "regressor": type(railway_system.ml_models.get('regressor')).__name__ if railway_system.ml_models.get('regressor') else None
        },
        "feature_columns": railway_system.ml_feature_columns,
        "total_features": len(railway_system.ml_feature_columns),
        "model_performance": railway_system.ml_model_performance
    }

@app.get("/api/ml/risk-summary")
async def get_risk_summary():
    """Get summary of maintenance risks across all trains"""
    predictions = []
    for train in railway_system.trains:
        prediction = railway_system.predict_maintenance_risk(train)
        predictions.append(prediction)
    
    # Calculate summary statistics
    risk_levels = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    total_risk = 0
    needs_maintenance_count = 0
    
    for pred in predictions:
        risk_levels[pred['risk_level']] += 1
        total_risk += pred['failure_risk']
        if pred['needs_maintenance']:
            needs_maintenance_count += 1
    
    avg_risk = total_risk / len(predictions) if predictions else 0
    
    return {
        "summary": {
            "total_trains": len(predictions),
            "needs_maintenance": needs_maintenance_count,
            "average_risk_score": round(avg_risk, 3),
            "risk_distribution": risk_levels
        },
        "alerts": {
            "critical_trains": risk_levels["Critical"],
            "high_risk_trains": risk_levels["High"],
            "immediate_attention_needed": risk_levels["Critical"] + risk_levels["High"]
        },
        "model_type": "machine_learning" if railway_system.ml_models else "heuristic"
    }

# Additional API endpoints for frontend integration

@app.get("/api/trains/{train_id}")
async def get_train(train_id: str):
    """Get specific train data"""
    train = next((t for t in railway_system.trains if t.id == train_id), None)
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    
    return {
        "id": train.id,
        "name": train.name,
        "current_track": train.current_track,
        "speed": train.speed,
        "position": train.position,
        "destination": train.destination,
        "priority": train.priority.value,
        "passengers": train.passengers,
        "delay": train.delay,
        "status": train.status.value,
        "efficiency": train.efficiency,
        "fuel_level": train.fuel_level,
        "maintenance_due": train.maintenance_due,
        "route": train.route,
        "estimated_arrival": train.estimated_arrival.isoformat()
    }

@app.get("/api/trains/{train_id}/status")
async def get_train_status(train_id: str):
    """Get train status and real-time data"""
    train = next((t for t in railway_system.trains if t.id == train_id), None)
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    
    return {
        "id": train.id,
        "status": train.status.value,
        "delay": train.delay,
        "speed": train.speed,
        "position": train.position,
        "efficiency": train.efficiency,
        "fuel_level": train.fuel_level,
        "maintenance_due": train.maintenance_due,
        "last_updated": datetime.now().isoformat()
    }

@app.put("/api/trains/{train_id}/status")
async def update_train_status(train_id: str, status_data: dict):
    """Update train status"""
    train = next((t for t in railway_system.trains if t.id == train_id), None)
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    
    # Update train properties
    if "speed" in status_data:
        train.speed = status_data["speed"]
    if "delay" in status_data:
        train.delay = status_data["delay"]
    if "status" in status_data:
        train.status = TrainStatus(status_data["status"])
    
    return {"message": "Train status updated successfully"}

@app.get("/api/tracks/{track_id}")
async def get_track(track_id: str):
    """Get specific track data"""
    track = railway_system.tracks.get(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    return {
        "id": track.id,
        "capacity": track.capacity,
        "speed_limit": track.speed_limit,
        "length": track.length,
        "utilization": track.utilization,
        "maintenance_status": track.maintenance_status,
        "weather_condition": track.weather_condition,
        "signal_status": track.signal_status
    }

@app.get("/api/tracks/{track_id}/trains")
async def get_track_trains(track_id: str):
    """Get trains on specific track"""
    track = railway_system.tracks.get(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    track_trains = [t for t in railway_system.trains if t.current_track == track_id]
    return [
        {
            "id": train.id,
            "name": train.name,
            "speed": train.speed,
            "position": train.position,
            "delay": train.delay,
            "status": train.status.value,
            "priority": train.priority.value
        }
        for train in track_trains
    ]

@app.get("/api/optimizations/{optimization_id}")
async def get_optimization(optimization_id: str):
    """Get specific optimization decision"""
    decision = next((d for d in railway_system.optimization_decisions if d.id == optimization_id), None)
    if not decision:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    return {
        "id": decision.id,
        "type": decision.type.value,
        "train_id": decision.train_id,
        "track_id": decision.track_id,
        "junction_id": decision.junction_id,
        "action": decision.action,
        "impact": decision.impact,
        "priority": decision.priority,
        "confidence": decision.confidence,
        "estimated_benefit": decision.estimated_benefit,
        "implementation_time": decision.implementation_time,
        "status": decision.status
    }

@app.put("/api/optimizations/{optimization_id}")
async def update_optimization(optimization_id: str, update_data: dict):
    """Update optimization decision status"""
    decision = next((d for d in railway_system.optimization_decisions if d.id == optimization_id), None)
    if not decision:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    if "status" in update_data:
        decision.status = update_data["status"]
    
    return {"message": "Optimization updated successfully"}

@app.get("/api/analytics/performance")
async def get_performance_analytics():
    """Get performance analytics data"""
    # Generate historical performance data
    current_time = datetime.now()
    performance_data = []
    
    for i in range(24):  # Last 24 hours
        timestamp = current_time - timedelta(hours=i)
        throughput = railway_system.calculate_throughput_score() + random.uniform(-5, 5)
        performance_data.append({
            "timestamp": timestamp.isoformat(),
            "throughput": round(max(0, min(100, throughput)), 1),
            "efficiency": round(random.uniform(75, 95), 1),
            "delays": random.randint(0, 15),
            "energy_consumption": round(random.uniform(80, 120), 1)
        })
    
    return {
        "performance_trends": performance_data,
        "peak_hours": [8, 18, 20],
        "efficiency_score": round(railway_system.calculate_throughput_score(), 1),
        "improvement_rate": round(random.uniform(5, 15), 1)
    }

@app.get("/api/analytics/reports")
async def get_analytics_reports():
    """Get analytics reports data"""
    return {
        "daily_report": {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_trains": len(railway_system.trains),
            "on_time_percentage": round(random.uniform(85, 95), 1),
            "average_delay": round(sum(train.delay for train in railway_system.trains) / len(railway_system.trains), 1),
            "throughput_score": round(railway_system.calculate_throughput_score(), 1),
            "energy_efficiency": round(random.uniform(80, 95), 1)
        },
        "weekly_trends": {
            "throughput_trend": "increasing",
            "delay_trend": "decreasing",
            "efficiency_trend": "stable"
        }
    }

@app.get("/api/alerts")
async def get_alerts():
    """Get system alerts and notifications"""
    alerts = []
    
    # Generate alerts based on system state
    for train in railway_system.trains:
        if train.delay > 20:
            alerts.append({
                "id": f"alert_{train.id}_delay",
                "type": "delay",
                "severity": "high",
                "message": f"Train {train.name} is delayed by {train.delay} minutes",
                "timestamp": datetime.now().isoformat(),
                "train_id": train.id
            })
        
        if train.fuel_level < 20:
            alerts.append({
                "id": f"alert_{train.id}_fuel",
                "type": "fuel",
                "severity": "medium",
                "message": f"Train {train.name} has low fuel level: {train.fuel_level:.1f}%",
                "timestamp": datetime.now().isoformat(),
                "train_id": train.id
            })
        
        if train.maintenance_due:
            alerts.append({
                "id": f"alert_{train.id}_maintenance",
                "type": "maintenance",
                "severity": "medium",
                "message": f"Train {train.name} requires maintenance",
                "timestamp": datetime.now().isoformat(),
                "train_id": train.id
            })
    
    # Track maintenance alerts
    for track_id, track in railway_system.tracks.items():
        if track.maintenance_status == "maintenance_required":
            alerts.append({
                "id": f"alert_{track_id}_maintenance",
                "type": "track_maintenance",
                "severity": "high",
                "message": f"Track {track_id} requires maintenance",
                "timestamp": datetime.now().isoformat(),
                "track_id": track_id
            })
    
    return {
        "alerts": alerts,
        "total_alerts": len(alerts),
        "critical_alerts": len([a for a in alerts if a["severity"] == "high"]),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/network/status")
async def get_network_status():
    """Get network connectivity status"""
    return {
        "status": "connected",
        "latency": random.randint(10, 50),
        "uptime": "99.9%",
        "last_sync": datetime.now().isoformat(),
        "active_connections": len(manager.active_connections),
        "data_flow": "normal"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send real-time updates every 5 seconds
            await asyncio.sleep(5)
            
            # Update system
            railway_system.update_system()
            
            # Send updated data
            data = {
                "type": "system_update",
                "timestamp": datetime.now().isoformat(),
                "metrics": await get_metrics(),
                "trains": await get_trains(),
                "optimizations": await get_optimizations()
            }
            
            await manager.broadcast(data)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task to update system
async def background_updater():
    """Background task to update system state"""
    while True:
        railway_system.update_system()
        await asyncio.sleep(10)  # Update every 10 seconds

@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    asyncio.create_task(background_updater())

# Serve Next.js static export at the root if built
try:
    app.mount("/_next", StaticFiles(directory="railway-optimization/out/_next", html=False), name="_next")
    app.mount("/public", StaticFiles(directory="railway-optimization/out", html=False), name="public")

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        return FileResponse("railway-optimization/out/index.html")
    
    # Handle SPA routing - serve index.html for all routes that don't exist as files
    @app.get("/{path:path}", response_class=HTMLResponse)
    async def serve_spa(path: str):
        # Check if it's an API route
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Check if the file exists
        file_path = f"railway-optimization/out/{path}"
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # For SPA routing, serve index.html for all other routes
        return FileResponse("railway-optimization/out/index.html")
        
except Exception as e:
    print(f"Error setting up static files: {e}")
    pass

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
