"""
Enhanced Logging for ERAIF AI/ML Components

Provides structured logging with AI-specific metrics and emergency context.
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import structlog

from ..core.config import ERAIFConfig


class ERAIFLogger:
    """
    Enhanced logger for ERAIF AI/ML system with structured logging,
    emergency context, and performance metrics.
    """
    
    def __init__(self, config: ERAIFConfig):
        """Initialize ERAIF logger."""
        self.config = config
        
        # Configure structured logging
        self._setup_structured_logging()
        
        # Create component loggers
        self.system_logger = structlog.get_logger("eraif.system")
        self.ai_logger = structlog.get_logger("eraif.ai")
        self.workflow_logger = structlog.get_logger("eraif.workflow")
        self.emergency_logger = structlog.get_logger("eraif.emergency")
        
        # Performance tracking
        self.performance_metrics = {}
        
    def _setup_structured_logging(self):
        """Setup structured logging configuration."""
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Configure standard logging
        logging.basicConfig(
            level=getattr(logging, self.config.monitoring.log_level.value),
            format='%(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.config.monitoring.log_file_path)
            ]
        )
    
    def log_ai_analysis(
        self,
        case_id: str,
        analysis_type: str,
        processing_time: float,
        confidence: float,
        critical_findings: int,
        success: bool = True,
        error: Optional[str] = None
    ):
        """Log AI analysis event."""
        self.ai_logger.info(
            "AI analysis completed",
            case_id=case_id,
            analysis_type=analysis_type,
            processing_time_seconds=processing_time,
            confidence_score=confidence,
            critical_findings_count=critical_findings,
            success=success,
            error=error,
            timestamp=datetime.now().isoformat()
        )
    
    def log_workflow_execution(
        self,
        workflow_id: str,
        workflow_type: str,
        execution_time: float,
        steps_completed: int,
        decisions_made: int,
        alerts_generated: int,
        success: bool = True,
        error: Optional[str] = None
    ):
        """Log workflow execution event."""
        self.workflow_logger.info(
            "Workflow execution completed",
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            execution_time_seconds=execution_time,
            steps_completed=steps_completed,
            decisions_made=decisions_made,
            alerts_generated=alerts_generated,
            success=success,
            error=error,
            timestamp=datetime.now().isoformat()
        )
    
    def log_emergency_event(
        self,
        event_type: str,
        severity: str,
        affected_patients: int,
        response_time: float,
        resources_mobilized: Dict[str, Any],
        ai_assisted: bool = True
    ):
        """Log emergency event."""
        self.emergency_logger.warning(
            f"Emergency event: {event_type}",
            event_type=event_type,
            severity=severity,
            affected_patients=affected_patients,
            response_time_seconds=response_time,
            resources_mobilized=resources_mobilized,
            ai_assisted=ai_assisted,
            timestamp=datetime.now().isoformat()
        )
    
    def log_critical_finding(
        self,
        case_id: str,
        finding_type: str,
        confidence: float,
        imaging_modality: str,
        alert_sent: bool,
        response_time: Optional[float] = None
    ):
        """Log critical medical finding."""
        self.ai_logger.critical(
            "Critical finding detected",
            case_id=case_id,
            finding_type=finding_type,
            confidence_score=confidence,
            imaging_modality=imaging_modality,
            alert_sent=alert_sent,
            response_time_seconds=response_time,
            requires_immediate_attention=True,
            timestamp=datetime.now().isoformat()
        )
    
    def log_system_performance(
        self,
        component: str,
        cpu_usage: float,
        memory_usage: float,
        gpu_usage: Optional[float] = None,
        active_cases: int = 0,
        queue_length: int = 0
    ):
        """Log system performance metrics."""
        self.system_logger.info(
            "System performance metrics",
            component=component,
            cpu_usage_percent=cpu_usage,
            memory_usage_percent=memory_usage,
            gpu_usage_percent=gpu_usage,
            active_cases=active_cases,
            queue_length=queue_length,
            timestamp=datetime.now().isoformat()
        )
    
    def start_performance_timer(self, operation_id: str) -> str:
        """Start performance timer for an operation."""
        timer_id = f"{operation_id}_{int(time.time() * 1000)}"
        self.performance_metrics[timer_id] = {
            "start_time": time.time(),
            "operation_id": operation_id
        }
        return timer_id
    
    def end_performance_timer(self, timer_id: str) -> float:
        """End performance timer and return duration."""
        if timer_id in self.performance_metrics:
            start_time = self.performance_metrics[timer_id]["start_time"]
            duration = time.time() - start_time
            
            operation_id = self.performance_metrics[timer_id]["operation_id"]
            
            self.system_logger.debug(
                "Operation completed",
                operation_id=operation_id,
                duration_seconds=duration,
                timer_id=timer_id
            )
            
            del self.performance_metrics[timer_id]
            return duration
        
        return 0.0
    
    def log_model_update(
        self,
        model_name: str,
        update_type: str,
        version: str,
        performance_improvement: Optional[float] = None,
        success: bool = True,
        error: Optional[str] = None
    ):
        """Log AI model update event."""
        self.ai_logger.info(
            "AI model updated",
            model_name=model_name,
            update_type=update_type,
            new_version=version,
            performance_improvement_percent=performance_improvement,
            success=success,
            error=error,
            timestamp=datetime.now().isoformat()
        )
    
    def log_resource_optimization(
        self,
        optimization_type: str,
        resources_before: Dict[str, Any],
        resources_after: Dict[str, Any],
        efficiency_gain: float,
        ai_recommendations: int
    ):
        """Log resource optimization event."""
        self.system_logger.info(
            "Resource optimization completed",
            optimization_type=optimization_type,
            resources_before=resources_before,
            resources_after=resources_after,
            efficiency_gain_percent=efficiency_gain,
            ai_recommendations_count=ai_recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    def get_logger(self, component: str) -> structlog.BoundLogger:
        """Get logger for specific component."""
        return structlog.get_logger(f"eraif.{component}")
    
    def export_logs(
        self,
        start_time: datetime,
        end_time: datetime,
        component: Optional[str] = None
    ) -> Dict[str, Any]:
        """Export logs for analysis."""
        # In production, this would query log storage
        # For now, return metadata
        return {
            "export_time": datetime.now().isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "component_filter": component,
            "log_file": self.config.monitoring.log_file_path,
            "format": "structured_json"
        }
