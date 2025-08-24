#!/usr/bin/env python3
"""
ERAIF Core Implementation
Emergency Radiology AI Interoperability Framework
Version: 0.1.0
License: MIT
"""

import json
import hashlib
import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmergencyMode(Enum):
    """Operating modes for ERAIF system."""
    NORMAL = "normal"
    DEGRADED = "degraded"
    DISASTER = "disaster"
    MASS_CASUALTY = "mass_casualty"
    ISOLATION = "isolation"


class Priority(Enum):
    """Message priority levels."""
    ROUTINE = 0
    URGENT = 1
    STAT = 2
    CRITICAL = 3
    LIFE_THREATENING = 4


class MessageType(Enum):
    """Types of ERAIF messages."""
    IMAGE_REQUEST = "image_request"
    IMAGE_RESPONSE = "image_response"
    STATUS_CHECK = "status_check"
    EMERGENCY_ALERT = "emergency_alert"
    HANDSHAKE = "handshake"


@dataclass
class ERAIFMessage:
    """Core ERAIF message structure."""
    version: str = "1.0"
    timestamp: str = ""
    priority: Priority = Priority.ROUTINE
    mode: EmergencyMode = EmergencyMode.NORMAL
    message_type: MessageType = MessageType.IMAGE_REQUEST
    payload: Dict[str, Any] = None
    routing: Dict[str, Any] = None
    signature: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"
        if self.payload is None:
            self.payload = {}
        if self.routing is None:
            self.routing = {}
        if not self.signature:
            self.signature = self.generate_signature()
    
    def generate_signature(self) -> str:
        """Generate message signature for verification."""
        content = f"{self.timestamp}{self.priority.value}{self.message_type.value}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_json(self) -> str:
        """Convert message to JSON format."""
        data = {
            "version": self.version,
            "timestamp": self.timestamp,
            "priority": self.priority.name,
            "mode": self.mode.name,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "routing": self.routing,
            "signature": self.signature
        }
        return json.dumps(data, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ERAIFMessage':
        """Create message from JSON string."""
        data = json.loads(json_str)
        return cls(
            version=data.get("version", "1.0"),
            timestamp=data.get("timestamp"),
            priority=Priority[data.get("priority", "ROUTINE")],
            mode=EmergencyMode[data.get("mode", "NORMAL")],
            message_type=MessageType(data.get("message_type", "image_request")),
            payload=data.get("payload", {}),
            routing=data.get("routing", {}),
            signature=data.get("signature", "")
        )


class ERAIFNode:
    """Represents a node in the ERAIF network."""
    
    def __init__(self, node_id: str, hospital_name: str):
        self.node_id = node_id
        self.hospital_name = hospital_name
        self.mode = EmergencyMode.NORMAL
        self.connected_nodes: List[str] = []
        self.message_queue: List[ERAIFMessage] = []
        self.cached_data: Dict[str, Any] = {}
        
        logger.info(f"ERAIF Node initialized: {self.node_id} ({self.hospital_name})")
    
    def set_mode(self, mode: EmergencyMode):
        """Change operating mode."""
        old_mode = self.mode
        self.mode = mode
        logger.warning(f"Mode change: {old_mode.value} -> {mode.value}")
        
        if mode == EmergencyMode.DISASTER:
            self._activate_disaster_mode()
        elif mode == EmergencyMode.MASS_CASUALTY:
            self._activate_mass_casualty_mode()
    
    def _activate_disaster_mode(self):
        """Activate disaster mode protocols."""
        logger.critical("DISASTER MODE ACTIVATED")
        # Implement disaster-specific logic
        # - Enable all fallback connections
        # - Reduce authentication requirements
        # - Prioritize life-critical only
    
    def _activate_mass_casualty_mode(self):
        """Activate mass casualty protocols."""
        logger.critical("MASS CASUALTY MODE ACTIVATED")
        # Implement mass casualty logic
        # - Clear non-critical from queue
        # - Enable rapid triage
        # - Activate AI assist
    
    def send_message(self, message: ERAIFMessage, destination: str) -> bool:
        """Send message to another node."""
        try:
            # In disaster mode, attempt multiple paths
            if self.mode == EmergencyMode.DISASTER:
                return self._send_disaster_mode(message, destination)
            
            # Normal sending logic
            logger.info(f"Sending {message.message_type.value} to {destination}")
            # Actual network implementation would go here
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.message_queue.append(message)  # Queue for retry
            return False
    
    def _send_disaster_mode(self, message: ERAIFMessage, destination: str) -> bool:
        """Send message using disaster mode protocols."""
        paths = ["primary", "p2p", "satellite", "cellular"]
        
        for path in paths:
            logger.info(f"Attempting {path} path to {destination}")
            # Try each communication path
            # Actual implementation would attempt each
            if path == "p2p":  # Simulate P2P success
                return True
        
        return False
    
    def receive_message(self, message: ERAIFMessage) -> Dict[str, Any]:
        """Process received message."""
        logger.info(f"Received {message.message_type.value} priority={message.priority.name}")
        
        # Verify signature
        if not self._verify_signature(message):
            if self.mode != EmergencyMode.DISASTER:
                return {"status": "error", "reason": "invalid_signature"}
            logger.warning("Invalid signature accepted in DISASTER mode")
        
        # Process based on type
        if message.message_type == MessageType.IMAGE_REQUEST:
            return self._handle_image_request(message)
        elif message.message_type == MessageType.EMERGENCY_ALERT:
            return self._handle_emergency_alert(message)
        
        return {"status": "processed"}
    
    def _verify_signature(self, message: ERAIFMessage) -> bool:
        """Verify message signature."""
        expected = message.generate_signature()
        return message.signature == expected
    
    def _handle_image_request(self, message: ERAIFMessage) -> Dict[str, Any]:
        """Handle incoming image request."""
        patient_id = message.payload.get("patient_id")
        modality = message.payload.get("modality")
        
        logger.info(f"Image request: patient={patient_id}, modality={modality}")
        
        # Check cache first
        cache_key = f"{patient_id}_{modality}"
        if cache_key in self.cached_data:
            return {
                "status": "success",
                "data": self.cached_data[cache_key],
                "source": "cache"
            }
        
        # In real implementation, would query PACS
        return {
            "status": "pending",
            "estimated_time": 30
        }
    
    def _handle_emergency_alert(self, message: ERAIFMessage) -> Dict[str, Any]:
        """Handle emergency alert message."""
        alert_type = message.payload.get("alert_type")
        logger.critical(f"EMERGENCY ALERT: {alert_type}")
        
        # Automatically adjust mode based on alert
        if alert_type == "mass_casualty":
            self.set_mode(EmergencyMode.MASS_CASUALTY)
        elif alert_type == "infrastructure_failure":
            self.set_mode(EmergencyMode.DISASTER)
        
        return {"status": "alert_acknowledged"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current node status."""
        return {
            "node_id": self.node_id,
            "hospital": self.hospital_name,
            "mode": self.mode.value,
            "connected_nodes": len(self.connected_nodes),
            "queued_messages": len(self.message_queue),
            "cache_size": len(self.cached_data),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


class ERAIFNetwork:
    """Manages the ERAIF network of nodes."""
    
    def __init__(self):
        self.nodes: Dict[str, ERAIFNode] = {}
        self.emergency_status = False
        
    def register_node(self, node: ERAIFNode):
        """Register a new node in the network."""
        self.nodes[node.node_id] = node
        logger.info(f"Node registered: {node.node_id}")
        
        # Notify other nodes
        for other_id, other_node in self.nodes.items():
            if other_id != node.node_id:
                other_node.connected_nodes.append(node.node_id)
    
    def broadcast_emergency(self, emergency_type: str):
        """Broadcast emergency to all nodes."""
        self.emergency_status = True
        
        alert = ERAIFMessage(
            priority=Priority.CRITICAL,
            message_type=MessageType.EMERGENCY_ALERT,
            payload={"alert_type": emergency_type}
        )
        
        for node in self.nodes.values():
            node.receive_message(alert)
        
        logger.critical(f"Emergency broadcast sent: {emergency_type}")
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get status of entire network."""
        return {
            "total_nodes": len(self.nodes),
            "emergency_active": self.emergency_status,
            "nodes": [node.get_status() for node in self.nodes.values()]
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize network
    network = ERAIFNetwork()
    
    # Create hospital nodes
    node1 = ERAIFNode("HOSP001", "County General Hospital")
    node2 = ERAIFNode("HOSP002", "St. Mary's Medical Center")
    node3 = ERAIFNode("HOSP003", "Rural Community Hospital")
    
    # Register nodes
    network.register_node(node1)
    network.register_node(node2)
    network.register_node(node3)
    
    # Simulate normal operation
    logger.info("=== NORMAL OPERATION ===")
    
    # Create an image request
    request = ERAIFMessage(
        priority=Priority.URGENT,
        message_type=MessageType.IMAGE_REQUEST,
        payload={
            "patient_id": hashlib.sha256(b"12345").hexdigest(),
            "modality": "CT",
            "body_part": "HEAD",
            "reason": "trauma"
        },
        routing={
            "source": "HOSP001",
            "destination": "HOSP002"
        }
    )
    
    # Send message
    node1.send_message(request, "HOSP002")
    
    # Process at receiving node
    response = node2.receive_message(request)
    print(f"Response: {response}")
    
    # Simulate emergency
    logger.info("\n=== SIMULATING MASS CASUALTY EVENT ===")
    network.broadcast_emergency("mass_casualty")
    
    # Check network status
    status = network.get_network_status()
    print(f"\nNetwork Status: {json.dumps(status, indent=2)}")
    
    # Simulate disaster mode
    logger.info("\n=== SIMULATING DISASTER MODE ===")
    node3.set_mode(EmergencyMode.DISASTER)
    
    # Try sending in disaster mode
    disaster_msg = ERAIFMessage(
        priority=Priority.LIFE_THREATENING,
        message_type=MessageType.IMAGE_REQUEST,
        payload={
            "patient_id": hashlib.sha256(b"67890").hexdigest(),
            "modality": "XRAY",
            "body_part": "CHEST",
            "reason": "crushing_injury"
        }
    )
    
    node3.send_message(disaster_msg, "HOSP001")
    
    print("\n=== ERAIF SIMULATION COMPLETE ===")
    print("This demonstrates core ERAIF functionality:")
    print("- Message creation and routing")
    print("- Emergency mode activation")
    print("- Disaster failover protocols")
    print("- Network-wide coordination")
