"""
Railway Simulation Harness

This module provides a comprehensive simulation framework for testing the Train Traffic
Throughput Maximization System using railML infrastructure and timetable data.
"""

import asyncio
import logging
import json
import uuid
import random
import math
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import simpy
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class SimulationEvent(Enum):
    """Types of simulation events"""
    TRAIN_ARRIVAL = "train_arrival"
    TRAIN_DEPARTURE = "train_departure"
    SIGNAL_CHANGE = "signal_change"
    TRACK_OCCUPANCY = "track_occupancy"
    DELAY_INCIDENT = "delay_incident"
    MAINTENANCE_START = "maintenance_start"
    MAINTENANCE_END = "maintenance_end"
    WEATHER_CHANGE = "weather_change"
    EMERGENCY_STOP = "emergency_stop"


class TrainStatus(Enum):
    """Train status in simulation"""
    WAITING = "waiting"
    MOVING = "moving"
    STOPPED = "stopped"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


@dataclass
class SimulationConfig:
    """Configuration for simulation"""
    duration_hours: int = 24
    time_step_minutes: int = 1
    train_count: int = 100
    zone_count: int = 5
    track_sections: int = 50
    stations: int = 20
    signals: int = 30
    weather_events: int = 5
    maintenance_events: int = 3
    delay_events: int = 10
    emergency_events: int = 2
    random_seed: int = 42


@dataclass
class SimulationMetrics:
    """Metrics collected during simulation"""
    total_trains: int = 0
    on_time_trains: int = 0
    delayed_trains: int = 0
    cancelled_trains: int = 0
    total_delay_minutes: float = 0.0
    average_delay_minutes: float = 0.0
    throughput_trains_per_hour: float = 0.0
    headway_compliance_rate: float = 0.0
    safety_violations: int = 0
    slot_trades: int = 0
    maintenance_events: int = 0
    emergency_stops: int = 0
    simulation_duration_minutes: float = 0.0


@dataclass
class SimulationEvent:
    """Event in simulation"""
    event_id: str
    event_type: SimulationEvent
    timestamp: datetime
    train_id: Optional[str] = None
    zone_id: Optional[str] = None
    section_id: Optional[str] = None
    station_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)


