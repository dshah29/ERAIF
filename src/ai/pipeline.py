"""
AI/ML Pipeline for ERAIF using LangGraph

This module implements the main AI/ML pipeline that orchestrates various
AI agents and models for emergency radiology analysis.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
import json
import uuid

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from ..core.config import ERAIFConfig
from .models import MedicalImagingModel
from .agents import EmergencyAIAgent, TriageAgent, ImagingAnalysisAgent
from .workflows import EmergencyWorkflow


logger = logging.getLogger(__name__)


@dataclass
class PipelineState:
    """State management for the AI/ML pipeline."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[BaseMessage] = field(default_factory=list)
    current_step: str = "initial"
    emergency_data: Dict[str, Any] = field(default_factory=dict)
    imaging_results: Dict[str, Any] = field(default_factory=dict)
    triage_results: Dict[str, Any] = field(default_factory=dict)
    ai_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    workflow_status: str = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "messages": [msg.dict() if hasattr(msg, 'dict') else str(msg) for msg in self.messages],
            "current_step": self.current_step,
            "emergency_data": self.emergency_data,
            "imaging_results": self.imaging_results,
            "triage_results": self.triage_results,
            "ai_recommendations": self.ai_recommendations,
            "workflow_status": self.workflow_status,
            "metadata": self.metadata
        }


