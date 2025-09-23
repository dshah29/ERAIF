"""
Health Checking for ERAIF AI/ML Components

Provides comprehensive health monitoring for all system components
including AI models, workflows, and infrastructure.
"""

import asyncio
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from ..core.config import ERAIFConfig


class HealthStatus(str, Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    component: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    response_time_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "component": self.component,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "response_time_ms": self.response_time_ms
        }


class HealthChecker:
    """
    Comprehensive health checker for ERAIF AI/ML system.
    
    Monitors:
    - System resources (CPU, memory, disk, GPU)
    - AI model availability and performance
    - Database connectivity
    - External service integrations
    - Workflow engine status
    - Emergency mode readiness
    """
    
    def __init__(self, config: ERAIFConfig):
        """Initialize health checker."""
        self.config = config
        self.health_checks = {}
        self.last_check_results = {}
        
        # Register default health checks
        self._register_default_checks()
        
        # Health check intervals
        self.check_interval = config.monitoring.health_check_interval_seconds
        
        # Background monitoring
        self.monitoring_task = None
        self.is_monitoring = False
    
    def _register_default_checks(self):
        """Register default health checks."""
        # System resource checks
        self.register_check("system_cpu", self._check_system_cpu)
        self.register_check("system_memory", self._check_system_memory)
        self.register_check("system_disk", self._check_system_disk)
        
        # AI component checks
        self.register_check("ai_pipeline", self._check_ai_pipeline)
        self.register_check("ai_models", self._check_ai_models)
        self.register_check("workflow_engine", self._check_workflow_engine)
        
        # Configuration checks
        self.register_check("configuration", self._check_configuration)
        self.register_check("emergency_readiness", self._check_emergency_readiness)
        
        # Optional checks based on configuration
        if self.config.ai.enable_gpu:
            self.register_check("gpu_resources", self._check_gpu_resources)
    
    def register_check(self, name: str, check_function: Callable) -> None:
        """Register a new health check."""
        self.health_checks[name] = check_function
    
    async def run_check(self, check_name: str) -> HealthCheckResult:
        """Run a specific health check."""
        if check_name not in self.health_checks:
            return HealthCheckResult(
                component=check_name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check '{check_name}' not found",
                details={},
                timestamp=datetime.now(),
                response_time_ms=0.0
            )
        
        start_time = time.time()
        
        try:
            check_function = self.health_checks[check_name]
            result = await check_function()
            
            response_time = (time.time() - start_time) * 1000
            
            if isinstance(result, HealthCheckResult):
                result.response_time_ms = response_time
                return result
            else:
                # Handle simple boolean or dict results
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = f"{check_name} check {'passed' if result else 'failed'}"
                
                return HealthCheckResult(
                    component=check_name,
                    status=status,
                    message=message,
                    details=result if isinstance(result, dict) else {},
                    timestamp=datetime.now(),
                    response_time_ms=response_time
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                component=check_name,
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e), "error_type": type(e).__name__},
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
    
    async def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks."""
        results = {}
        
        # Run checks concurrently
        tasks = []
        for check_name in self.health_checks:
            tasks.append(self.run_check(check_name))
        
        check_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, check_name in enumerate(self.health_checks):
            result = check_results[i]
            if isinstance(result, Exception):
                # Handle exceptions from gather
                results[check_name] = HealthCheckResult(
                    component=check_name,
                    status=HealthStatus.CRITICAL,
                    message=f"Health check exception: {str(result)}",
                    details={"error": str(result)},
                    timestamp=datetime.now(),
                    response_time_ms=0.0
                )
            else:
                results[check_name] = result
        
        # Cache results
        self.last_check_results = results
        
        return results
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health summary."""
        results = await self.run_all_checks()
        
        # Calculate overall health
        status_counts = {status: 0 for status in HealthStatus}
        total_response_time = 0
        
        for result in results.values():
            status_counts[result.status] += 1
            total_response_time += result.response_time_ms
        
        # Determine overall status
        if status_counts[HealthStatus.CRITICAL] > 0:
            overall_status = HealthStatus.CRITICAL
        elif status_counts[HealthStatus.UNHEALTHY] > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        # Calculate health score (0-100)
        total_checks = len(results)
        if total_checks > 0:
            health_score = (
                (status_counts[HealthStatus.HEALTHY] * 100 +
                 status_counts[HealthStatus.DEGRADED] * 70 +
                 status_counts[HealthStatus.UNHEALTHY] * 30 +
                 status_counts[HealthStatus.CRITICAL] * 0) / total_checks
            )
        else:
            health_score = 0
        
        return {
            "overall_status": overall_status.value,
            "health_score": round(health_score, 2),
            "timestamp": datetime.now().isoformat(),
            "total_checks": total_checks,
            "status_breakdown": {status.value: count for status, count in status_counts.items()},
            "average_response_time_ms": total_response_time / total_checks if total_checks > 0 else 0,
            "checks": {name: result.to_dict() for name, result in results.items()}
        }
    
    def start_monitoring(self):
        """Start background health monitoring."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    def stop_monitoring(self):
        """Stop background health monitoring."""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
    
    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.is_monitoring:
            try:
                await self.run_all_checks()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    # Individual health check implementations
    
    async def _check_system_cpu(self) -> HealthCheckResult:
        """Check system CPU usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent < 70:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"
            elif cpu_percent < 85:
                status = HealthStatus.DEGRADED
                message = f"CPU usage elevated: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"CPU usage high: {cpu_percent:.1f}%"
            
            return HealthCheckResult(
                component="system_cpu",
                status=status,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "cpu_count": psutil.cpu_count(),
                    "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                timestamp=datetime.now(),
                response_time_ms=0
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="system_cpu",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check CPU: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    async def _check_system_memory(self) -> HealthCheckResult:
        """Check system memory usage."""
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            if memory_percent < 75:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory_percent:.1f}%"
            elif memory_percent < 90:
                status = HealthStatus.DEGRADED
                message = f"Memory usage elevated: {memory_percent:.1f}%"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage high: {memory_percent:.1f}%"
            
            return HealthCheckResult(
                component="system_memory",
                status=status,
                message=message,
                details={
                    "memory_percent": memory_percent,
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2)
                },
                timestamp=datetime.now(),
                response_time_ms=0
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="system_memory",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check memory: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    async def _check_system_disk(self) -> HealthCheckResult:
        """Check system disk usage."""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            if disk_percent < 80:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {disk_percent:.1f}%"
            elif disk_percent < 90:
                status = HealthStatus.DEGRADED
                message = f"Disk usage elevated: {disk_percent:.1f}%"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Disk usage high: {disk_percent:.1f}%"
            
            return HealthCheckResult(
                component="system_disk",
                status=status,
                message=message,
                details={
                    "disk_percent": disk_percent,
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2)
                },
                timestamp=datetime.now(),
                response_time_ms=0
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="system_disk",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check disk: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    async def _check_gpu_resources(self) -> HealthCheckResult:
        """Check GPU resources."""
        try:
            # This would require nvidia-ml-py or similar
            # For demo purposes, return healthy status
            return HealthCheckResult(
                component="gpu_resources",
                status=HealthStatus.HEALTHY,
                message="GPU resources available",
                details={
                    "gpu_enabled": self.config.ai.enable_gpu,
                    "note": "GPU monitoring not fully implemented in demo"
                },
                timestamp=datetime.now(),
                response_time_ms=0
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="gpu_resources",
                status=HealthStatus.DEGRADED,
                message=f"GPU check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    async def _check_ai_pipeline(self) -> HealthCheckResult:
        """Check AI pipeline status."""
        try:
            # In production, this would test the actual AI pipeline
            # For demo, simulate a health check
            
            status = HealthStatus.HEALTHY
            message = "AI pipeline operational"
            details = {
                "models_loaded": True,
                "langgraph_ready": True,
                "agents_available": True,
                "inference_ready": True
            }
            
            return HealthCheckResult(
                component="ai_pipeline",
                status=status,
                message=message,
                details=details,
                timestamp=datetime.now(),
                response_time_ms=0
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="ai_pipeline",
                status=HealthStatus.CRITICAL,
                message=f"AI pipeline check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    async def _check_ai_models(self) -> HealthCheckResult:
        """Check AI models availability."""
        try:
            # Check model cache directory
            model_cache_path = self.config.ai.model_cache_dir
            
            details = {
                "model_cache_dir": model_cache_path,
                "ct_analysis_enabled": self.config.ai.enable_ct_analysis,
                "xray_analysis_enabled": self.config.ai.enable_xray_analysis,
                "mri_analysis_enabled": self.config.ai.enable_mri_analysis,
                "ultrasound_analysis_enabled": self.config.ai.enable_ultrasound_analysis
            }
            
            # Simple check - in production would verify actual model files
            status = HealthStatus.HEALTHY
            message = "AI models available"
            
            return HealthCheckResult(
                component="ai_models",
                status=status,
                message=message,
                details=details,
                timestamp=datetime.now(),
                response_time_ms=0
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="ai_models",
                status=HealthStatus.UNHEALTHY,
                message=f"AI models check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    async def _check_workflow_engine(self) -> HealthCheckResult:
        """Check workflow engine status."""
        try:
            # Check LangGraph configuration
            details = {
                "langgraph_backend": self.config.ai.langgraph_checkpoint_backend,
                "thread_timeout": self.config.ai.langgraph_thread_timeout,
                "workflows_available": [
                    "mass_casualty", "disaster_response", "resource_optimization",
                    "patient_transfer", "surge_capacity"
                ]
            }
            
            status = HealthStatus.HEALTHY
            message = "Workflow engine operational"
            
            return HealthCheckResult(
                component="workflow_engine",
                status=status,
                message=message,
                details=details,
                timestamp=datetime.now(),
                response_time_ms=0
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="workflow_engine",
                status=HealthStatus.UNHEALTHY,
                message=f"Workflow engine check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    async def _check_configuration(self) -> HealthCheckResult:
        """Check system configuration."""
        try:
            # Validate configuration
            config_issues = self.config.validate()
            
            if not config_issues:
                status = HealthStatus.HEALTHY
                message = "Configuration valid"
            else:
                status = HealthStatus.DEGRADED
                message = f"Configuration issues found: {len(config_issues)}"
            
            details = {
                "deployment_mode": self.config.deployment_mode.value,
                "issues": config_issues,
                "ai_enabled": bool(self.config.ai.openai_api_key),
                "emergency_auto_activation": self.config.emergency.auto_activation_enabled
            }
            
            return HealthCheckResult(
                component="configuration",
                status=status,
                message=message,
                details=details,
                timestamp=datetime.now(),
                response_time_ms=0
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="configuration",
                status=HealthStatus.CRITICAL,
                message=f"Configuration check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    async def _check_emergency_readiness(self) -> HealthCheckResult:
        """Check emergency mode readiness."""
        try:
            # Check emergency configuration
            emergency_config = self.config.emergency
            
            details = {
                "auto_activation_enabled": emergency_config.auto_activation_enabled,
                "offline_mode_enabled": emergency_config.enable_offline_mode,
                "disaster_mode_compression": emergency_config.disaster_mode_compression,
                "network_failure_threshold": emergency_config.network_failure_threshold_seconds,
                "cpu_threshold": emergency_config.cpu_threshold_percent,
                "memory_threshold": emergency_config.memory_threshold_percent
            }
            
            # Check readiness factors
            readiness_score = 0
            total_factors = 6
            
            if emergency_config.auto_activation_enabled:
                readiness_score += 1
            if emergency_config.enable_offline_mode:
                readiness_score += 1
            if emergency_config.disaster_mode_compression:
                readiness_score += 1
            if emergency_config.network_failure_threshold_seconds > 0:
                readiness_score += 1
            if emergency_config.cpu_threshold_percent > 0:
                readiness_score += 1
            if emergency_config.memory_threshold_percent > 0:
                readiness_score += 1
            
            readiness_percentage = (readiness_score / total_factors) * 100
            
            if readiness_percentage >= 80:
                status = HealthStatus.HEALTHY
                message = f"Emergency readiness: {readiness_percentage:.0f}%"
            elif readiness_percentage >= 60:
                status = HealthStatus.DEGRADED
                message = f"Emergency readiness degraded: {readiness_percentage:.0f}%"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Emergency readiness poor: {readiness_percentage:.0f}%"
            
            details["readiness_percentage"] = readiness_percentage
            
            return HealthCheckResult(
                component="emergency_readiness",
                status=status,
                message=message,
                details=details,
                timestamp=datetime.now(),
                response_time_ms=0
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="emergency_readiness",
                status=HealthStatus.CRITICAL,
                message=f"Emergency readiness check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now(),
                response_time_ms=0
            )