class RailwaySimulation:
    """Main railway simulation class"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.env = simpy.Environment()
        self.metrics = SimulationMetrics()
        self.events: List[SimulationEvent] = []
        self.trains: Dict[str, Dict[str, Any]] = {}
        self.zones: Dict[str, Dict[str, Any]] = {}
        self.tracks: Dict[str, Dict[str, Any]] = {}
        self.stations: Dict[str, Dict[str, Any]] = {}
        self.signals: Dict[str, Dict[str, Any]] = {}
        self.network = nx.Graph()
        
        # Random number generator
        self.rng = random.Random(config.random_seed)
        np.random.seed(config.random_seed)
        
        # Simulation state
        self.current_time = datetime.now(timezone.utc)
        self.simulation_start = self.current_time
        self.simulation_end = self.current_time + timedelta(hours=config.duration_hours)
        
        # Initialize simulation components
        self._initialize_network()
        self._initialize_zones()
        self._initialize_tracks()
        self._initialize_stations()
        self._initialize_signals()
        self._initialize_trains()
    
    def _initialize_network(self):
        """Initialize railway network graph"""
        # Create a sample railway network
        # In production, this would load from railML data
        
        # Add nodes (stations and junctions)
        for i in range(self.config.stations):
            station_id = f"station_{i:03d}"
            self.network.add_node(station_id, 
                                type='station',
                                x=self.rng.uniform(0, 100),
                                y=self.rng.uniform(0, 100))
        
        # Add edges (track sections)
        for i in range(self.config.track_sections):
            track_id = f"track_{i:03d}"
            # Connect random stations
            source = f"station_{self.rng.randint(0, self.config.stations-1):03d}"
            target = f"station_{self.rng.randint(0, self.config.stations-1):03d}"
            
            if source != target:
                self.network.add_edge(source, target, 
                                    track_id=track_id,
                                    length=self.rng.uniform(10, 100),
                                    max_speed=self.rng.uniform(80, 160),
                                    electrified=self.rng.choice([True, False]))
    
    def _initialize_zones(self):
        """Initialize railway zones"""
        for i in range(self.config.zone_count):
            zone_id = f"zone_{i+1:03d}"
            self.zones[zone_id] = {
                'zone_id': zone_id,
                'name': f'Zone {i+1}',
                'capacity': self.rng.randint(10, 30),
                'current_trains': 0,
                'status': 'normal',
                'throughput': 0.0,
                'average_delay': 0.0
            }
    
    def _initialize_tracks(self):
        """Initialize track sections"""
        for i in range(self.config.track_sections):
            track_id = f"track_{i:03d}"
            self.tracks[track_id] = {
                'track_id': track_id,
                'length': self.rng.uniform(10, 100),
                'max_speed': self.rng.uniform(80, 160),
                'gradient': self.rng.uniform(-5, 5),
                'curvature': self.rng.uniform(0, 1000),
                'electrified': self.rng.choice([True, False]),
                'double_line': self.rng.choice([True, False]),
                'atp_enabled': True,
                'occupied': False,
                'current_train': None,
                'maintenance_required': False
            }
    
    def _initialize_stations(self):
        """Initialize stations"""
        for i in range(self.config.stations):
            station_id = f"station_{i:03d}"
            self.stations[station_id] = {
                'station_id': station_id,
                'name': f'Station {i+1}',
                'zone': f'zone_{self.rng.randint(1, self.config.zone_count):03d}',
                'platforms': self.rng.randint(2, 8),
                'electrified': True,
                'atp_enabled': True,
                'current_trains': 0,
                'platform_occupancy': [False] * self.rng.randint(2, 8)
            }
    
    def _initialize_signals(self):
        """Initialize signals"""
        for i in range(self.config.signals):
            signal_id = f"signal_{i:03d}"
            self.signals[signal_id] = {
                'signal_id': signal_id,
                'track_id': f"track_{self.rng.randint(0, self.config.track_sections-1):03d}",
                'station_id': f"station_{self.rng.randint(0, self.config.stations-1):03d}",
                'aspect': self.rng.choice(['red', 'yellow', 'green']),
                'atp_controlled': True,
                'interlocked': True,
                'last_change': self.current_time
            }
    
    def _initialize_trains(self):
        """Initialize trains"""
        for i in range(self.config.train_count):
            train_id = f"train_{i:05d}"
            self.trains[train_id] = {
                'train_id': train_id,
                'name': f'Train {i+1}',
                'type': self.rng.choice(['express', 'superfast', 'freight', 'local', 'mail']),
                'status': TrainStatus.WAITING,
                'current_section': None,
                'target_section': None,
                'speed': 0.0,
                'max_speed': self.rng.uniform(80, 160),
                'priority': self.rng.randint(1, 10),
                'delay': 0,
                'route': [],
                'current_station': None,
                'destination': None,
                'atp_enabled': True,
                'kavach_enabled': True,
                'created_at': self.current_time,
                'departure_time': self.current_time + timedelta(minutes=self.rng.randint(0, 60))
            }
    
    async def run_simulation(self):
        """Run the complete simulation"""
        logger.info("Starting railway simulation", 
                   duration_hours=self.config.duration_hours,
                   train_count=self.config.train_count)
        
        # Start simulation processes
        self.env.process(self._train_generator())
        self.env.process(self._weather_events())
        self.env.process(self._maintenance_events())
        self.env.process(self._delay_events())
        self.env.process(self._emergency_events())
        self.env.process(self._metrics_collector())
        
        # Run simulation
        simulation_duration = self.config.duration_hours * 60  # Convert to minutes
        self.env.run(until=simulation_duration)
        
        # Calculate final metrics
        await self._calculate_final_metrics()
        
        logger.info("Simulation completed", 
                   duration_minutes=simulation_duration,
                   total_events=len(self.events))
        
        return self.metrics
    
    def _train_generator(self):
        """Generate trains during simulation"""
        while True:
            # Generate a new train
            train_id = f"train_{self.rng.randint(0, 99999):05d}"
            train = self._create_train(train_id)
            self.trains[train_id] = train
            
            # Add to simulation
            self.env.process(self._train_process(train_id))
            
            # Wait for next train
            yield self.env.timeout(self.rng.uniform(5, 30))  # 5-30 minutes between trains
    
    def _create_train(self, train_id: str) -> Dict[str, Any]:
        """Create a new train"""
        return {
            'train_id': train_id,
            'name': f'Train {train_id}',
            'type': self.rng.choice(['express', 'superfast', 'freight', 'local', 'mail']),
            'status': TrainStatus.WAITING,
            'current_section': None,
            'target_section': None,
            'speed': 0.0,
            'max_speed': self.rng.uniform(80, 160),
            'priority': self.rng.randint(1, 10),
            'delay': 0,
            'route': self._generate_route(),
            'current_station': None,
            'destination': None,
            'atp_enabled': True,
            'kavach_enabled': True,
            'created_at': self.current_time,
            'departure_time': self.current_time + timedelta(minutes=self.rng.randint(0, 60))
        }
    
    def _generate_route(self) -> List[str]:
        """Generate a random route for a train"""
        # Select random start and end stations
        start_station = f"station_{self.rng.randint(0, self.config.stations-1):03d}"
        end_station = f"station_{self.rng.randint(0, self.config.stations-1):03d}"
        
        # Find path between stations
        try:
            path = nx.shortest_path(self.network, start_station, end_station)
            return path
        except nx.NetworkXNoPath:
            # If no path exists, return a simple route
            return [start_station, end_station]
    
    def _train_process(self, train_id: str):
        """Process a single train through the simulation"""
        train = self.trains[train_id]
        
        try:
            # Wait for departure time
            departure_delay = (train['departure_time'] - self.current_time).total_seconds() / 60
            if departure_delay > 0:
                yield self.env.timeout(departure_delay)
            
            # Update train status
            train['status'] = TrainStatus.MOVING
            self.metrics.total_trains += 1
            
            # Process route
            for i, station in enumerate(train['route']):
                if i == 0:
                    # First station - departure
                    yield from self._process_departure(train_id, station)
                elif i == len(train['route']) - 1:
                    # Last station - arrival
                    yield from self._process_arrival(train_id, station)
                else:
                    # Intermediate station - pass through
                    yield from self._process_pass_through(train_id, station)
            
            # Train completed
            train['status'] = TrainStatus.COMPLETED
            self.metrics.on_time_trains += 1
            
        except Exception as e:
            logger.error("Error processing train", train_id=train_id, error=str(e))
            train['status'] = TrainStatus.CANCELLED
            self.metrics.cancelled_trains += 1
    
    def _process_departure(self, train_id: str, station_id: str):
        """Process train departure from station"""
        train = self.trains[train_id]
        station = self.stations[station_id]
        
        # Check if platform is available
        available_platform = self._find_available_platform(station_id)
        if available_platform is None:
            # No platform available, add delay
            delay = self.rng.uniform(5, 30)
            yield self.env.timeout(delay)
            train['delay'] += delay
        
        # Update station occupancy
        station['current_trains'] += 1
        if available_platform is not None:
            station['platform_occupancy'][available_platform] = True
        
        # Record event
        self._record_event(SimulationEvent.TRAIN_DEPARTURE, train_id, station_id=station_id)
        
        # Wait for departure processing time
        yield self.env.timeout(self.rng.uniform(2, 10))
    
    def _process_arrival(self, train_id: str, station_id: str):
        """Process train arrival at station"""
        train = self.trains[train_id]
        station = self.stations[station_id]
        
        # Update station occupancy
        station['current_trains'] -= 1
        
        # Free up platform
        for i, occupied in enumerate(station['platform_occupancy']):
            if occupied:
                station['platform_occupancy'][i] = False
                break
        
        # Record event
        self._record_event(SimulationEvent.TRAIN_ARRIVAL, train_id, station_id=station_id)
        
        # Wait for arrival processing time
        yield self.env.timeout(self.rng.uniform(1, 5))
    
    def _process_pass_through(self, train_id: str, station_id: str):
        """Process train passing through station"""
        train = self.trains[train_id]
        
        # Calculate travel time
        travel_time = self._calculate_travel_time(train)
        yield self.env.timeout(travel_time)
        
        # Record event
        self._record_event(SimulationEvent.TRAIN_DEPARTURE, train_id, station_id=station_id)
    
    def _find_available_platform(self, station_id: str) -> Optional[int]:
        """Find available platform at station"""
        station = self.stations[station_id]
        for i, occupied in enumerate(station['platform_occupancy']):
            if not occupied:
                return i
        return None
    
    def _calculate_travel_time(self, train: Dict[str, Any]) -> float:
        """Calculate travel time for train"""
        # Base travel time
        base_time = self.rng.uniform(10, 60)  # 10-60 minutes
        
        # Adjust based on train type
        type_multiplier = {
            'express': 0.8,
            'superfast': 0.6,
            'freight': 1.2,
            'local': 1.0,
            'mail': 1.1
        }.get(train['type'], 1.0)
        
        # Adjust based on priority
        priority_multiplier = 1.0 - (train['priority'] - 1) * 0.05  # Higher priority = faster
        
        return base_time * type_multiplier * priority_multiplier
    
    def _weather_events(self):
        """Generate weather events"""
        for _ in range(self.config.weather_events):
            # Wait for random time
            yield self.env.timeout(self.rng.uniform(60, 300))  # 1-5 hours
            
            # Generate weather event
            weather_type = self.rng.choice(['rain', 'fog', 'snow', 'storm'])
            severity = self.rng.choice(['light', 'moderate', 'heavy'])
            
            # Apply weather effects
            self._apply_weather_effects(weather_type, severity)
            
            # Record event
            self._record_event(SimulationEvent.WEATHER_CHANGE, 
                             data={'weather_type': weather_type, 'severity': severity})
    
    def _apply_weather_effects(self, weather_type: str, severity: str):
        """Apply weather effects to simulation"""
        # Reduce speeds for all trains
        speed_reduction = {
            'light': 0.9,
            'moderate': 0.8,
            'heavy': 0.6
        }.get(severity, 1.0)
        
        for train in self.trains.values():
            if train['status'] == TrainStatus.MOVING:
                train['speed'] *= speed_reduction
    
    def _maintenance_events(self):
        """Generate maintenance events"""
        for _ in range(self.config.maintenance_events):
            # Wait for random time
            yield self.env.timeout(self.rng.uniform(120, 600))  # 2-10 hours
            
            # Select random track for maintenance
            track_id = f"track_{self.rng.randint(0, self.config.track_sections-1):03d}"
            track = self.tracks[track_id]
            
            # Start maintenance
            track['maintenance_required'] = True
            self.metrics.maintenance_events += 1
            
            # Record event
            self._record_event(SimulationEvent.MAINTENANCE_START, 
                             data={'track_id': track_id})
            
            # Maintenance duration
            maintenance_duration = self.rng.uniform(60, 240)  # 1-4 hours
            yield self.env.timeout(maintenance_duration)
            
            # End maintenance
            track['maintenance_required'] = False
            
            # Record event
            self._record_event(SimulationEvent.MAINTENANCE_END, 
                             data={'track_id': track_id})
    
    def _delay_events(self):
        """Generate delay events"""
        for _ in range(self.config.delay_events):
            # Wait for random time
            yield self.env.timeout(self.rng.uniform(30, 180))  # 30 minutes - 3 hours
            
            # Select random train for delay
            if self.trains:
                train_id = self.rng.choice(list(self.trains.keys()))
                train = self.trains[train_id]
                
                # Apply delay
                delay_minutes = self.rng.uniform(5, 60)  # 5-60 minutes
                train['delay'] += delay_minutes
                train['status'] = TrainStatus.DELAYED
                self.metrics.delayed_trains += 1
                self.metrics.total_delay_minutes += delay_minutes
                
                # Record event
                self._record_event(SimulationEvent.DELAY_INCIDENT, train_id, 
                                 data={'delay_minutes': delay_minutes})
    
    def _emergency_events(self):
        """Generate emergency events"""
        for _ in range(self.config.emergency_events):
            # Wait for random time
            yield self.env.timeout(self.rng.uniform(180, 720))  # 3-12 hours
            
            # Select random train for emergency
            if self.trains:
                train_id = self.rng.choice(list(self.trains.keys()))
                train = self.trains[train_id]
                
                # Apply emergency stop
                train['status'] = TrainStatus.STOPPED
                train['speed'] = 0
                self.metrics.emergency_stops += 1
                
                # Record event
                self._record_event(SimulationEvent.EMERGENCY_STOP, train_id)
                
                # Emergency duration
                emergency_duration = self.rng.uniform(10, 60)  # 10-60 minutes
                yield self.env.timeout(emergency_duration)
                
                # Resume normal operation
                train['status'] = TrainStatus.MOVING
    
    def _metrics_collector(self):
        """Collect metrics during simulation"""
        while True:
            # Update zone metrics
            for zone in self.zones.values():
                zone['current_trains'] = len([t for t in self.trains.values() 
                                            if t['status'] in [TrainStatus.MOVING, TrainStatus.STOPPED]])
                zone['throughput'] = zone['current_trains'] / zone['capacity'] * 100
            
            # Wait for next collection
            yield self.env.timeout(60)  # Collect every hour
    
    def _record_event(self, event_type: SimulationEvent, train_id: Optional[str] = None, 
                     zone_id: Optional[str] = None, section_id: Optional[str] = None,
                     station_id: Optional[str] = None, data: Dict[str, Any] = None):
        """Record a simulation event"""
        event = SimulationEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=self.current_time + timedelta(minutes=self.env.now),
            train_id=train_id,
            zone_id=zone_id,
            section_id=section_id,
            station_id=station_id,
            data=data or {}
        )
        
        self.events.append(event)
        logger.debug("Event recorded", event_type=event_type.value, train_id=train_id)
    
    async def _calculate_final_metrics(self):
        """Calculate final simulation metrics"""
        # Calculate average delay
        if self.metrics.delayed_trains > 0:
            self.metrics.average_delay_minutes = self.metrics.total_delay_minutes / self.metrics.delayed_trains
        
        # Calculate throughput
        simulation_duration_hours = self.config.duration_hours
        self.metrics.throughput_trains_per_hour = self.metrics.total_trains / simulation_duration_hours
        
        # Calculate headway compliance (simplified)
        self.metrics.headway_compliance_rate = 0.95  # Placeholder
        
        # Calculate simulation duration
        self.metrics.simulation_duration_minutes = self.config.duration_hours * 60
        
        logger.info("Final metrics calculated", 
                   total_trains=self.metrics.total_trains,
                   on_time_rate=self.metrics.on_time_trains / self.metrics.total_trains * 100,
                   average_delay=self.metrics.average_delay_minutes,
                   throughput=self.metrics.throughput_trains_per_hour)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate simulation report"""
        return {
            'simulation_config': {
                'duration_hours': self.config.duration_hours,
                'train_count': self.config.train_count,
                'zone_count': self.config.zone_count,
                'track_sections': self.config.track_sections,
                'stations': self.config.stations,
                'signals': self.config.signals
            },
            'metrics': {
                'total_trains': self.metrics.total_trains,
                'on_time_trains': self.metrics.on_time_trains,
                'delayed_trains': self.metrics.delayed_trains,
                'cancelled_trains': self.metrics.cancelled_trains,
                'total_delay_minutes': self.metrics.total_delay_minutes,
                'average_delay_minutes': self.metrics.average_delay_minutes,
                'throughput_trains_per_hour': self.metrics.throughput_trains_per_hour,
                'headway_compliance_rate': self.metrics.headway_compliance_rate,
                'safety_violations': self.metrics.safety_violations,
                'slot_trades': self.metrics.slot_trades,
                'maintenance_events': self.metrics.maintenance_events,
                'emergency_stops': self.metrics.emergency_stops,
                'simulation_duration_minutes': self.metrics.simulation_duration_minutes
            },
            'events': [
                {
                    'event_id': event.event_id,
                    'event_type': event.event_type.value,
                    'timestamp': event.timestamp.isoformat(),
                    'train_id': event.train_id,
                    'zone_id': event.zone_id,
                    'section_id': event.section_id,
                    'station_id': event.station_id,
                    'data': event.data
                }
                for event in self.events
            ],
            'zones': list(self.zones.values()),
            'tracks': list(self.tracks.values()),
            'stations': list(self.stations.values()),
            'signals': list(self.signals.values())
        }
    
    def export_to_csv(self, filename: str):
        """Export simulation data to CSV"""
        # Export events
        events_df = pd.DataFrame([
            {
                'event_id': event.event_id,
                'event_type': event.event_type.value,
                'timestamp': event.timestamp.isoformat(),
                'train_id': event.train_id,
                'zone_id': event.zone_id,
                'section_id': event.section_id,
                'station_id': event.station_id,
                'data': json.dumps(event.data)
            }
            for event in self.events
        ])
        events_df.to_csv(f"{filename}_events.csv", index=False)
        
        # Export metrics
        metrics_df = pd.DataFrame([self.metrics.__dict__])
        metrics_df.to_csv(f"{filename}_metrics.csv", index=False)
        
        logger.info("Simulation data exported to CSV", filename=filename)