class AIMLPipeline:
    """
    Main AI/ML Pipeline using LangGraph for orchestrating emergency radiology workflows.
    
    This pipeline coordinates multiple AI agents and models to provide:
    - Medical imaging analysis
    - Emergency triage support
    - Clinical decision support
    - Resource optimization
    - Predictive analytics
    """
    
    def __init__(self, config: ERAIFConfig):
        """Initialize the AI/ML pipeline."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=config.openai_api_key
        )
        
        # Initialize components
        self.medical_imaging_model = MedicalImagingModel(config)
        self.emergency_agent = EmergencyAIAgent(config, self.llm)
        self.triage_agent = TriageAgent(config, self.llm)
        self.imaging_agent = ImagingAnalysisAgent(config, self.llm)
        self.workflow = EmergencyWorkflow(config)
        
        # Initialize LangGraph
        self.graph = self._build_graph()
        self.checkpointer = MemorySaver()
        
        self.logger.info("AI/ML Pipeline initialized successfully")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for emergency processing."""
        
        # Define the graph
        workflow = StateGraph(PipelineState)
        
        # Add nodes
        workflow.add_node("intake", self._intake_node)
        workflow.add_node("triage", self._triage_node)
        workflow.add_node("imaging_analysis", self._imaging_analysis_node)
        workflow.add_node("clinical_decision", self._clinical_decision_node)
        workflow.add_node("resource_optimization", self._resource_optimization_node)
        workflow.add_node("emergency_coordination", self._emergency_coordination_node)
        workflow.add_node("monitoring", self._monitoring_node)
        
        # Define edges
        workflow.set_entry_point("intake")
        
        workflow.add_edge("intake", "triage")
        workflow.add_conditional_edges(
            "triage",
            self._triage_router,
            {
                "critical": "imaging_analysis",
                "urgent": "imaging_analysis", 
                "routine": "clinical_decision",
                "monitoring": "monitoring"
            }
        )
        
        workflow.add_edge("imaging_analysis", "clinical_decision")
        workflow.add_edge("clinical_decision", "resource_optimization")
        workflow.add_edge("resource_optimization", "emergency_coordination")
        workflow.add_edge("emergency_coordination", END)
        workflow.add_edge("monitoring", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _intake_node(self, state: PipelineState) -> PipelineState:
        """Initial intake and data validation node."""
        self.logger.info(f"Processing intake for session {state.session_id}")
        
        # Validate and process incoming emergency data
        emergency_data = state.emergency_data
        
        # Add structured data extraction
        if "raw_text" in emergency_data:
            extracted_data = await self.emergency_agent.extract_emergency_data(
                emergency_data["raw_text"]
            )
            state.emergency_data.update(extracted_data)
        
        # Add metadata
        state.metadata.update({
            "intake_timestamp": datetime.now().isoformat(),
            "data_quality_score": self._calculate_data_quality(emergency_data),
            "processing_priority": self._determine_priority(emergency_data)
        })
        
        state.current_step = "intake_complete"
        state.messages.append(AIMessage(content="Emergency data intake completed"))
        
        return state
    
    async def _triage_node(self, state: PipelineState) -> PipelineState:
        """AI-powered triage node."""
        self.logger.info("Performing AI triage analysis")
        
        # Perform triage analysis
        triage_result = await self.triage_agent.analyze_emergency(
            state.emergency_data
        )
        
        state.triage_results = triage_result
        state.current_step = "triage_complete"
        
        # Add triage message
        priority = triage_result.get("priority", "unknown")
        confidence = triage_result.get("confidence", 0)
        
        state.messages.append(AIMessage(
            content=f"Triage completed: Priority {priority} (confidence: {confidence:.2f})"
        ))
        
        return state
    
    async def _imaging_analysis_node(self, state: PipelineState) -> PipelineState:
        """Medical imaging analysis node."""
        self.logger.info("Performing medical imaging analysis")
        
        # Analyze medical images if available
        imaging_data = state.emergency_data.get("imaging_studies", [])
        
        if imaging_data:
            analysis_results = []
            
            for study in imaging_data:
                result = await self.imaging_agent.analyze_study(study)
                analysis_results.append(result)
            
            state.imaging_results = {
                "studies_analyzed": len(imaging_data),
                "results": analysis_results,
                "summary": await self._summarize_imaging_results(analysis_results)
            }
        else:
            state.imaging_results = {
                "studies_analyzed": 0,
                "results": [],
                "summary": "No imaging studies available for analysis"
            }
        
        state.current_step = "imaging_analysis_complete"
        state.messages.append(AIMessage(
            content=f"Imaging analysis completed for {len(imaging_data)} studies"
        ))
        
        return state
    
    async def _clinical_decision_node(self, state: PipelineState) -> PipelineState:
        """Clinical decision support node."""
        self.logger.info("Generating clinical decision support")
        
        # Generate clinical recommendations
        recommendations = await self.emergency_agent.generate_clinical_recommendations(
            emergency_data=state.emergency_data,
            triage_results=state.triage_results,
            imaging_results=state.imaging_results
        )
        
        state.ai_recommendations = recommendations
        state.current_step = "clinical_decision_complete"
        
        state.messages.append(AIMessage(
            content=f"Generated {len(recommendations)} clinical recommendations"
        ))
        
        return state
    
    async def _resource_optimization_node(self, state: PipelineState) -> PipelineState:
        """Resource optimization and allocation node."""
        self.logger.info("Optimizing resource allocation")
        
        # Optimize resource allocation based on triage and clinical decisions
        resource_plan = await self.workflow.optimize_resources(
            triage_results=state.triage_results,
            recommendations=state.ai_recommendations,
            current_capacity=state.emergency_data.get("facility_capacity", {})
        )
        
        state.metadata["resource_optimization"] = resource_plan
        state.current_step = "resource_optimization_complete"
        
        state.messages.append(AIMessage(
            content="Resource optimization completed"
        ))
        
        return state
    
    async def _emergency_coordination_node(self, state: PipelineState) -> PipelineState:
        """Emergency coordination and communication node."""
        self.logger.info("Coordinating emergency response")
        
        # Generate coordination plan
        coordination_plan = await self.emergency_agent.create_coordination_plan(
            emergency_data=state.emergency_data,
            triage_results=state.triage_results,
            imaging_results=state.imaging_results,
            recommendations=state.ai_recommendations
        )
        
        state.metadata["coordination_plan"] = coordination_plan
        state.current_step = "emergency_coordination_complete"
        state.workflow_status = "completed"
        
        state.messages.append(AIMessage(
            content="Emergency coordination plan generated and distributed"
        ))
        
        return state
    
    async def _monitoring_node(self, state: PipelineState) -> PipelineState:
        """Continuous monitoring node for routine cases."""
        self.logger.info("Setting up continuous monitoring")
        
        # Set up monitoring parameters
        monitoring_config = {
            "check_interval_minutes": 15,
            "escalation_triggers": ["vital_sign_changes", "symptom_progression"],
            "alert_threshold": 0.8
        }
        
        state.metadata["monitoring_config"] = monitoring_config
        state.current_step = "monitoring_active"
        state.workflow_status = "monitoring"
        
        state.messages.append(AIMessage(
            content="Continuous monitoring activated for routine case"
        ))
        
        return state
    
    def _triage_router(self, state: PipelineState) -> str:
        """Route based on triage results."""
        priority = state.triage_results.get("priority", "routine")
        
        if priority in ["critical", "life_threatening"]:
            return "critical"
        elif priority in ["urgent", "high"]:
            return "urgent"
        elif priority in ["routine", "normal"]:
            return "routine"
        else:
            return "monitoring"
    
    def _calculate_data_quality(self, data: Dict[str, Any]) -> float:
        """Calculate data quality score (0-1)."""
        required_fields = ["patient_id", "chief_complaint", "vital_signs"]
        score = 0.0
        
        for field in required_fields:
            if field in data and data[field]:
                score += 1.0 / len(required_fields)
        
        return score
    
    def _determine_priority(self, data: Dict[str, Any]) -> str:
        """Determine processing priority based on emergency data."""
        # Simple priority determination logic
        keywords = data.get("chief_complaint", "").lower()
        
        if any(word in keywords for word in ["cardiac", "stroke", "trauma", "respiratory"]):
            return "high"
        elif any(word in keywords for word in ["pain", "fever", "nausea"]):
            return "medium"
        else:
            return "low"
    
    async def _summarize_imaging_results(self, results: List[Dict[str, Any]]) -> str:
        """Summarize imaging analysis results."""
        if not results:
            return "No imaging studies analyzed"
        
        # Use LLM to generate summary
        results_text = json.dumps(results, indent=2)
        
        messages = [
            HumanMessage(content=f"""
            Please provide a concise clinical summary of these medical imaging analysis results:
            
            {results_text}
            
            Focus on:
            - Key findings
            - Clinical significance
            - Recommended actions
            """)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    async def process_emergency(self, emergency_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an emergency case through the AI/ML pipeline.
        
        Args:
            emergency_data: Emergency case data including patient info, symptoms, imaging, etc.
            
        Returns:
            Complete analysis results and recommendations
        """
        # Create initial state
        initial_state = PipelineState(
            emergency_data=emergency_data,
            messages=[HumanMessage(content="New emergency case received")]
        )
        
        # Configure the run
        config = RunnableConfig(
            configurable={"thread_id": initial_state.session_id}
        )
        
        try:
            # Execute the workflow
            final_state = await self.graph.ainvoke(initial_state, config=config)
            
            # Return comprehensive results
            return {
                "session_id": final_state.session_id,
                "status": final_state.workflow_status,
                "triage_results": final_state.triage_results,
                "imaging_results": final_state.imaging_results,
                "recommendations": final_state.ai_recommendations,
                "metadata": final_state.metadata,
                "processing_steps": [msg.content for msg in final_state.messages]
            }
            
        except Exception as e:
            self.logger.error(f"Error processing emergency: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "session_id": initial_state.session_id
            }
    
    async def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get processing history for a session."""
        try:
            # Retrieve session state from checkpointer
            config = RunnableConfig(configurable={"thread_id": session_id})
            
            # This would typically retrieve from persistent storage
            # For now, return empty list as checkpointer is in-memory
            return []
            
        except Exception as e:
            self.logger.error(f"Error retrieving session history: {str(e)}")
            return []
    
    async def update_models(self, model_updates: Dict[str, Any]) -> bool:
        """Update AI models with new training data or configurations."""
        try:
            # Update medical imaging model
            if "imaging_model" in model_updates:
                await self.medical_imaging_model.update_model(
                    model_updates["imaging_model"]
                )
            
            # Update agent configurations
            if "agent_configs" in model_updates:
                await self._update_agent_configs(model_updates["agent_configs"])
            
            self.logger.info("Models updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating models: {str(e)}")
            return False
    
    async def _update_agent_configs(self, configs: Dict[str, Any]):
        """Update agent configurations."""
        for agent_name, config in configs.items():
            if hasattr(self, f"{agent_name}_agent"):
                agent = getattr(self, f"{agent_name}_agent")
                await agent.update_config(config)
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and metrics."""
        return {
            "status": "active",
            "components": {
                "llm": "operational",
                "medical_imaging_model": self.medical_imaging_model.get_status(),
                "agents": {
                    "emergency": self.emergency_agent.get_status(),
                    "triage": self.triage_agent.get_status(),
                    "imaging": self.imaging_agent.get_status()
                },
                "workflow": self.workflow.get_status()
            },
            "graph_nodes": len(self.graph.nodes),
            "checkpointer": "memory"
        }
