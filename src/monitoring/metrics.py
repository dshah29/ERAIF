"""
Metrics Collection for ERAIF AI/ML Components

Provides comprehensive metrics collection and reporting for AI performance,
system health, and emergency response effectiveness.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import json

from ..core.config import ERAIFConfig


class MetricsCollector:
    """
    Comprehensive metrics collector for ERAIF AI/ML system.
    
    Tracks:
    - AI model performance metrics
    - System resource utilization
    - Emergency response times
    - Workflow execution statistics
    - Critical finding detection rates
    """
    
    def __init__(self, config: ERAIFConfig):
        """Initialize metrics collector."""
        self.config = config
        
        # Metrics storage
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(lambda: deque(maxlen=1000))
        
        # Time-series data (last 24 hours)
        self.time_series = defaultdict(lambda: deque(maxlen=1440))  # 1 minute resolution
        
        # Performance tracking
        self.active_timers = {}
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Start background collection
        self._start_background_collection()
    
    def record_ai_analysis(
        self,
        case_id: str,
        analysis_type: str,
        processing_time: float,
        confidence: float,
        critical_findings: int,
        model_version: str = "1.0.0"
    ):
        """Record AI analysis metrics."""
        with self.lock:
            timestamp = datetime.now()
            
            # Record processing time
            self.histograms[f"ai_analysis_time_{analysis_type}"].append(processing_time)
            
            # Record confidence scores
            self.histograms[f"ai_confidence_{analysis_type}"].append(confidence)
            
            # Update counters
            self.counters[f"ai_analyses_total"] += 1
            self.counters[f"ai_analyses_{analysis_type}"] += 1
            
            if critical_findings > 0:
                self.counters["critical_findings_detected"] += critical_findings
            
            # Time series data
            self.time_series["ai_analyses_per_minute"].append({
                "timestamp": timestamp.isoformat(),
                "count": 1,
                "processing_time": processing_time,
                "confidence": confidence
            })
            
            # Detailed metrics
            self.metrics["ai_analyses"].append({
                "timestamp": timestamp.isoformat(),
                "case_id": case_id,
                "analysis_type": analysis_type,
                "processing_time": processing_time,
                "confidence": confidence,
                "critical_findings": critical_findings,
                "model_version": model_version
            })
    
    def record_workflow_execution(
        self,
        workflow_id: str,
        workflow_type: str,
        execution_time: float,
        steps_completed: int,
        decisions_made: int,
        success: bool = True
    ):
        """Record workflow execution metrics."""
        with self.lock:
            timestamp = datetime.now()
            
            # Record execution time
            self.histograms[f"workflow_time_{workflow_type}"].append(execution_time)
            
            # Update counters
            self.counters["workflows_executed"] += 1
            self.counters[f"workflows_{workflow_type}"] += 1
            self.counters["workflow_decisions_made"] += decisions_made
            
            if success:
                self.counters["workflows_successful"] += 1
            else:
                self.counters["workflows_failed"] += 1
            
            # Time series
            self.time_series["workflows_per_minute"].append({
                "timestamp": timestamp.isoformat(),
                "workflow_type": workflow_type,
                "execution_time": execution_time,
                "success": success
            })
            
            # Detailed metrics
            self.metrics["workflow_executions"].append({
                "timestamp": timestamp.isoformat(),
                "workflow_id": workflow_id,
                "workflow_type": workflow_type,
                "execution_time": execution_time,
                "steps_completed": steps_completed,
                "decisions_made": decisions_made,
                "success": success
            })
    
    def record_emergency_response(
        self,
        event_type: str,
        severity: str,
        response_time: float,
        patients_affected: int,
        ai_assisted: bool = True
    ):
        """Record emergency response metrics."""
        with self.lock:
            timestamp = datetime.now()
            
            # Record response time
            self.histograms[f"emergency_response_time_{severity}"].append(response_time)
            
            # Update counters
            self.counters["emergency_events"] += 1
            self.counters[f"emergency_{severity}"] += 1
            self.counters["patients_affected"] += patients_affected
            
            if ai_assisted:
                self.counters["ai_assisted_emergencies"] += 1
            
            # Time series
            self.time_series["emergency_events_per_hour"].append({
                "timestamp": timestamp.isoformat(),
                "event_type": event_type,
                "severity": severity,
                "response_time": response_time,
                "patients_affected": patients_affected
            })
    
    def record_system_performance(
        self,
        component: str,
        cpu_usage: float,
        memory_usage: float,
        gpu_usage: Optional[float] = None,
        active_cases: int = 0
    ):
        """Record system performance metrics."""
        with self.lock:
            timestamp = datetime.now()
            
            # Update gauges
            self.gauges[f"cpu_usage_{component}"] = cpu_usage
            self.gauges[f"memory_usage_{component}"] = memory_usage
            self.gauges[f"active_cases_{component}"] = active_cases
            
            if gpu_usage is not None:
                self.gauges[f"gpu_usage_{component}"] = gpu_usage
            
            # Time series
            self.time_series[f"system_performance_{component}"].append({
                "timestamp": timestamp.isoformat(),
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "gpu_usage": gpu_usage,
                "active_cases": active_cases
            })
    
    def record_critical_finding(
        self,
        finding_type: str,
        confidence: float,
        response_time: Optional[float] = None,
        alert_sent: bool = True
    ):
        """Record critical finding metrics."""
        with self.lock:
            timestamp = datetime.now()
            
            # Update counters
            self.counters["critical_findings_total"] += 1
            self.counters[f"critical_findings_{finding_type}"] += 1
            
            if alert_sent:
                self.counters["critical_alerts_sent"] += 1
            
            if response_time is not None:
                self.histograms["critical_finding_response_time"].append(response_time)
            
            # Time series
            self.time_series["critical_findings_per_hour"].append({
                "timestamp": timestamp.isoformat(),
                "finding_type": finding_type,
                "confidence": confidence,
                "response_time": response_time,
                "alert_sent": alert_sent
            })
    
    def start_timer(self, operation_name: str) -> str:
        """Start a performance timer."""
        timer_id = f"{operation_name}_{int(time.time() * 1000)}"
        self.active_timers[timer_id] = {
            "operation": operation_name,
            "start_time": time.time()
        }
        return timer_id
    
    def end_timer(self, timer_id: str) -> float:
        """End a performance timer and record the duration."""
        if timer_id in self.active_timers:
            timer_data = self.active_timers[timer_id]
            duration = time.time() - timer_data["start_time"]
            operation = timer_data["operation"]
            
            # Record the timing
            with self.lock:
                self.histograms[f"operation_time_{operation}"].append(duration)
            
            del self.active_timers[timer_id]
            return duration
        
        return 0.0
    
    def get_summary_metrics(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        with self.lock:
            current_time = datetime.now()
            
            # Calculate rates
            ai_analysis_rate = self._calculate_rate("ai_analyses_total", timedelta(minutes=5))
            workflow_rate = self._calculate_rate("workflows_executed", timedelta(minutes=5))
            
            # Calculate averages
            avg_ai_processing_time = self._calculate_average("ai_analysis_time_total")
            avg_workflow_time = self._calculate_average("workflow_time_total")
            
            # Calculate success rates
            workflow_success_rate = self._calculate_success_rate(
                "workflows_successful", "workflows_executed"
            )
            
            return {
                "timestamp": current_time.isoformat(),
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "rates": {
                    "ai_analyses_per_minute": ai_analysis_rate,
                    "workflows_per_minute": workflow_rate
                },
                "averages": {
                    "ai_processing_time_seconds": avg_ai_processing_time,
                    "workflow_execution_time_seconds": avg_workflow_time
                },
                "success_rates": {
                    "workflow_success_rate": workflow_success_rate
                },
                "system_health": self._calculate_system_health()
            }
    
    def get_time_series_data(
        self,
        metric_name: str,
        duration: timedelta = timedelta(hours=1)
    ) -> List[Dict[str, Any]]:
        """Get time series data for a specific metric."""
        with self.lock:
            if metric_name not in self.time_series:
                return []
            
            cutoff_time = datetime.now() - duration
            
            # Filter data within the time range
            filtered_data = []
            for data_point in self.time_series[metric_name]:
                timestamp = datetime.fromisoformat(data_point["timestamp"])
                if timestamp >= cutoff_time:
                    filtered_data.append(data_point)
            
            return filtered_data
    
    def get_performance_percentiles(
        self,
        operation: str,
        percentiles: List[float] = [50, 90, 95, 99]
    ) -> Dict[str, float]:
        """Get performance percentiles for an operation."""
        with self.lock:
            histogram_key = f"operation_time_{operation}"
            
            if histogram_key not in self.histograms:
                return {}
            
            data = sorted(list(self.histograms[histogram_key]))
            
            if not data:
                return {}
            
            result = {}
            for percentile in percentiles:
                index = int((percentile / 100.0) * len(data))
                if index >= len(data):
                    index = len(data) - 1
                result[f"p{percentile}"] = data[index]
            
            return result
    
    def export_metrics(
        self,
        format_type: str = "json",
        time_range: Optional[timedelta] = None
    ) -> str:
        """Export metrics in specified format."""
        with self.lock:
            if time_range is None:
                time_range = timedelta(hours=24)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "time_range_hours": time_range.total_seconds() / 3600,
                "summary": self.get_summary_metrics(),
                "time_series": {}
            }
            
            # Export time series data
            for metric_name in self.time_series.keys():
                export_data["time_series"][metric_name] = self.get_time_series_data(
                    metric_name, time_range
                )
            
            if format_type == "json":
                return json.dumps(export_data, indent=2)
            else:
                # Could add other formats like CSV, Prometheus, etc.
                return json.dumps(export_data, indent=2)
    
    def _calculate_rate(self, counter_name: str, time_window: timedelta) -> float:
        """Calculate rate for a counter over a time window."""
        if counter_name not in self.counters:
            return 0.0
        
        # For simplicity, return current count / time window in minutes
        # In production, this would use proper time-based calculations
        window_minutes = time_window.total_seconds() / 60
        return self.counters[counter_name] / max(window_minutes, 1)
    
    def _calculate_average(self, histogram_name: str) -> float:
        """Calculate average from histogram data."""
        if histogram_name not in self.histograms:
            return 0.0
        
        data = list(self.histograms[histogram_name])
        if not data:
            return 0.0
        
        return sum(data) / len(data)
    
    def _calculate_success_rate(self, success_counter: str, total_counter: str) -> float:
        """Calculate success rate percentage."""
        total = self.counters.get(total_counter, 0)
        if total == 0:
            return 0.0
        
        successful = self.counters.get(success_counter, 0)
        return (successful / total) * 100.0
    
    def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate overall system health score."""
        # Simple health calculation based on various factors
        health_factors = []
        
        # AI processing performance
        avg_ai_time = self._calculate_average("ai_analysis_time_total")
        if avg_ai_time > 0:
            ai_health = max(0, 100 - (avg_ai_time * 10))  # Penalize slow processing
            health_factors.append(ai_health)
        
        # Workflow success rate
        workflow_success = self._calculate_success_rate("workflows_successful", "workflows_executed")
        health_factors.append(workflow_success)
        
        # System resource utilization (assume reasonable if no data)
        cpu_health = 100 - max(0, max(self.gauges.get(k, 0) for k in self.gauges if 'cpu_usage' in k) - 80)
        memory_health = 100 - max(0, max(self.gauges.get(k, 0) for k in self.gauges if 'memory_usage' in k) - 85)
        
        health_factors.extend([cpu_health, memory_health])
        
        overall_health = sum(health_factors) / len(health_factors) if health_factors else 100
        
        return {
            "overall_score": round(overall_health, 2),
            "status": "healthy" if overall_health >= 80 else "degraded" if overall_health >= 60 else "unhealthy",
            "factors": {
                "ai_performance": health_factors[0] if health_factors else 100,
                "workflow_reliability": health_factors[1] if len(health_factors) > 1 else 100,
                "system_resources": (cpu_health + memory_health) / 2
            }
        }
    
    def _start_background_collection(self):
        """Start background metrics collection."""
        # In production, this would start background threads for
        # system metrics collection, log parsing, etc.
        pass
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)."""
        with self.lock:
            self.metrics.clear()
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            self.time_series.clear()
            self.active_timers.clear()
