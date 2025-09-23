"""
AI Agents for ERAIF Emergency System

This module contains specialized AI agents for different aspects of emergency
radiology and medical response coordination.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import uuid
from abc import ABC, abstractmethod

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from ..core.config import ERAIFConfig


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all ERAIF AI agents."""
    
    def __init__(self, config: ERAIFConfig, llm: ChatOpenAI, agent_name: str):
        """Initialize base agent."""
        self.config = config
        self.llm = llm
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")
        self.status = "initialized"
        self.metrics = {"requests_processed": 0, "errors": 0}
    
    async def update_config(self, new_config: Dict[str, Any]):
        """Update agent configuration."""
        # Override in subclasses as needed
        self.logger.info(f"Configuration updated for {self.agent_name}")
    
    def get_status(self) -> str:
        """Get current agent status."""
        return self.status
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        return self.metrics.copy()
    
    def _update_metrics(self, success: bool = True):
        """Update agent metrics."""
        self.metrics["requests_processed"] += 1
        if not success:
            self.metrics["errors"] += 1


class EmergencyAIAgent(BaseAgent):
    """
    Main emergency coordination AI agent.
    
    Handles overall emergency response coordination, clinical decision support,
    and integration with other specialized agents.
    """
    
    def __init__(self, config: ERAIFConfig, llm: ChatOpenAI):
        """Initialize emergency AI agent."""
        super().__init__(config, llm, "emergency")
        
        self.system_prompt = """
        You are an expert emergency medicine AI assistant specializing in radiology and emergency response coordination.
        
        Your responsibilities include:
        - Analyzing emergency medical situations
        - Providing clinical decision support
        - Coordinating with multiple healthcare facilities
        - Optimizing resource allocation during disasters
        - Ensuring patient safety and optimal outcomes
        
        Always prioritize patient safety and follow evidence-based medical guidelines.
        Provide clear, actionable recommendations with confidence levels.
        Consider resource constraints and emergency protocols.
        """
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="chat_history", optional=True)
        ])
        
        self.json_parser = JsonOutputParser()
        self.status = "ready"
    
    async def extract_emergency_data(self, raw_text: str) -> Dict[str, Any]:
        """Extract structured data from raw emergency text."""
        try:
            prompt = f"""
            Extract structured emergency medical data from the following text:
            
            {raw_text}
            
            Return a JSON object with the following fields:
            - patient_id: Patient identifier
            - chief_complaint: Primary complaint or reason for visit
            - vital_signs: Dictionary of vital signs if mentioned
            - symptoms: List of symptoms
            - medical_history: Relevant medical history
            - medications: Current medications
            - allergies: Known allergies
            - severity: Estimated severity (low/medium/high/critical)
            - urgent_flags: List of urgent medical flags
            
            If information is not available, use null for that field.
            """
            
            messages = [HumanMessage(content=prompt)]
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            try:
                extracted_data = json.loads(response.content)
                self._update_metrics(success=True)
                return extracted_data
            except json.JSONDecodeError:
                # Fallback to basic extraction
                self.logger.warning("Failed to parse JSON response, using fallback")
                return {"raw_text": raw_text, "extraction_error": True}
                
        except Exception as e:
            self.logger.error(f"Error extracting emergency data: {str(e)}")
            self._update_metrics(success=False)
            return {"error": str(e)}
    
    async def generate_clinical_recommendations(
        self,
        emergency_data: Dict[str, Any],
        triage_results: Dict[str, Any],
        imaging_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate clinical recommendations based on all available data."""
        try:
            context = {
                "emergency_data": emergency_data,
                "triage_results": triage_results,
                "imaging_results": imaging_results
            }
            
            prompt = f"""
            Based on the following emergency medical information, provide clinical recommendations:
            
            {json.dumps(context, indent=2)}
            
            Generate a list of clinical recommendations, each with:
            - recommendation: The specific recommendation
            - priority: Priority level (1-5, 1 being highest)
            - rationale: Medical reasoning behind the recommendation
            - timeframe: Recommended timeframe for action
            - confidence: Confidence level (0-1)
            - category: Category (diagnostic, therapeutic, monitoring, etc.)
            
            Return as a JSON array of recommendation objects.
            """
            
            messages = [HumanMessage(content=prompt)]
            response = await self.llm.ainvoke(messages)
            
            try:
                recommendations = json.loads(response.content)
                self._update_metrics(success=True)
                return recommendations if isinstance(recommendations, list) else [recommendations]
            except json.JSONDecodeError:
                # Return a fallback recommendation
                return [{
                    "recommendation": "Comprehensive clinical assessment needed",
                    "priority": 3,
                    "rationale": "Insufficient data for specific recommendations",
                    "timeframe": "immediate",
                    "confidence": 0.5,
                    "category": "assessment"
                }]
                
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            self._update_metrics(success=False)
            return []
    
    async def create_coordination_plan(
        self,
        emergency_data: Dict[str, Any],
        triage_results: Dict[str, Any],
        imaging_results: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create emergency coordination plan."""
        try:
            context = {
                "emergency_data": emergency_data,
                "triage_results": triage_results,
                "imaging_results": imaging_results,
                "recommendations": recommendations
            }
            
            prompt = f"""
            Create an emergency coordination plan based on:
            
            {json.dumps(context, indent=2)}
            
            Generate a coordination plan with:
            - action_items: List of specific actions needed
            - resource_requirements: Resources needed
            - timeline: Timeline for each action
            - responsible_parties: Who should handle each action
            - communication_plan: How to communicate updates
            - escalation_triggers: When to escalate
            - success_metrics: How to measure success
            
            Return as a JSON object.
            """
            
            messages = [HumanMessage(content=prompt)]
            response = await self.llm.ainvoke(messages)
            
            try:
                plan = json.loads(response.content)
                self._update_metrics(success=True)
                return plan
            except json.JSONDecodeError:
                return {"error": "Failed to parse coordination plan"}
                
        except Exception as e:
            self.logger.error(f"Error creating coordination plan: {str(e)}")
            self._update_metrics(success=False)
            return {"error": str(e)}


class TriageAgent(BaseAgent):
    """
    AI agent specialized in emergency triage and prioritization.
    """
    
    def __init__(self, config: ERAIFConfig, llm: ChatOpenAI):
        """Initialize triage agent."""
        super().__init__(config, llm, "triage")
        
        self.triage_categories = {
            "immediate": {"code": "red", "priority": 1, "max_wait_time": 0},
            "urgent": {"code": "yellow", "priority": 2, "max_wait_time": 30},
            "less_urgent": {"code": "green", "priority": 3, "max_wait_time": 120},
            "non_urgent": {"code": "blue", "priority": 4, "max_wait_time": 240}
        }
        
        self.system_prompt = """
        You are an expert emergency triage nurse with advanced training in emergency medicine.
        
        Use the Emergency Severity Index (ESI) and clinical judgment to:
        - Assess patient acuity and urgency
        - Determine appropriate triage category
        - Identify life-threatening conditions
        - Recommend immediate interventions
        
        Consider:
        - Vital signs and their stability
        - Level of consciousness
        - Severity of pain
        - Mechanism of injury
        - Medical history and risk factors
        
        Always err on the side of caution for patient safety.
        """
        
        self.status = "ready"
    
    async def analyze_emergency(self, emergency_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform triage analysis on emergency case."""
        try:
            prompt = f"""
            Perform emergency triage analysis on this patient:
            
            {json.dumps(emergency_data, indent=2)}
            
            Provide triage assessment with:
            - priority: immediate/urgent/less_urgent/non_urgent
            - esi_level: Emergency Severity Index level (1-5)
            - acuity_score: Numerical acuity score (1-10, 10 being most acute)
            - max_wait_time: Maximum safe wait time in minutes
            - red_flags: List of concerning findings
            - immediate_interventions: List of immediate actions needed
            - rationale: Detailed reasoning for triage decision
            - confidence: Confidence in assessment (0-1)
            
            Return as JSON object.
            """
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            try:
                triage_result = json.loads(response.content)
                
                # Validate and enhance result
                if "priority" in triage_result:
                    priority = triage_result["priority"]
                    if priority in self.triage_categories:
                        triage_result.update(self.triage_categories[priority])
                
                self._update_metrics(success=True)
                return triage_result
                
            except json.JSONDecodeError:
                # Return safe default
                return {
                    "priority": "urgent",
                    "esi_level": 2,
                    "acuity_score": 7,
                    "max_wait_time": 30,
                    "red_flags": ["Unable to complete full assessment"],
                    "confidence": 0.3,
                    "error": "JSON parsing failed"
                }
                
        except Exception as e:
            self.logger.error(f"Error in triage analysis: {str(e)}")
            self._update_metrics(success=False)
            return {
                "priority": "urgent",
                "error": str(e),
                "confidence": 0.0
            }


class ImagingAnalysisAgent(BaseAgent):
    """
    AI agent specialized in medical imaging analysis and interpretation.
    """
    
    def __init__(self, config: ERAIFConfig, llm: ChatOpenAI):
        """Initialize imaging analysis agent."""
        super().__init__(config, llm, "imaging")
        
        self.supported_modalities = [
            "CT", "MRI", "X-Ray", "Ultrasound", "Nuclear Medicine", "PET", "SPECT"
        ]
        
        self.system_prompt = """
        You are an expert radiologist with subspecialty training in emergency radiology.
        
        Your expertise includes:
        - Trauma imaging interpretation
        - Emergency CT and MRI analysis
        - Critical findings detection
        - Urgent vs non-urgent finding prioritization
        - Communication of critical results
        
        Focus on:
        - Life-threatening findings first
        - Clear, concise reporting
        - Appropriate urgency levels
        - Recommendations for further imaging or clinical correlation
        """
        
        self.status = "ready"
    
    async def analyze_study(self, study_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a medical imaging study."""
        try:
            prompt = f"""
            Analyze this medical imaging study:
            
            {json.dumps(study_data, indent=2)}
            
            Provide imaging analysis with:
            - modality: Type of imaging study
            - study_quality: Quality assessment (excellent/good/fair/poor)
            - critical_findings: List of critical/urgent findings
            - significant_findings: List of significant but non-critical findings
            - incidental_findings: List of incidental findings
            - impression: Overall radiological impression
            - recommendations: Recommended follow-up or additional imaging
            - urgency_level: critical/urgent/routine
            - confidence: Confidence in interpretation (0-1)
            - limitations: Any limitations in the study or interpretation
            
            Return as JSON object.
            """
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            try:
                analysis_result = json.loads(response.content)
                self._update_metrics(success=True)
                return analysis_result
                
            except json.JSONDecodeError:
                return {
                    "error": "Failed to parse imaging analysis",
                    "modality": study_data.get("modality", "unknown"),
                    "urgency_level": "routine",
                    "confidence": 0.0
                }
                
        except Exception as e:
            self.logger.error(f"Error in imaging analysis: {str(e)}")
            self._update_metrics(success=False)
            return {
                "error": str(e),
                "urgency_level": "routine",
                "confidence": 0.0
            }
    
    async def compare_studies(
        self,
        current_study: Dict[str, Any],
        prior_studies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare current study with prior studies."""
        try:
            context = {
                "current_study": current_study,
                "prior_studies": prior_studies
            }
            
            prompt = f"""
            Compare the current imaging study with prior studies:
            
            {json.dumps(context, indent=2)}
            
            Provide comparison analysis with:
            - interval_changes: List of changes since prior studies
            - progression: Whether findings are progressing, stable, or improving
            - new_findings: New findings not present in prior studies
            - resolved_findings: Findings that have resolved
            - comparison_limitations: Any limitations in comparison
            - clinical_significance: Clinical significance of changes
            - recommendations: Recommended actions based on changes
            
            Return as JSON object.
            """
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            try:
                comparison_result = json.loads(response.content)
                self._update_metrics(success=True)
                return comparison_result
                
            except json.JSONDecodeError:
                return {"error": "Failed to parse comparison analysis"}
                
        except Exception as e:
            self.logger.error(f"Error in study comparison: {str(e)}")
            self._update_metrics(success=False)
            return {"error": str(e)}


class ResourceOptimizationAgent(BaseAgent):
    """
    AI agent specialized in resource optimization during emergencies.
    """
    
    def __init__(self, config: ERAIFConfig, llm: ChatOpenAI):
        """Initialize resource optimization agent."""
        super().__init__(config, llm, "resource_optimization")
        
        self.resource_types = [
            "beds", "ventilators", "imaging_equipment", "staff", 
            "medications", "blood_products", "surgical_suites"
        ]
        
        self.system_prompt = """
        You are an expert in healthcare operations and emergency resource management.
        
        Your expertise includes:
        - Hospital capacity planning
        - Resource allocation optimization
        - Emergency surge planning
        - Staff scheduling and deployment
        - Equipment utilization optimization
        
        Consider:
        - Patient acuity and needs
        - Resource availability and constraints
        - Staff capabilities and limitations
        - Equipment maintenance and availability
        - Surge capacity requirements
        """
        
        self.status = "ready"
    
    async def optimize_allocation(
        self,
        current_demand: Dict[str, Any],
        available_resources: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize resource allocation based on current demand and availability."""
        try:
            context = {
                "demand": current_demand,
                "resources": available_resources,
                "constraints": constraints
            }
            
            prompt = f"""
            Optimize resource allocation for emergency situation:
            
            {json.dumps(context, indent=2)}
            
            Provide optimization plan with:
            - allocation_plan: Detailed resource allocation
            - priority_queue: Patient priority queue
            - staff_assignments: Staff deployment plan
            - equipment_schedule: Equipment utilization schedule
            - overflow_plan: Plan for surge capacity
            - efficiency_metrics: Expected efficiency gains
            - risk_assessment: Risks and mitigation strategies
            - alternative_scenarios: Alternative allocation scenarios
            
            Return as JSON object.
            """
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            try:
                optimization_result = json.loads(response.content)
                self._update_metrics(success=True)
                return optimization_result
                
            except json.JSONDecodeError:
                return {"error": "Failed to parse optimization plan"}
                
        except Exception as e:
            self.logger.error(f"Error in resource optimization: {str(e)}")
            self._update_metrics(success=False)
            return {"error": str(e)}