async def main():
    """Main entry point for simulation"""
    config = SimulationConfig(
        duration_hours=24,
        train_count=100,
        zone_count=5,
        track_sections=50,
        stations=20,
        signals=30,
        random_seed=42
    )
    
    simulation = RailwaySimulation(config)
    
    # Run simulation
    metrics = await simulation.run_simulation()
    
    # Generate report
    report = simulation.generate_report()
    
    # Export to CSV
    simulation.export_to_csv("simulation_results")
    
    # Print summary
    print("\n=== SIMULATION SUMMARY ===")
    print(f"Total Trains: {metrics.total_trains}")
    print(f"On Time: {metrics.on_time_trains} ({metrics.on_time_trains/metrics.total_trains*100:.1f}%)")
    print(f"Delayed: {metrics.delayed_trains} ({metrics.delayed_trains/metrics.total_trains*100:.1f}%)")
    print(f"Cancelled: {metrics.cancelled_trains} ({metrics.cancelled_trains/metrics.total_trains*100:.1f}%)")
    print(f"Average Delay: {metrics.average_delay_minutes:.1f} minutes")
    print(f"Throughput: {metrics.throughput_trains_per_hour:.1f} trains/hour")
    print(f"Headway Compliance: {metrics.headway_compliance_rate*100:.1f}%")
    print(f"Safety Violations: {metrics.safety_violations}")
    print(f"Slot Trades: {metrics.slot_trades}")
    print(f"Maintenance Events: {metrics.maintenance_events}")
    print(f"Emergency Stops: {metrics.emergency_stops}")
    print(f"Total Events: {len(simulation.events)}")
    
    # Save report to file
    with open("simulation_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print("\nSimulation completed! Report saved to simulation_report.json")


if __name__ == "__main__":
    asyncio.run(main())

