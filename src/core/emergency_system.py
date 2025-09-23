"""
ERAIF Emergency System

Main system orchestrator that integrates AI/ML pipeline with emergency
radiology workflows and interoperability protocols.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
import json

from .config import ERAIFConfig
from .protocol import ERAIFProtocol
from ..ai.pipeline import AIMLPipeline
from ..ai.workflows import EmergencyWorkflow


logger = logging.getLogger(__name__)


class EmergencySystem:
    """
    Main ERAIF Emergency System that coordinates all components.
    
    This system provides:
    - Emergency case processing with AI analysis
    - Resource optimization and allocation
    - Multi-facility coordination
    - Disaster response workflows
    - Real-time monitoring and alerts
    """
    
    def __init__(self, config: ERAIFConfig):
        """Initialize the emergency system."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.protocol = ERAIFProtocol(config)
        self.ai_pipeline = AIMLPipeline(config)
        self.emergency_workflow = EmergencyWorkflow(config)
        
        # System state
        self.system_status = "initializing"
        self.active_cases = {}
        self.system_metrics = {
            "cases_processed": 0,
            "ai_analyses_completed": 0,
            "workflows_executed": 0,
            "alerts_generated": 0,
            "uptime_start": datetime.now()
        }
        
        # Emergency mode tracking
        self.emergency_mode_active = False
        self.emergency_mode_reason = None
        self.emergency_mode_activated_at = None
        
        self.logger.info("ERAIF Emergency System initialized")
        self.system_status = "ready"
    
    async def process_emergency_case(
        self,
        case_data: Dict[str, Any],
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """
        Process a complete emergency case through the AI pipeline.
        
        Args:
            case_data: Emergency case data including patient info, imaging, etc.
            priority: Case priority (low, medium, high, critical)
            
        Returns:
            Complete case analysis with AI insights and recommendations
        """
        case_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Processing emergency case {case_id} with priority {priority}")
            
            # Add case to active cases
            self.active_cases[case_id] = {
                "case_id": case_id,
                "start_time": start_time,
                "priority": priority,
                "status": "processing",
                "data": case_data
            }
            
            # Process through AI pipeline
            ai_results = await self.ai_pipeline.process_emergency(case_data)
            
            # Execute appropriate workflow based on case characteristics
            workflow_type = self._determine_workflow_type(case_data, ai_results)
            workflow_results = await self.emergency_workflow.execute_workflow(
                workflow_type, 
                {**case_data, "ai_results": ai_results}
            )
            
            # Generate final case summary
            case_summary = self._generate_case_summary(
                case_id, case_data, ai_results, workflow_results, start_time
            )
            
            # Update case status
            self.active_cases[case_id]["status"] = "completed"
            self.active_cases[case_id]["results"] = case_summary
            
            # Update metrics
            self.system_metrics["cases_processed"] += 1
            self.system_metrics["ai_analyses_completed"] += 1
            self.system_metrics["workflows_executed"] += 1
            
            # Check for critical findings and generate alerts
            await self._check_critical_findings(case_id, case_summary)
            
            self.logger.info(f"Emergency case {case_id} processed successfully")
            return case_summary
            
        except Exception as e:
            self.logger.error(f"Error processing emergency case {case_id}: {str(e)}")
            
            # Update case status
            if case_id in self.active_cases:
                self.active_cases[case_id]["status"] = "error"
                self.active_cases[case_id]["error"] = str(e)
            
            return {
                "case_id": case_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def activate_emergency_mode(
        self,
        reason: str,
        severity: str = "high",
        estimated_duration_hours: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Activate emergency mode for disaster response.
        
        Args:
            reason: Reason for emergency activation
            severity: Emergency severity (low, medium, high, critical)
            estimated_duration_hours: Estimated duration of emergency
            
        Returns:
            Emergency activation status and configuration
        """
        try:
            self.logger.warning(f"Activating emergency mode: {reason}")
            
            self.emergency_mode_active = True
            self.emergency_mode_reason = reason
            self.emergency_mode_activated_at = datetime.now()
            
            # Adjust system configuration for emergency mode
            emergency_config = self._configure_emergency_mode(severity)
            
            # Execute disaster response workflow
            disaster_workflow_data = {
                "reason": reason,
                "severity": severity,
                "estimated_duration_hours": estimated_duration_hours,
                "activation_time": self.emergency_mode_activated_at.isoformat()
            }
            
            workflow_results = await self.emergency_workflow.execute_workflow(
                "disaster_response",
                disaster_workflow_data
            )
            
            # Generate emergency alerts
            await self._generate_emergency_alerts(reason, severity)
            
            activation_result = {
                "status": "activated",
                "reason": reason,
                "severity": severity,
                "activated_at": self.emergency_mode_activated_at.isoformat(),
                "estimated_duration_hours": estimated_duration_hours,
                "emergency_config": emergency_config,
                "workflow_id": workflow_results.get("workflow_id"),
                "system_adjustments": self._get_emergency_adjustments()
            }
            
            self.logger.info("Emergency mode activated successfully")
            return activation_result
            
        except Exception as e:
            self.logger.error(f"Error activating emergency mode: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def deactivate_emergency_mode(self, resolution_notes: str = "") -> Dict[str, Any]:
        """Deactivate emergency mode and return to normal operations."""
        try:
            if not self.emergency_mode_active:
                return {"status": "not_active", "message": "Emergency mode is not active"}
            
            self.logger.info("Deactivating emergency mode")
            
            # Calculate emergency duration
            duration = datetime.now() - self.emergency_mode_activated_at
            duration_hours = duration.total_seconds() / 3600
            
            # Reset emergency mode flags
            reason = self.emergency_mode_reason
            activated_at = self.emergency_mode_activated_at
            
            self.emergency_mode_active = False
            self.emergency_mode_reason = None
            self.emergency_mode_activated_at = None
            
            # Reset system configuration to normal
            self._configure_normal_mode()
            
            deactivation_result = {
                "status": "deactivated",
                "previous_reason": reason,
                "activated_at": activated_at.isoformat(),
                "deactivated_at": datetime.now().isoformat(),
                "duration_hours": round(duration_hours, 2),
                "resolution_notes": resolution_notes,
                "cases_processed_during_emergency": self._count_emergency_cases(activated_at)
            }
            
            self.logger.info("Emergency mode deactivated successfully")
            return deactivation_result
            
        except Exception as e:
            self.logger.error(f"Error deactivating emergency mode: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            # Get component statuses
            ai_pipeline_status = self.ai_pipeline.get_pipeline_status()
            workflow_status = self.emergency_workflow.get_status()
            
            # Calculate uptime
            uptime = datetime.now() - self.system_metrics["uptime_start"]
            uptime_hours = uptime.total_seconds() / 3600
            
            return {
                "system_status": self.system_status,
                "emergency_mode": {
                    "active": self.emergency_mode_active,
                    "reason": self.emergency_mode_reason,
                    "activated_at": self.emergency_mode_activated_at.isoformat() if self.emergency_mode_activated_at else None
                },
                "active_cases": len(self.active_cases),
                "metrics": {
                    **self.system_metrics,
                    "uptime_hours": round(uptime_hours, 2)
                },
                "components": {
                    "ai_pipeline": ai_pipeline_status,
                    "emergency_workflow": workflow_status,
                    "protocol": "operational"
                },
                "configuration": {
                    "deployment_mode": self.config.deployment_mode.value,
                    "ai_enabled": True,
                    "gpu_enabled": self.config.ai.enable_gpu,
                    "emergency_auto_activation": self.config.emergency.auto_activation_enabled
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            return {
                "system_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_case_status(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific case."""
        return self.active_cases.get(case_id)
    
    async def list_active_cases(self) -> List[Dict[str, Any]]:
        """List all active cases."""
        return [
            {
                "case_id": case_id,
                "priority": case_data["priority"],
                "status": case_data["status"],
                "start_time": case_data["start_time"].isoformat(),
                "processing_duration": (datetime.now() - case_data["start_time"]).total_seconds()
            }
            for case_id, case_data in self.active_cases.items()
            if case_data["status"] in ["processing", "analyzing"]
        ]
    
    async def optimize_resources(
        self,
        facility_data: Dict[str, Any],
        current_demand: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize resource allocation across facilities."""
        try:
            self.logger.info("Optimizing resource allocation")
            
            # Use AI pipeline for resource optimization
            optimization_data = {
                "facility_data": facility_data,
                "current_demand": current_demand,
                "emergency_mode": self.emergency_mode_active
            }
            
            workflow_results = await self.emergency_workflow.execute_workflow(
                "resource_optimization",
                optimization_data
            )
            
            return workflow_results
            
        except Exception as e:
            self.logger.error(f"Error optimizing resources: {str(e)}")
            return {"error": str(e)}
    
    async def coordinate_patient_transfer(
        self,
        patient_data: Dict[str, Any],
        source_facility: str,
        destination_preferences: List[str]
    ) -> Dict[str, Any]:
        """Coordinate patient transfer between facilities."""
        try:
            self.logger.info(f"Coordinating patient transfer from {source_facility}")
            
            transfer_data = {
                "patient_data": patient_data,
                "source_facility": source_facility,
                "destination_preferences": destination_preferences,
                "emergency_mode": self.emergency_mode_active
            }
            
            workflow_results = await self.emergency_workflow.execute_workflow(
                "patient_transfer",
                transfer_data
            )
            
            return workflow_results
            
        except Exception as e:
            self.logger.error(f"Error coordinating patient transfer: {str(e)}")
            return {"error": str(e)}
    
    # Private helper methods
    
    def _determine_workflow_type(
        self,
        case_data: Dict[str, Any],
        ai_results: Dict[str, Any]
    ) -> str:
        """Determine appropriate workflow type based on case characteristics."""
        
        # Check for mass casualty indicators
        if case_data.get("incident_type") == "mass_casualty":
            return "mass_casualty"
        
        # Check for disaster-related cases
        if self.emergency_mode_active:
            return "disaster_response"
        
        # Check for resource optimization needs
        triage_results = ai_results.get("triage_results", {})
        if triage_results.get("priority") in ["critical", "high"]:
            priority_cases = case_data.get("concurrent_priority_cases", 0)
            if priority_cases > 5:  # Threshold for resource optimization
                return "resource_optimization"
        
        # Check for transfer needs
        if case_data.get("requires_transfer", False):
            return "patient_transfer"
        
        # Check for surge capacity needs
        facility_capacity = case_data.get("facility_capacity", {})
        if facility_capacity.get("occupancy_percent", 0) > 85:
            return "surge_capacity"
        
        # Default to resource optimization
        return "resource_optimization"
    
    def _generate_case_summary(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        ai_results: Dict[str, Any],
        workflow_results: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive case summary."""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "case_id": case_id,
            "status": "completed",
            "processing_time_seconds": processing_time,
            "timestamp": datetime.now().isoformat(),
            "patient_info": {
                "patient_id": case_data.get("patient_id"),
                "age": case_data.get("age"),
                "chief_complaint": case_data.get("chief_complaint")
            },
            "ai_analysis": {
                "triage_results": ai_results.get("triage_results", {}),
                "imaging_results": ai_results.get("imaging_results", {}),
                "recommendations": ai_results.get("recommendations", []),
                "confidence_scores": self._extract_confidence_scores(ai_results)
            },
            "workflow_execution": {
                "workflow_type": workflow_results.get("workflow_type"),
                "workflow_id": workflow_results.get("workflow_id"),
                "timeline": workflow_results.get("timeline", []),
                "resource_allocation": workflow_results.get("resource_allocation", {})
            },
            "critical_findings": self._extract_critical_findings(ai_results),
            "next_actions": self._generate_next_actions(ai_results, workflow_results),
            "system_context": {
                "emergency_mode_active": self.emergency_mode_active,
                "system_load": len(self.active_cases)
            }
        }
    
    async def _check_critical_findings(self, case_id: str, case_summary: Dict[str, Any]):
        """Check for critical findings and generate alerts."""
        critical_findings = case_summary.get("critical_findings", [])
        
        for finding in critical_findings:
            confidence = finding.get("confidence", 0.0)
            
            if confidence >= self.config.ai.auto_alert_threshold:
                await self._generate_critical_alert(case_id, finding)
    
    async def _generate_critical_alert(self, case_id: str, finding: Dict[str, Any]):
        """Generate critical finding alert."""
        alert = {
            "alert_id": str(uuid.uuid4()),
            "case_id": case_id,
            "type": "critical_finding",
            "finding": finding,
            "timestamp": datetime.now().isoformat(),
            "requires_immediate_attention": True
        }
        
        self.logger.critical(f"CRITICAL FINDING ALERT: {finding.get('description')} "
                           f"(Confidence: {finding.get('confidence', 0.0):.2f})")
        
        # Here you would integrate with notification systems
        # (email, SMS, Slack, etc.)
        
        self.system_metrics["alerts_generated"] += 1
    
    def _configure_emergency_mode(self, severity: str) -> Dict[str, Any]:
        """Configure system for emergency mode."""
        config = {
            "priority_threshold": "HIGH" if severity in ["high", "critical"] else "MEDIUM",
            "batch_processing": True,
            "compression_enabled": True,
            "timeout_reduced": True,
            "ai_confidence_threshold": 0.6 if severity == "critical" else 0.7
        }
        
        # Apply emergency configuration
        # This would modify system behavior in production
        
        return config
    
    def _configure_normal_mode(self):
        """Reset system to normal mode configuration."""
        # Reset to normal configuration
        pass
    
    async def _generate_emergency_alerts(self, reason: str, severity: str):
        """Generate emergency mode activation alerts."""
        alert = {
            "alert_id": str(uuid.uuid4()),
            "type": "emergency_activation",
            "reason": reason,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "system_status": "emergency_mode_active"
        }
        
        self.logger.warning(f"EMERGENCY MODE ACTIVATED: {reason} (Severity: {severity})")
        self.system_metrics["alerts_generated"] += 1
    
    def _get_emergency_adjustments(self) -> Dict[str, Any]:
        """Get list of system adjustments made for emergency mode."""
        return {
            "ai_processing": "expedited",
            "resource_allocation": "optimized_for_emergency",
            "communication": "high_priority_channels",
            "monitoring": "enhanced_alerting",
            "data_compression": "enabled",
            "offline_capability": "activated"
        }
    
    def _count_emergency_cases(self, since: datetime) -> int:
        """Count cases processed since emergency activation."""
        count = 0
        for case_data in self.active_cases.values():
            if case_data["start_time"] >= since:
                count += 1
        return count
    
    def _extract_confidence_scores(self, ai_results: Dict[str, Any]) -> Dict[str, float]:
        """Extract confidence scores from AI results."""
        scores = {}
        
        triage_results = ai_results.get("triage_results", {})
        if "confidence" in triage_results:
            scores["triage"] = triage_results["confidence"]
        
        imaging_results = ai_results.get("imaging_results", {})
        if "confidence" in imaging_results:
            scores["imaging"] = imaging_results["confidence"]
        
        return scores
    
    def _extract_critical_findings(self, ai_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract critical findings from AI results."""
        critical_findings = []
        
        # Extract from imaging results
        imaging_results = ai_results.get("imaging_results", {})
        for result in imaging_results.get("results", []):
            for finding in result.get("critical_findings", []):
                critical_findings.append({
                    "source": "imaging_analysis",
                    "type": finding.get("type"),
                    "description": finding.get("description", ""),
                    "confidence": finding.get("confidence", 0.0),
                    "severity": finding.get("severity", "unknown")
                })
        
        # Extract from triage results
        triage_results = ai_results.get("triage_results", {})
        for flag in triage_results.get("red_flags", []):
            critical_findings.append({
                "source": "triage_analysis",
                "type": "red_flag",
                "description": flag,
                "confidence": triage_results.get("confidence", 0.0),
                "severity": "high"
            })
        
        return critical_findings
    
    def _generate_next_actions(
        self,
        ai_results: Dict[str, Any],
        workflow_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate recommended next actions."""
        actions = []
        
        # Add AI recommendations
        for rec in ai_results.get("recommendations", []):
            actions.append({
                "source": "ai_analysis",
                "action": rec.get("recommendation"),
                "priority": rec.get("priority", 3),
                "timeframe": rec.get("timeframe", "routine")
            })
        
        # Add workflow actions
        timeline = workflow_results.get("timeline", [])
        for event in timeline:
            if event.get("event_type") == "action_required":
                actions.append({
                    "source": "workflow",
                    "action": event.get("description"),
                    "priority": 2,
                    "timeframe": "immediate"
                })
        
        # Sort by priority
        actions.sort(key=lambda x: x.get("priority", 3))
        
        return actions
