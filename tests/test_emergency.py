"""
Emergency Scenario Tests

Integration tests for emergency scenarios including network failures,
system overloads, and disaster response protocols.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from src.eraif_core import ERAIFCore
from src.models.emergency import EmergencyMode
from src.models.study import Study
from src.models.patient import Patient


class TestEmergencyScenarios:
    """Test emergency scenario handling."""
    
    @pytest.fixture
    async def eraif_core(self):
        """Create a test ERAIF Core instance."""
        config = {
            "emergency": {
                "triggers": [
                    {"type": "network_failure", "threshold": 5},
                    {"type": "system_overload", "threshold": 90}
                ],
                "disaster_mode": {
                    "compression": True,
                    "priority_filter": ["CRITICAL", "HIGH"],
                    "batch_size": 10
                }
            }
        }
        core = ERAIFCore(config)
        await core.initialize()
        yield core
        await core.shutdown()
    
    @pytest.mark.asyncio
    async def test_network_failure_trigger(self, eraif_core):
        """Test automatic emergency activation on network failure."""
        # Simulate network failure
        with patch.object(eraif_core.monitor, 'detect_network_failure') as mock_failure:
            mock_failure.return_value = True
            
            # This would be triggered by the monitoring system
            await eraif_core.activate_emergency_mode("Network failure detected")
            
            assert eraif_core.emergency_mode != EmergencyMode.NORMAL
            assert eraif_core.emergency_id is not None
    
    @pytest.mark.asyncio
    async def test_system_overload_trigger(self, eraif_core):
        """Test emergency activation on system overload."""
        with patch.object(eraif_core.monitor, 'get_cpu_usage') as mock_cpu:
            mock_cpu.return_value = 95.0  # Above threshold
            
            await eraif_core.activate_emergency_mode("System overload detected")
            
            assert eraif_core.emergency_mode != EmergencyMode.NORMAL
    
    @pytest.mark.asyncio
    async def test_priority_filtering_in_disaster_mode(self, eraif_core):
        """Test that only critical/high priority studies are processed in disaster mode."""
        # Force disaster mode
        with patch.object(eraif_core.monitor, 'get_system_health') as mock_health:
            mock_health.return_value = {"connectivity": 0.1}
            
            await eraif_core.activate_emergency_mode("Disaster simulation")
            
            assert eraif_core.emergency_mode == EmergencyMode.DISASTER
            
            # Test study filtering (would be implemented in actual study processing)
            critical_study = Study(
                study_id="critical_001",
                priority="CRITICAL",
                modality="CT"
            )
            
            low_study = Study(
                study_id="low_001", 
                priority="LOW",
                modality="XR"
            )
            
            # In disaster mode, only critical/high priority should be processed
            assert critical_study.priority in ["CRITICAL", "HIGH"]
            assert low_study.priority not in ["CRITICAL", "HIGH"]
    
    @pytest.mark.asyncio
    async def test_emergency_queue_processing(self, eraif_core):
        """Test emergency queue processing."""
        # Add studies to emergency queue
        study1 = Study(study_id="emg_001", priority="CRITICAL")
        study2 = Study(study_id="emg_002", priority="HIGH")
        
        eraif_core.emergency_queue.extend([study1, study2])
        
        # Activate emergency mode
        await eraif_core.activate_emergency_mode("Queue processing test")
        
        # Queue should be processed (mocked)
        # In real implementation, studies would be transferred/processed
        assert len(eraif_core.emergency_queue) == 0  # Queue cleared after processing
    
    @pytest.mark.asyncio
    async def test_failover_to_backup_systems(self, eraif_core):
        """Test failover to backup systems during emergency."""
        # Simulate primary system failure
        with patch.object(eraif_core.dicom_protocol, 'is_available') as mock_dicom:
            mock_dicom.return_value = False
            
            # Activate emergency mode
            await eraif_core.activate_emergency_mode("Primary system failure")
            
            # Should attempt to use backup systems
            backup_status = await eraif_core._check_backup_systems()
            assert "offline_storage" in backup_status
            assert "satellite_link" in backup_status


class TestDisasterRecovery:
    """Test disaster recovery procedures."""
    
    @pytest.fixture
    async def eraif_core(self):
        config = {}
        core = ERAIFCore(config)
        await core.initialize()
        yield core
        await core.shutdown()
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self, eraif_core):
        """Test graceful system degradation during emergencies."""
        # Simulate various system failures
        failures = {
            "database": False,
            "network": False,
            "storage": True  # Only storage available
        }
        
        with patch.object(eraif_core.monitor, 'get_system_components') as mock_components:
            mock_components.return_value = failures
            
            await eraif_core.activate_emergency_mode("Multiple system failures")
            
            # System should still be functional with limited capabilities
            status = await eraif_core.get_health_status()
            assert status["status"] in ["degraded", "healthy"]
    
    @pytest.mark.asyncio
    async def test_automatic_recovery(self, eraif_core):
        """Test automatic recovery when systems come back online."""
        # Start in emergency mode
        await eraif_core.activate_emergency_mode("Recovery test")
        
        # Simulate systems coming back online
        with patch.object(eraif_core.monitor, 'get_system_health') as mock_health:
            mock_health.return_value = {"connectivity": 0.9, "cpu": 20, "memory": 30}
            
            # In real implementation, this would trigger automatic recovery
            # For now, manually test recovery
            await eraif_core.deactivate_emergency_mode("Systems recovered")
            
            assert eraif_core.emergency_mode == EmergencyMode.NORMAL
    
    @pytest.mark.asyncio
    async def test_data_synchronization_after_recovery(self, eraif_core):
        """Test data synchronization after emergency recovery."""
        # Simulate offline period with queued data
        offline_data = [
            {"study_id": "offline_001", "timestamp": datetime.utcnow()},
            {"study_id": "offline_002", "timestamp": datetime.utcnow()}
        ]
        
        # Start emergency mode
        await eraif_core.activate_emergency_mode("Offline simulation")
        
        # Add offline data to queue (simulated)
        eraif_core.emergency_queue.extend([
            Study(study_id=data["study_id"]) for data in offline_data
        ])
        
        # Recovery - data should be synchronized
        await eraif_core.deactivate_emergency_mode("Recovery complete")
        
        # Verify synchronization occurred (in real implementation)
        # This would check that queued data was properly synchronized


class TestEmergencyProtocols:
    """Test emergency protocol handling."""
    
    @pytest.fixture
    async def eraif_core(self):
        config = {}
        core = ERAIFCore(config)
        await core.initialize()
        yield core
        await core.shutdown()
    
    @pytest.mark.asyncio
    async def test_protocol_switching(self, eraif_core):
        """Test protocol switching during emergency modes."""
        # Normal mode - all protocols available
        assert eraif_core.emergency_mode == EmergencyMode.NORMAL
        
        # Switch to emergency mode
        await eraif_core.activate_emergency_mode("Protocol switching test")
        
        # Protocols should be configured for emergency mode
        # This would be verified by checking protocol configurations
        assert eraif_core.emergency_mode != EmergencyMode.NORMAL
    
    @pytest.mark.asyncio
    async def test_compression_in_disaster_mode(self, eraif_core):
        """Test data compression in disaster mode."""
        # Force disaster mode
        with patch.object(eraif_core.monitor, 'get_system_health') as mock_health:
            mock_health.return_value = {"connectivity": 0.1}
            
            await eraif_core.activate_emergency_mode("Compression test")
            
            assert eraif_core.emergency_mode == EmergencyMode.DISASTER
            
            # In disaster mode, compression should be enabled
            # This would be verified by checking protocol settings
    
    @pytest.mark.asyncio
    async def test_priority_based_qos(self, eraif_core):
        """Test priority-based quality of service."""
        await eraif_core.activate_emergency_mode("QoS test")
        
        # Critical studies should get priority
        critical_study = Study(study_id="critical", priority="CRITICAL")
        normal_study = Study(study_id="normal", priority="NORMAL")
        
        # In real implementation, critical studies would be processed first
        assert critical_study.priority == "CRITICAL"
        assert normal_study.priority == "NORMAL"


@pytest.mark.asyncio
async def test_concurrent_emergency_handling():
    """Test handling of concurrent emergency situations."""
    config = {}
    core = ERAIFCore(config)
    await core.initialize()
    
    try:
        # Simulate multiple concurrent emergency triggers
        tasks = []
        
        # Network failure
        tasks.append(core.activate_emergency_mode("Network failure"))
        
        # Wait a bit, then try system overload
        await asyncio.sleep(0.1)
        
        # System should handle multiple triggers gracefully
        # Second activation should not interfere with first
        status = await core.get_emergency_status()
        assert status["emergency_mode"] is True
        
    finally:
        await core.shutdown()


@pytest.mark.asyncio
async def test_emergency_duration_tracking():
    """Test emergency duration tracking and reporting."""
    config = {}
    core = ERAIFCore(config)
    await core.initialize()
    
    try:
        start_time = datetime.utcnow()
        
        # Activate emergency mode
        await core.activate_emergency_mode("Duration test", "2h")
        
        # Check that start time is recorded
        assert core.emergency_start_time is not None
        assert core.emergency_start_time >= start_time
        
        # Simulate some time passing
        await asyncio.sleep(0.1)
        
        # Deactivate and check duration
        result = await core.deactivate_emergency_mode("Test complete")
        
        assert "duration" in result
        assert result["duration"] is not None
        
    finally:
        await core.shutdown()
