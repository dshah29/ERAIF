"""
ERAIF Emergency Data Models

This module contains data models for emergency modes, status tracking,
and emergency event management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class EmergencyMode(str, Enum):
    """Operating modes for ERAIF system during emergencies."""
    NORMAL = "normal"
    DEGRADED = "degraded"
    DISASTER = "disaster"
    MASS_CASUALTY = "mass_casualty"
    ISOLATION = "isolation"
    RECOVERY = "recovery"


class EmergencySeverity(str, Enum):
    """Emergency severity levels."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CATASTROPHIC = "catastrophic"


class EmergencyType(str, Enum):
    """Types of emergency events."""
    NATURAL_DISASTER = "natural_disaster"
    MAN_MADE_DISASTER = "man_made_disaster"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    MASS_CASUALTY_INCIDENT = "mass_casualty_incident"
    PANDEMIC = "pandemic"
    TERRORISM = "terrorism"
    CIVIL_UNREST = "civil_unrest"
    TECHNOLOGICAL_FAILURE = "technological_failure"
    OTHER = "other"


class EmergencyStatus(str, Enum):
    """Status of emergency events."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    MONITORING = "monitoring"
    ESCALATING = "escalating"
    DECLINING = "declining"
    STABLE = "stable"


class CommunicationStatus(str, Enum):
    """Communication system status."""
    FULL = "full"
    PARTIAL = "partial"
    LIMITED = "limited"
    FAILED = "failed"
    RESTORING = "restoring"


@dataclass
class EmergencyContact:
    """Emergency contact information for coordination."""
    name: str
    role: str
    organization: str
    phone: str
    email: Optional[str] = None
    backup_phone: Optional[str] = None
    is_primary: bool = False
    can_escalate: bool = False
    response_time_minutes: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "role": self.role,
            "organization": self.organization,
            "phone": self.phone,
            "email": self.email,
            "backup_phone": self.backup_phone,
            "is_primary": self.is_primary,
            "can_escalate": self.can_escalate,
            "response_time_minutes": self.response_time_minutes
        }


@dataclass
class ResourceStatus:
    """Status of critical resources during emergency."""
    resource_type: str  # e.g., "power", "network", "storage", "bandwidth"
    current_status: str  # e.g., "operational", "degraded", "failed"
    capacity_percent: float  # 0.0 to 100.0
    estimated_recovery_time: Optional[int] = None  # minutes
    backup_available: bool = False
    last_updated: Optional[datetime] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if not self.last_updated:
            self.last_updated = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "resource_type": self.resource_type,
            "current_status": self.current_status,
            "capacity_percent": self.capacity_percent,
            "estimated_recovery_time": self.estimated_recovery_time,
            "backup_available": self.backup_available,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "notes": self.notes
        }


@dataclass
class EmergencyEvent:
    """Complete emergency event information."""
    event_type: EmergencyType
    severity: EmergencySeverity
    title: str
    description: str
    location: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: EmergencyStatus = EmergencyStatus.ACTIVE
    affected_facilities: List[str] = field(default_factory=list)
    affected_population: Optional[int] = None
    declared_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    estimated_duration: Optional[int] = None  # hours
    emergency_contacts: List[EmergencyContact] = field(default_factory=list)
    resource_status: List[ResourceStatus] = field(default_factory=list)
    protocols_activated: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if not self.declared_at:
            self.declared_at = datetime.now()
    
    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate duration in minutes if resolved."""
        if self.resolved_at and self.declared_at:
            return int((self.resolved_at - self.declared_at).total_seconds() / 60)
        return None
    
    @property
    def is_active(self) -> bool:
        """Check if emergency is currently active."""
        return self.status in [EmergencyStatus.ACTIVE, EmergencyStatus.ESCALATING]
    
    @property
    def is_resolved(self) -> bool:
        """Check if emergency is resolved."""
        return self.status == EmergencyStatus.RESOLVED
    
    def add_emergency_contact(self, contact: EmergencyContact):
        """Add an emergency contact."""
        self.emergency_contacts.append(contact)
    
    def add_resource_status(self, status: ResourceStatus):
        """Add or update resource status."""
        # Remove existing status for this resource type
        self.resource_status = [s for s in self.resource_status if s.resource_type != status.resource_type]
        self.resource_status.append(status)
    
    def activate_protocol(self, protocol_name: str):
        """Activate an emergency protocol."""
        if protocol_name not in self.protocols_activated:
            self.protocols_activated.append(protocol_name)
    
    def deactivate_protocol(self, protocol_name: str):
        """Deactivate an emergency protocol."""
        if protocol_name in self.protocols_activated:
            self.protocols_activated.remove(protocol_name)
    
    def add_note(self, note: str):
        """Add a note to the emergency event."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.notes.append(f"[{timestamp}] {note}")
    
    def update_status(self, new_status: EmergencyStatus):
        """Update emergency status."""
        old_status = self.status
        self.status = new_status
        
        if new_status == EmergencyStatus.RESOLVED and not self.resolved_at:
            self.resolved_at = datetime.now()
        
        self.add_note(f"Status changed from {old_status} to {new_status}")
    
    def escalate(self):
        """Escalate emergency severity."""
        severity_levels = list(EmergencySeverity)
        current_index = severity_levels.index(self.severity)
        
        if current_index < len(severity_levels) - 1:
            new_severity = severity_levels[current_index + 1]
            self.severity = new_severity
            self.add_note(f"Emergency escalated to {new_severity}")
            
            if new_severity in [EmergencySeverity.MAJOR, EmergencySeverity.CATASTROPHIC]:
                self.status = EmergencyStatus.ESCALATING
    
    def resolve(self, resolution_notes: str = ""):
        """Mark emergency as resolved."""
        self.status = EmergencyStatus.RESOLVED
        self.resolved_at = datetime.now()
        if resolution_notes:
            self.add_note(f"Resolution: {resolution_notes}")
    
    def get_resource_status(self, resource_type: str) -> Optional[ResourceStatus]:
        """Get status of a specific resource."""
        for status in self.resource_status:
            if status.resource_type == resource_type:
                return status
        return None
    
    def get_primary_contacts(self) -> List[EmergencyContact]:
        """Get primary emergency contacts."""
        return [c for c in self.emergency_contacts if c.is_primary]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "affected_facilities": self.affected_facilities,
            "affected_population": self.affected_population,
            "declared_at": self.declared_at.isoformat() if self.declared_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "estimated_duration": self.estimated_duration,
            "emergency_contacts": [c.to_dict() for c in self.emergency_contacts],
            "resource_status": [s.to_dict() for s in self.resource_status],
            "protocols_activated": self.protocols_activated,
            "notes": self.notes,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EmergencyEvent':
        """Create EmergencyEvent instance from dictionary."""
        # Parse emergency contacts
        emergency_contacts = []
        for contact_data in data.get('emergency_contacts', []):
            contact = EmergencyContact(
                name=contact_data['name'],
                role=contact_data['role'],
                organization=contact_data['organization'],
                phone=contact_data['phone'],
                email=contact_data.get('email'),
                backup_phone=contact_data.get('backup_phone'),
                is_primary=contact_data.get('is_primary', False),
                can_escalate=contact_data.get('can_escalate', False),
                response_time_minutes=contact_data.get('response_time_minutes')
            )
            emergency_contacts.append(contact)
        
        # Parse resource status
        resource_status = []
        for status_data in data.get('resource_status', []):
            status = ResourceStatus(
                resource_type=status_data['resource_type'],
                current_status=status_data['current_status'],
                capacity_percent=status_data['capacity_percent'],
                estimated_recovery_time=status_data.get('estimated_recovery_time'),
                backup_available=status_data.get('backup_available', False),
                last_updated=datetime.fromisoformat(status_data['last_updated']) if status_data.get('last_updated') else None,
                notes=status_data.get('notes')
            )
            resource_status.append(status)
        
        return cls(
            event_id=data.get('event_id'),
            event_type=EmergencyType(data['event_type']),
            severity=EmergencySeverity(data['severity']),
            status=EmergencyStatus(data.get('status', 'ACTIVE')),
            title=data['title'],
            description=data['description'],
            location=data['location'],
            affected_facilities=data.get('affected_facilities', []),
            affected_population=data.get('affected_population'),
            declared_at=datetime.fromisoformat(data['declared_at']) if data.get('declared_at') else None,
            resolved_at=datetime.fromisoformat(data['resolved_at']) if data.get('resolved_at') else None,
            estimated_duration=data.get('estimated_duration'),
            emergency_contacts=emergency_contacts,
            resource_status=resource_status,
            protocols_activated=data.get('protocols_activated', []),
            notes=data.get('notes', []),
            metadata=data.get('metadata', {})
        )


@dataclass
class EmergencyModeConfig:
    """Configuration for different emergency modes."""
    mode: EmergencyMode
    description: str
    communication_level: CommunicationStatus
    authentication_required: bool = True
    audit_logging: bool = True
    data_compression: bool = False
    backup_systems_active: bool = False
    priority_threshold: str = "ROUTINE"  # Minimum priority to process
    max_concurrent_connections: Optional[int] = None
    timeout_seconds: int = 30
    retry_attempts: int = 3
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "mode": self.mode.value,
            "description": self.description,
            "communication_level": self.communication_level.value,
            "authentication_required": self.authentication_required,
            "audit_logging": self.audit_logging,
            "data_compression": self.data_compression,
            "backup_systems_active": self.backup_systems_active,
            "priority_threshold": self.priority_threshold,
            "max_concurrent_connections": self.max_concurrent_connections,
            "timeout_seconds": self.timeout_seconds,
            "retry_attempts": self.retry_attempts
        }
