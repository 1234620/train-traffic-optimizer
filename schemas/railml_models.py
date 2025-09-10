"""
railML/RailDax Schema Models

This module implements railML and RailDax schemas for:
- Infrastructure data (tracks, signals, stations)
- Rolling stock data (trains, locomotives, coaches)
- Timetable data (schedules, routes, stops)
- Event data (movements, delays, disruptions)
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, time
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, Field, validator
import xml.etree.ElementTree as ET


class TrackType(Enum):
    """Types of railway tracks"""
    MAIN_LINE = "main_line"
    LOOP_LINE = "loop_line"
    SIDING = "siding"
    YARD = "yard"
    CROSSING = "crossing"


class SignalAspect(Enum):
    """Signal aspects for ATP/Kavach compliance"""
    RED = "red"  # Stop
    YELLOW = "yellow"  # Caution
    GREEN = "green"  # Proceed
    DOUBLE_YELLOW = "double_yellow"  # Caution - next signal at caution
    FLASHING_YELLOW = "flashing_yellow"  # Proceed with caution
    FLASHING_GREEN = "flashing_green"  # Proceed at line speed


class TrainType(Enum):
    """Types of trains"""
    PASSENGER = "passenger"
    EXPRESS = "express"
    SUPERFAST = "superfast"
    RAJDHANI = "rajdhani"
    SHATABDI = "shatabdi"
    FREIGHT = "freight"
    GOODS = "goods"
    MAIL = "mail"
    LOCAL = "local"


class InfrastructureElement(BaseModel):
    """Base class for railway infrastructure elements"""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Element name")
    coordinates: Optional[Dict[str, float]] = Field(None, description="GPS coordinates")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")


class TrackSection(InfrastructureElement):
    """Railway track section"""
    track_type: TrackType = Field(..., description="Type of track")
    length: float = Field(..., description="Length in meters")
    max_speed: float = Field(..., description="Maximum speed in km/h")
    gradient: float = Field(default=0.0, description="Gradient percentage")
    curvature: float = Field(default=0.0, description="Curvature radius in meters")
    electrified: bool = Field(default=True, description="Whether track is electrified")
    double_line: bool = Field(default=True, description="Whether it's a double line")
    atp_enabled: bool = Field(default=True, description="ATP/Kavach enabled")
    
    @validator('max_speed')
    def validate_max_speed(cls, v):
        if v <= 0 or v > 200:
            raise ValueError('Max speed must be between 0 and 200 km/h')
        return v


class Station(InfrastructureElement):
    """Railway station"""
    station_code: str = Field(..., description="Station code (e.g., NDLS)")
    zone: str = Field(..., description="Railway zone")
    division: str = Field(..., description="Railway division")
    platforms: List[int] = Field(..., description="Platform numbers")
    station_type: str = Field(default="junction", description="Station type")
    electrified: bool = Field(default=True, description="Whether station is electrified")
    atp_enabled: bool = Field(default=True, description="ATP/Kavach enabled")
    
    @validator('station_code')
    def validate_station_code(cls, v):
        if len(v) != 4 or not v.isupper():
            raise ValueError('Station code must be 4 uppercase letters')
        return v


class Signal(InfrastructureElement):
    """Railway signal"""
    signal_id: str = Field(..., description="Signal identifier")
    signal_type: str = Field(default="semaphore", description="Signal type")
    current_aspect: SignalAspect = Field(default=SignalAspect.RED, description="Current signal aspect")
    controlled_section: str = Field(..., description="Controlled track section")
    station_id: Optional[str] = Field(None, description="Associated station")
    atp_controlled: bool = Field(default=True, description="ATP/Kavach controlled")
    interlocked: bool = Field(default=True, description="Signal interlocked")
    
    def can_proceed(self) -> bool:
        """Check if train can proceed based on signal aspect"""
        return self.current_aspect in [SignalAspect.GREEN, SignalAspect.FLASHING_GREEN]
    
    def requires_caution(self) -> bool:
        """Check if train needs to proceed with caution"""
        return self.current_aspect in [
            SignalAspect.YELLOW, 
            SignalAspect.DOUBLE_YELLOW, 
            SignalAspect.FLASHING_YELLOW
        ]


class RollingStock(BaseModel):
    """Rolling stock information"""
    stock_id: str = Field(..., description="Unique rolling stock identifier")
    stock_type: str = Field(..., description="Type of rolling stock")
    train_type: TrainType = Field(..., description="Type of train")
    max_speed: float = Field(..., description="Maximum speed in km/h")
    length: float = Field(..., description="Length in meters")
    weight: float = Field(..., description="Weight in tons")
    capacity: int = Field(..., description="Passenger/freight capacity")
    atp_compatible: bool = Field(default=True, description="ATP/Kavach compatible")
    braking_distance: float = Field(..., description="Braking distance in meters")
    acceleration: float = Field(..., description="Acceleration in m/s²")
    
    @validator('max_speed')
    def validate_max_speed(cls, v):
        if v <= 0 or v > 200:
            raise ValueError('Max speed must be between 0 and 200 km/h')
        return v


class Train(InfrastructureElement):
    """Train information"""
    train_number: str = Field(..., description="Train number")
    train_name: str = Field(..., description="Train name")
    train_type: TrainType = Field(..., description="Type of train")
    rolling_stock: RollingStock = Field(..., description="Rolling stock details")
    priority: int = Field(default=5, description="Priority level (1=highest, 10=lowest)")
    zone: str = Field(..., description="Operating zone")
    division: str = Field(..., description="Operating division")
    atp_enabled: bool = Field(default=True, description="ATP/Kavach enabled")
    
    @validator('priority')
    def validate_priority(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Priority must be between 1 and 10')
        return v


class TimetableEntry(BaseModel):
    """Timetable entry for a station"""
    station_id: str = Field(..., description="Station identifier")
    station_code: str = Field(..., description="Station code")
    arrival_time: Optional[time] = Field(None, description="Scheduled arrival time")
    departure_time: Optional[time] = Field(None, description="Scheduled departure time")
    platform: Optional[int] = Field(None, description="Platform number")
    halt_duration: int = Field(default=0, description="Halt duration in minutes")
    distance: float = Field(..., description="Distance from origin in km")
    day_offset: int = Field(default=0, description="Day offset from start")
    
    @validator('halt_duration')
    def validate_halt_duration(cls, v):
        if v < 0:
            raise ValueError('Halt duration cannot be negative')
        return v


class Route(BaseModel):
    """Train route definition"""
    route_id: str = Field(..., description="Route identifier")
    route_name: str = Field(..., description="Route name")
    origin_station: str = Field(..., description="Origin station code")
    destination_station: str = Field(..., description="Destination station code")
    total_distance: float = Field(..., description="Total distance in km")
    timetable: List[TimetableEntry] = Field(..., description="Timetable entries")
    track_sections: List[str] = Field(..., description="Track section IDs")
    signals: List[str] = Field(..., description="Signal IDs along route")
    atp_route: bool = Field(default=True, description="ATP/Kavach route")
    
    def get_station_times(self, station_code: str) -> Optional[TimetableEntry]:
        """Get timetable entry for a specific station"""
        for entry in self.timetable:
            if entry.station_code == station_code:
                return entry
        return None


class MovementEvent(BaseModel):
    """Train movement event"""
    event_id: str = Field(..., description="Event identifier")
    train_id: str = Field(..., description="Train identifier")
    event_type: str = Field(..., description="Event type")
    station_id: str = Field(..., description="Station identifier")
    platform: Optional[int] = Field(None, description="Platform number")
    scheduled_time: datetime = Field(..., description="Scheduled time")
    actual_time: datetime = Field(..., description="Actual time")
    delay_minutes: int = Field(default=0, description="Delay in minutes")
    status: str = Field(..., description="Event status")
    additional_data: Dict[str, Any] = Field(default_factory=dict, description="Additional event data")
    
    @validator('delay_minutes')
    def validate_delay(cls, v):
        if v < -60 or v > 1440:  # -1 hour to +24 hours
            raise ValueError('Delay must be between -60 and 1440 minutes')
        return v


class InfrastructureModel(BaseModel):
    """Complete infrastructure model"""
    track_sections: List[TrackSection] = Field(..., description="Track sections")
    stations: List[Station] = Field(..., description="Stations")
    signals: List[Signal] = Field(..., description="Signals")
    routes: List[Route] = Field(..., description="Routes")
    trains: List[Train] = Field(..., description="Trains")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    def get_track_section(self, section_id: str) -> Optional[TrackSection]:
        """Get track section by ID"""
        for section in self.track_sections:
            if section.id == section_id:
                return section
        return None
    
    def get_station(self, station_id: str) -> Optional[Station]:
        """Get station by ID"""
        for station in self.stations:
            if station.id == station_id:
                return station
        return None
    
    def get_signal(self, signal_id: str) -> Optional[Signal]:
        """Get signal by ID"""
        for signal in self.signals:
            if signal.id == signal_id:
                return signal
        return None
    
    def get_route(self, route_id: str) -> Optional[Route]:
        """Get route by ID"""
        for route in self.routes:
            if route.id == route_id:
                return route
        return None
    
    def get_train(self, train_id: str) -> Optional[Train]:
        """Get train by ID"""
        for train in self.trains:
            if train.id == train_id:
                return train
        return None


class RailMLValidator:
    """Validator for railML/RailDax compliance"""
    
    @staticmethod
    def validate_infrastructure(infra: InfrastructureModel) -> List[str]:
        """Validate infrastructure model for railML compliance"""
        errors = []
        
        # Check for duplicate IDs
        all_ids = []
        for section in infra.track_sections:
            if section.id in all_ids:
                errors.append(f"Duplicate track section ID: {section.id}")
            all_ids.append(section.id)
        
        for station in infra.stations:
            if station.id in all_ids:
                errors.append(f"Duplicate station ID: {station.id}")
            all_ids.append(station.id)
        
        for signal in infra.signals:
            if signal.id in all_ids:
                errors.append(f"Duplicate signal ID: {signal.id}")
            all_ids.append(signal.id)
        
        # Check signal references
        for signal in infra.signals:
            if signal.controlled_section not in [s.id for s in infra.track_sections]:
                errors.append(f"Signal {signal.id} references non-existent track section: {signal.controlled_section}")
        
        # Check route references
        for route in infra.routes:
            for section_id in route.track_sections:
                if section_id not in [s.id for s in infra.track_sections]:
                    errors.append(f"Route {route.id} references non-existent track section: {section_id}")
        
        return errors
    
    @staticmethod
    def validate_timetable(route: Route) -> List[str]:
        """Validate timetable for consistency"""
        errors = []
        
        # Check for duplicate stations
        station_codes = [entry.station_code for entry in route.timetable]
        if len(station_codes) != len(set(station_codes)):
            errors.append(f"Duplicate stations in route {route.id}")
        
        # Check time progression
        for i in range(1, len(route.timetable)):
            prev_entry = route.timetable[i-1]
            curr_entry = route.timetable[i]
            
            if prev_entry.departure_time and curr_entry.arrival_time:
                if prev_entry.departure_time > curr_entry.arrival_time:
                    errors.append(f"Time progression error in route {route.id} at station {curr_entry.station_code}")
        
        return errors


def export_to_railml(infra: InfrastructureModel, filename: str) -> bool:
    """Export infrastructure model to railML XML format"""
    try:
        root = ET.Element("railml")
        root.set("version", "3.1")
        root.set("xmlns", "http://www.railml.org/schemas/2013")
        
        # Infrastructure section
        infrastructure = ET.SubElement(root, "infrastructure")
        
        # Track sections
        tracks = ET.SubElement(infrastructure, "tracks")
        for section in infra.track_sections:
            track = ET.SubElement(tracks, "track")
            track.set("id", section.id)
            track.set("name", section.name)
            track.set("type", section.track_type.value)
            
            # Track properties
            props = ET.SubElement(track, "properties")
            ET.SubElement(props, "length").text = str(section.length)
            ET.SubElement(props, "maxSpeed").text = str(section.max_speed)
            ET.SubElement(props, "gradient").text = str(section.gradient)
            ET.SubElement(props, "curvature").text = str(section.curvature)
            ET.SubElement(props, "electrified").text = str(section.electrified).lower()
            ET.SubElement(props, "doubleLine").text = str(section.double_line).lower()
            ET.SubElement(props, "atpEnabled").text = str(section.atp_enabled).lower()
        
        # Stations
        stations = ET.SubElement(infrastructure, "stations")
        for station in infra.stations:
            station_elem = ET.SubElement(stations, "station")
            station_elem.set("id", station.id)
            station_elem.set("name", station.name)
            station_elem.set("code", station.station_code)
            
            # Station properties
            props = ET.SubElement(station_elem, "properties")
            ET.SubElement(props, "zone").text = station.zone
            ET.SubElement(props, "division").text = station.division
            ET.SubElement(props, "stationType").text = station.station_type
            ET.SubElement(props, "electrified").text = str(station.electrified).lower()
            ET.SubElement(props, "atpEnabled").text = str(station.atp_enabled).lower()
            
            # Platforms
            platforms = ET.SubElement(station_elem, "platforms")
            for platform in station.platforms:
                ET.SubElement(platforms, "platform").text = str(platform)
        
        # Signals
        signals = ET.SubElement(infrastructure, "signals")
        for signal in infra.signals:
            signal_elem = ET.SubElement(signals, "signal")
            signal_elem.set("id", signal.id)
            signal_elem.set("name", signal.name)
            signal_elem.set("signalId", signal.signal_id)
            
            # Signal properties
            props = ET.SubElement(signal_elem, "properties")
            ET.SubElement(props, "signalType").text = signal.signal_type
            ET.SubElement(props, "currentAspect").text = signal.current_aspect.value
            ET.SubElement(props, "controlledSection").text = signal.controlled_section
            ET.SubElement(props, "atpControlled").text = str(signal.atp_controlled).lower()
            ET.SubElement(props, "interlocked").text = str(signal.interlocked).lower()
        
        # Write to file
        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
        
        return True
        
    except Exception as e:
        print(f"Error exporting to railML: {e}")
        return False


def import_from_railml(filename: str) -> Optional[InfrastructureModel]:
    """Import infrastructure model from railML XML format"""
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        
        # Parse infrastructure elements
        track_sections = []
        stations = []
        signals = []
        routes = []
        trains = []
        
        # Parse tracks
        for track in root.findall(".//track"):
            section = TrackSection(
                id=track.get("id"),
                name=track.get("name"),
                track_type=TrackType(track.get("type")),
                length=float(track.find("properties/length").text),
                max_speed=float(track.find("properties/maxSpeed").text),
                gradient=float(track.find("properties/gradient").text),
                curvature=float(track.find("properties/curvature").text),
                electrified=track.find("properties/electrified").text.lower() == "true",
                double_line=track.find("properties/doubleLine").text.lower() == "true",
                atp_enabled=track.find("properties/atpEnabled").text.lower() == "true"
            )
            track_sections.append(section)
        
        # Parse stations
        for station in root.findall(".//station"):
            platforms = [int(p.text) for p in station.findall("platforms/platform")]
            station_obj = Station(
                id=station.get("id"),
                name=station.get("name"),
                station_code=station.get("code"),
                zone=station.find("properties/zone").text,
                division=station.find("properties/division").text,
                platforms=platforms,
                station_type=station.find("properties/stationType").text,
                electrified=station.find("properties/electrified").text.lower() == "true",
                atp_enabled=station.find("properties/atpEnabled").text.lower() == "true"
            )
            stations.append(station_obj)
        
        # Parse signals
        for signal in root.findall(".//signal"):
            signal_obj = Signal(
                id=signal.get("id"),
                name=signal.get("name"),
                signal_id=signal.get("signalId"),
                signal_type=signal.find("properties/signalType").text,
                current_aspect=SignalAspect(signal.find("properties/currentAspect").text),
                controlled_section=signal.find("properties/controlledSection").text,
                atp_controlled=signal.find("properties/atpControlled").text.lower() == "true",
                interlocked=signal.find("properties/interlocked").text.lower() == "true"
            )
            signals.append(signal_obj)
        
        return InfrastructureModel(
            track_sections=track_sections,
            stations=stations,
            signals=signals,
            routes=routes,
            trains=trains
        )
        
    except Exception as e:
        print(f"Error importing from railML: {e}")
        return None
