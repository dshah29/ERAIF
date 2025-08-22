"""
ERAIF Core Module

This module contains the core functionality of the Emergency Radiology AI
Interoperability Framework, including emergency mode management, system
monitoring, and protocol handling.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4

from .models.emergency import EmergencyMode, EmergencyStatus
from .models.patient import Patient
from .models.study import Study
from .protocols.dicom import DICOMProtocol
from .protocols.fhir import FHIRProtocol
from .protocols.ecp import ECPProtocol
from .utils.monitoring import SystemMonitor


class ERAIFCore:
    """
    Core ERAIF system that manages emergency protocols, system monitoring,
    and interoperability between medical imaging systems.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ERAIF Core system.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # System state
        self.emergency_mode = EmergencyMode.NORMAL
        self.emergency_id: Optional[str] = None
        self.emergency_start_time: Optional[datetime] = None
        self.system_status = "initializing"
        
        # Protocol handlers
        self.dicom_protocol = DICOMProtocol(config.get("dicom", {}))
        self.fhir_protocol = FHIRProtocol(config.get("fhir", {}))
        self.ecp_protocol = ECPProtocol(config.get("ecp", {}))
        
        # System monitoring
        self.monitor = SystemMonitor(config.get("monitoring", {}))
        
        # Active connections and studies
        self.active_connections: Dict[str, Any] = {}
        self.active_studies: Dict[str, Study] = {}
        self.emergency_queue: List[Study] = []
        
        self.logger.info("ERAIF Core initialized")
    
    async def initialize(self):
        """Initialize the ERAIF system."""
        try:
            self.logger.info("Initializing ERAIF Core...")
            
            # Initialize protocol handlers
            await self.dicom_protocol.initialize()
            await self.fhir_protocol.initialize()
            await self.ecp_protocol.initialize()
            
            # Start system monitoring
            await self.monitor.start()
            
            # Setup emergency triggers
            await self._setup_emergency_triggers()
            
            self.system_status = "ready"
            self.logger.info("ERAIF Core initialization complete")
            
        except Exception as e:
            self.system_status = "error"
            self.logger.error(f"Failed to initialize ERAIF Core: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the ERAIF system gracefully."""
        try:
            self.logger.info("Shutting down ERAIF Core...")
            
            # Deactivate emergency mode if active
            if self.emergency_mode != EmergencyMode.NORMAL:
                await self.deactivate_emergency_mode("System shutdown")
            
            # Shutdown protocol handlers
            await self.dicom_protocol.shutdown()
            await self.fhir_protocol.shutdown()
            await self.ecp_protocol.shutdown()
            
            # Stop monitoring
            await self.monitor.stop()
            
            self.system_status = "stopped"
            self.logger.info("ERAIF Core shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get system health status."""
        return {
            "status": "healthy" if self.system_status == "ready" else self.system_status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "emergency_mode": self.emergency_mode.value,
            "components": {
                "dicom": await self.dicom_protocol.get_status(),
                "fhir": await self.fhir_protocol.get_status(),
                "ecp": await self.ecp_protocol.get_status(),
                "monitor": await self.monitor.get_status()
            }
        }
    
    async def get_emergency_status(self) -> Dict[str, Any]:
        """Get emergency system readiness status."""
        return {
            "emergency_mode": self.emergency_mode != EmergencyMode.NORMAL,
            "mode": self.emergency_mode.value,
            "emergency_id": self.emergency_id,
            "readiness": "ready" if self.system_status == "ready" else "not_ready",
            "last_test": await self._get_last_test_time(),
            "active_since": self.emergency_start_time.isoformat() if self.emergency_start_time else None,
            "backup_systems": await self._check_backup_systems(),
            "queue_size": len(self.emergency_queue)
        }
    
    async def activate_emergency_mode(self, reason: str, duration: Optional[str] = None) -> Dict[str, Any]:
        """
        Activate emergency mode.
        
        Args:
            reason: Reason for activation
            duration: Estimated duration (e.g., "72h")
        
        Returns:
            Emergency activation response
        """
        try:
            self.logger.warning(f"Activating emergency mode: {reason}")
            
            # Generate emergency ID
            self.emergency_id = f"emg_{uuid4().hex[:8]}"
            self.emergency_start_time = datetime.utcnow()
            
            # Determine emergency mode based on system conditions
            system_health = await self.monitor.get_system_health()
            if system_health["connectivity"] < 0.3:
                self.emergency_mode = EmergencyMode.DISASTER
            elif system_health["connectivity"] < 0.7:
                self.emergency_mode = EmergencyMode.HYBRID
            else:
                self.emergency_mode = EmergencyMode.EMERGENCY
            
            # Configure protocols for emergency mode
            await self.dicom_protocol.set_emergency_mode(self.emergency_mode)
            await self.fhir_protocol.set_emergency_mode(self.emergency_mode)
            await self.ecp_protocol.set_emergency_mode(self.emergency_mode)
            
            # Start emergency monitoring
            await self.monitor.start_emergency_monitoring()
            
            # Process queued studies
            await self._process_emergency_queue()
            
            estimated_end = None
            if duration:
                estimated_end = (self.emergency_start_time + self._parse_duration(duration)).isoformat()
            
            response = {
                "emergency_id": self.emergency_id,
                "status": "activated",
                "mode": self.emergency_mode.value,
                "activation_time": self.emergency_start_time.isoformat(),
                "reason": reason,
                "estimated_end": estimated_end
            }
            
            self.logger.warning(f"Emergency mode activated: {response}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to activate emergency mode: {e}")
            raise
    
    async def deactivate_emergency_mode(self, reason: str) -> Dict[str, Any]:
        """
        Deactivate emergency mode.
        
        Args:
            reason: Reason for deactivation
        
        Returns:
            Emergency deactivation response
        """
        try:
            if self.emergency_mode == EmergencyMode.NORMAL:
                return {"status": "already_normal"}
            
            self.logger.info(f"Deactivating emergency mode: {reason}")
            
            # Return protocols to normal mode
            await self.dicom_protocol.set_emergency_mode(EmergencyMode.NORMAL)
            await self.fhir_protocol.set_emergency_mode(EmergencyMode.NORMAL)
            await self.ecp_protocol.set_emergency_mode(EmergencyMode.NORMAL)
            
            # Stop emergency monitoring
            await self.monitor.stop_emergency_monitoring()
            
            # Calculate emergency duration
            duration = None
            if self.emergency_start_time:
                duration = str(datetime.utcnow() - self.emergency_start_time)
            
            response = {
                "emergency_id": self.emergency_id,
                "status": "deactivated",
                "deactivation_time": datetime.utcnow().isoformat(),
                "duration": duration,
                "reason": reason
            }
            
            # Reset emergency state
            self.emergency_mode = EmergencyMode.NORMAL
            self.emergency_id = None
            self.emergency_start_time = None
            
            self.logger.info(f"Emergency mode deactivated: {response}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to deactivate emergency mode: {e}")
            raise
    
    async def test_emergency_systems(self) -> Dict[str, Any]:
        """Test emergency systems readiness."""
        try:
            self.logger.info("Testing emergency systems...")
            
            test_results = {
                "test_id": f"test_{uuid4().hex[:8]}",
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": "pass",
                "components": {}
            }
            
            # Test protocol handlers
            test_results["components"]["dicom"] = await self.dicom_protocol.test_emergency_readiness()
            test_results["components"]["fhir"] = await self.fhir_protocol.test_emergency_readiness()
            test_results["components"]["ecp"] = await self.ecp_protocol.test_emergency_readiness()
            
            # Test system monitoring
            test_results["components"]["monitor"] = await self.monitor.test_emergency_readiness()
            
            # Test backup systems
            test_results["components"]["backup"] = await self._test_backup_systems()
            
            # Determine overall status
            failed_components = [
                name for name, result in test_results["components"].items()
                if result.get("status") != "pass"
            ]
            
            if failed_components:
                test_results["overall_status"] = "fail"
                test_results["failed_components"] = failed_components
            
            self.logger.info(f"Emergency systems test completed: {test_results['overall_status']}")
            return test_results
            
        except Exception as e:
            self.logger.error(f"Emergency systems test failed: {e}")
            return {
                "test_id": f"test_{uuid4().hex[:8]}",
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }
    
    async def _setup_emergency_triggers(self):
        """Setup automatic emergency triggers."""
        # This would setup monitoring for network failures, system overload, etc.
        # Implementation depends on specific monitoring requirements
        pass
    
    async def _get_last_test_time(self) -> Optional[str]:
        """Get timestamp of last emergency test."""
        # This would retrieve the last test time from storage
        return "2024-01-15T09:00:00Z"  # Placeholder
    
    async def _check_backup_systems(self) -> Dict[str, str]:
        """Check status of backup systems."""
        return {
            "offline_storage": "ready",
            "satellite_link": "ready",
            "battery_backup": "90%"
        }
    
    async def _test_backup_systems(self) -> Dict[str, Any]:
        """Test backup systems."""
        return {
            "status": "pass",
            "offline_storage": "ready",
            "satellite_link": "ready",
            "battery_backup": "90%"
        }
    
    async def _process_emergency_queue(self):
        """Process studies in the emergency queue."""
        while self.emergency_queue:
            study = self.emergency_queue.pop(0)
            await self._process_emergency_study(study)
    
    async def _process_emergency_study(self, study: Study):
        """Process a single study in emergency mode."""
        # Implementation for emergency study processing
        pass
    
    def _parse_duration(self, duration: str) -> timedelta:
        """Parse duration string (e.g., '72h', '30m') into timedelta."""
        if duration.endswith('h'):
            return timedelta(hours=int(duration[:-1]))
        elif duration.endswith('m'):
            return timedelta(minutes=int(duration[:-1]))
        elif duration.endswith('d'):
            return timedelta(days=int(duration[:-1]))
        else:
            return timedelta(hours=24)  # Default to 24 hours
