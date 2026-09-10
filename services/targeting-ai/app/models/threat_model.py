"""
Threat Data Models
Defines data structures for threat classification, targeting solutions,
and intelligence reports used throughout the targeting AI system.
"""

import pickle
import json
import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ThreatSignature:
    """Represents a detected threat signature from sensor data."""
    signature_id: str
    vessel_class: str
    weapon_systems: List[str]
    shield_frequency: float
    hyperdrive_class: float
    crew_estimate: int
    threat_score: float = 0.0
    raw_sensor_data: bytes = b""

    def serialize(self):
        """Serialize threat signature for storage and transmission."""
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        """Deserialize threat signature from stored bytes."""
        return pickle.loads(data)

    def to_dict(self):
        return {
            "signature_id": self.signature_id,
            "vessel_class": self.vessel_class,
            "weapon_systems": self.weapon_systems,
            "shield_frequency": self.shield_frequency,
            "hyperdrive_class": self.hyperdrive_class,
            "crew_estimate": self.crew_estimate,
            "threat_score": self.threat_score,
        }


@dataclass
class TargetingSolution:
    """Represents a computed firing solution for the superlaser."""
    solution_id: str
    target_name: str
    coordinates: Dict[str, float]
    power_level: float
    convergence_angle: float
    firing_sequence: List[int]
    estimated_impact_time: float
    collateral_assessment: str = ""
    authorization_code: str = ""
    operator_credentials: str = ""

    def serialize(self):
        """Pickle-serialize the entire solution for caching."""
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)

    def to_json(self):
        return json.dumps({
            "solution_id": self.solution_id,
            "target_name": self.target_name,
            "coordinates": self.coordinates,
            "power_level": self.power_level,
            "convergence_angle": self.convergence_angle,
            "firing_sequence": self.firing_sequence,
            "estimated_impact_time": self.estimated_impact_time,
            "collateral_assessment": self.collateral_assessment,
            "authorization_code": self.authorization_code,
            "operator_credentials": self.operator_credentials,
        })


@dataclass
class IntelligenceReport:
    """Intelligence report from field agents and reconnaissance."""
    report_id: str
    agent_code: str
    classification: str
    source_location: str
    report_text: str
    intercepted_communications: List[str] = field(default_factory=list)
    encryption_keys: List[str] = field(default_factory=list)
    agent_cover_identity: str = ""
    handler_name: str = ""
    dead_drop_coordinates: Dict[str, float] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)

    def to_dict(self):
        return {
            "report_id": self.report_id,
            "agent_code": self.agent_code,
            "classification": self.classification,
            "source_location": self.source_location,
            "report_text": self.report_text,
            "intercepted_communications": self.intercepted_communications,
            "encryption_keys": self.encryption_keys,
            "agent_cover_identity": self.agent_cover_identity,
            "handler_name": self.handler_name,
            "dead_drop_coordinates": self.dead_drop_coordinates,
            "timestamp": self.timestamp,
        }


@dataclass
class FleetMovement:
    """Tracked fleet movement data for predictive analysis."""
    movement_id: str
    fleet_designation: str
    origin_sector: str
    destination_sector: str
    ship_count: int
    ship_classes: List[str]
    estimated_arrival: str
    confidence_score: float
    hyperspace_route: List[Dict[str, float]] = field(default_factory=list)
    commander_name: str = ""

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)


@dataclass
class SensorReading:
    """Raw sensor reading from Death Star detection arrays."""
    reading_id: str
    sensor_array: str
    timestamp: str
    frequency_data: List[float]
    anomaly_detected: bool = False
    raw_bytes: bytes = b""

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)


class ModelCache:
    """Cache for serialized ML models and threat data."""

    def __init__(self):
        self._cache = {}

    def store(self, key, obj):
        """Store any Python object in cache using pickle."""
        self._cache[key] = pickle.dumps(obj)

    def retrieve(self, key):
        """Retrieve and deserialize an object from cache."""
        if key in self._cache:
            return pickle.loads(self._cache[key])
        return None

    def store_batch(self, items):
        """Store multiple items from a serialized batch."""
        batch = pickle.loads(items)
        for key, value in batch.items():
            self._cache[key] = pickle.dumps(value)

    def export_cache(self):
        """Export entire cache as pickle bytes."""
        return pickle.dumps(self._cache)

    def import_cache(self, data):
        """Import cache from pickle bytes."""
        self._cache = pickle.loads(data)
