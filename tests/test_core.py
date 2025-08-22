"""
Core ERAIF System Tests

Unit tests for the core ERAIF functionality including emergency mode
activation, protocol handling, and system monitoring.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from src.eraif_core import ERAIFCore
from src.models.emergency import EmergencyMode


class TestERAIFCore:
    """Test cases for ERAIF Core functionality."""
    
    @pytest.fixture
    async def eraif_core(self):
        """Create a test ERAIF Core instance."""
        config = {
            "dicom": {"port": 11112},
            "fhir": {"base_url": "http://localhost:8080/fhir"},
            "monitoring": {"interval": 10}
        }
        core = ERAIFCore(config)
        await core.initialize()
        yield core
        await core.shutdown()
    
    @pytest.mark.asyncio
    async def test_initialization(self, eraif_core):
        """Test ERAIF Core initialization."""
        assert eraif_core.system_status == "ready"
        assert eraif_core.emergency_mode == EmergencyMode.NORMAL
        assert eraif_core.emergency_id is None
    
    @pytest.mark.asyncio
    async def test_health_status(self, eraif_core):
        """Test health status reporting."""
        status = await eraif_core.get_health_status()
        
        assert status["status"] == "healthy"
        assert "timestamp" in status
        assert "version" in status
        assert status["emergency_mode"] == "normal"
        assert "components" in status
    
    @pytest.mark.asyncio
    async def test_emergency_activation(self, eraif_core):
        """Test emergency mode activation."""
        reason = "Test emergency activation"
        
        response = await eraif_core.activate_emergency_mode(reason)
        
        assert response["status"] == "activated"
        assert response["reason"] == reason
        assert "emergency_id" in response
        assert "activation_time" in response
        
        # Verify emergency mode is active
        assert eraif_core.emergency_mode != EmergencyMode.NORMAL
        assert eraif_core.emergency_id is not None
        assert eraif_core.emergency_start_time is not None
    
    @pytest.mark.asyncio
    async def test_emergency_deactivation(self, eraif_core):
        """Test emergency mode deactivation."""
        # First activate emergency mode
        await eraif_core.activate_emergency_mode("Test activation")
        
        # Then deactivate
        reason = "Test deactivation"
        response = await eraif_core.deactivate_emergency_mode(reason)
        
        assert response["status"] == "deactivated"
        assert response["reason"] == reason
        assert "deactivation_time" in response
        assert "duration" in response
        
        # Verify normal mode is restored
        assert eraif_core.emergency_mode == EmergencyMode.NORMAL
        assert eraif_core.emergency_id is None
        assert eraif_core.emergency_start_time is None
    
    @pytest.mark.asyncio
    async def test_emergency_status(self, eraif_core):
        """Test emergency status reporting."""
        # Test normal mode status
        status = await eraif_core.get_emergency_status()
        assert status["emergency_mode"] is False
        assert status["mode"] == "normal"
        
        # Activate emergency mode
        await eraif_core.activate_emergency_mode("Test")
        
        # Test emergency mode status
        status = await eraif_core.get_emergency_status()
        assert status["emergency_mode"] is True
        assert status["mode"] != "normal"
        assert status["emergency_id"] is not None
    
    @pytest.mark.asyncio
    async def test_emergency_systems_test(self, eraif_core):
        """Test emergency systems testing."""
        test_results = await eraif_core.test_emergency_systems()
        
        assert "test_id" in test_results
        assert "timestamp" in test_results
        assert "overall_status" in test_results
        assert "components" in test_results
        
        # Should test all major components
        components = test_results["components"]
        assert "dicom" in components
        assert "fhir" in components
        assert "ecp" in components
        assert "monitor" in components
        assert "backup" in components
    
    @pytest.mark.asyncio
    async def test_duration_parsing(self, eraif_core):
        """Test duration string parsing."""
        # Test various duration formats
        assert eraif_core._parse_duration("1h").total_seconds() == 3600
        assert eraif_core._parse_duration("30m").total_seconds() == 1800
        assert eraif_core._parse_duration("2d").total_seconds() == 172800
        
        # Test default fallback
        assert eraif_core._parse_duration("invalid").total_seconds() == 86400


class TestEmergencyModeSelection:
    """Test emergency mode selection based on system conditions."""
    
    @pytest.fixture
    async def eraif_core(self):
        """Create a test ERAIF Core instance."""
        config = {}
        core = ERAIFCore(config)
        await core.initialize()
        yield core
        await core.shutdown()
    
    @pytest.mark.asyncio
    async def test_disaster_mode_selection(self, eraif_core):
        """Test disaster mode selection for low connectivity."""
        with patch.object(eraif_core.monitor, 'get_system_health') as mock_health:
            mock_health.return_value = {"connectivity": 0.2}
            
            await eraif_core.activate_emergency_mode("Low connectivity test")
            assert eraif_core.emergency_mode == EmergencyMode.DISASTER
    
    @pytest.mark.asyncio
    async def test_hybrid_mode_selection(self, eraif_core):
        """Test hybrid mode selection for medium connectivity."""
        with patch.object(eraif_core.monitor, 'get_system_health') as mock_health:
            mock_health.return_value = {"connectivity": 0.5}
            
            await eraif_core.activate_emergency_mode("Medium connectivity test")
            assert eraif_core.emergency_mode == EmergencyMode.HYBRID
    
    @pytest.mark.asyncio
    async def test_emergency_mode_selection(self, eraif_core):
        """Test emergency mode selection for good connectivity."""
        with patch.object(eraif_core.monitor, 'get_system_health') as mock_health:
            mock_health.return_value = {"connectivity": 0.8}
            
            await eraif_core.activate_emergency_mode("Good connectivity test")
            assert eraif_core.emergency_mode == EmergencyMode.EMERGENCY


@pytest.mark.asyncio
async def test_concurrent_emergency_operations():
    """Test concurrent emergency operations."""
    config = {}
    core = ERAIFCore(config)
    await core.initialize()
    
    try:
        # Test concurrent activation attempts
        tasks = [
            core.activate_emergency_mode(f"Test {i}")
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # First activation should succeed, others should handle gracefully
        successful_activations = [
            r for r in results 
            if isinstance(r, dict) and r.get("status") == "activated"
        ]
        
        assert len(successful_activations) >= 1
        
    finally:
        await core.shutdown()
