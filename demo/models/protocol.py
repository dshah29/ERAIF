"""
ERAIF Protocol Models

This module contains protocol-related data models for the ERAIF system.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class MessageType(str, Enum):
    """Types of ERAIF protocol messages."""
    IMAGE_REQUEST = "image_request"
    IMAGE_RESPONSE = "image_response"
    STATUS_CHECK = "status_check"
    EMERGENCY_ALERT = "emergency_alert"
    HANDSHAKE = "handshake"
    STUDY_TRANSFER = "study_transfer"
    AI_ANALYSIS_REQUEST = "ai_analysis_request"
    AI_ANALYSIS_RESPONSE = "ai_analysis_response"


class Priority(str, Enum):
    """Message priority levels."""
    ROUTINE = "ROUTINE"
    URGENT = "URGENT"
    STAT = "STAT"
    CRITICAL = "CRITICAL"
    LIFE_THREATENING = "LIFE_THREATENING"


@dataclass
class ECPMessage:
    """ERAIF Core Protocol (ECP) message structure."""
    message_type: MessageType
    priority: Priority = Priority.ROUTINE
    message_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    source: Optional[Dict[str, str]] = None
    destination: Optional[Dict[str, str]] = None
    payload: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize default values if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now()
        if not self.message_id:
            self.message_id = f"msg_{int(self.timestamp.timestamp())}"
        if not self.source:
            self.source = {"facilityId": "unknown", "systemId": "unknown"}
        if not self.destination:
            self.destination = {"facilityId": "unknown", "systemId": "unknown"}
        if not self.payload:
            self.payload = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "messageId": self.message_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "messageType": self.message_type.value,
            "priority": self.priority.value,
            "source": self.source,
            "destination": self.destination,
            "payload": self.payload
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ECPMessage':
        """Create message from dictionary."""
        return cls(
            message_type=MessageType(data['messageType']),
            priority=Priority(data.get('priority', 'ROUTINE')),
            message_id=data.get('messageId'),
            timestamp=datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else None,
            source=data.get('source'),
            destination=data.get('destination'),
            payload=data.get('payload')
        )
