#!/usr/bin/env python3
"""
ERAIF AI/ML Demo

Enhanced demo showcasing AI-powered emergency radiology analysis,
LangGraph workflows, and intelligent decision support.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json
import random
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.core.config import ERAIFConfig
from src.core.emergency_system import EmergencySystem
from src.ai.pipeline import AIMLPipeline
from src.ai.workflows import EmergencyWorkflow

# Demo utilities
from ..utils.data_generator import generate_emergency_case, generate_imaging_study
from ..models.emergency import EmergencyEvent, EmergencyType, EmergencySeverity


class ERAIFAIDemo:
    """
    Interactive AI demo for ERAIF system.
    
    Demonstrates:
    - AI-powered emergency triage
    - Medical imaging analysis with deep learning
    - LangGraph workflow orchestration
    - Intelligent resource optimization
    - Real-time decision support
    """
    
    def __init__(self):
        """Initialize the AI demo."""
        print("🤖 Initializing ERAIF AI/ML Demo System...")
        
        # Create configuration
        self.config = self._create_demo_config()
        
        # Initialize emergency system
        self.emergency_system = EmergencySystem(self.config)
        
        # Demo data
        self.demo_cases = []
        self.demo_results = []
        
        print("✅ ERAIF AI System initialized successfully!")
        print()
    
    def _create_demo_config(self) -> ERAIFConfig:
        """Create demo configuration."""
        config = ERAIFConfig()
        
        # Set demo-specific settings
        config.deployment_mode = "development"
        config.debug = True
        
        # AI configuration (using mock values for demo)
        config.ai.openai_api_key = os.getenv("OPENAI_API_KEY", "demo_key")
        config.ai.enable_gpu = False  # Disable for demo
        config.ai.model_cache_dir = "./demo_models"
        config.ai.min_confidence_threshold = 0.3
        config.ai.critical_finding_threshold = 0.7
        config.ai.auto_alert_threshold = 0.85
        
        # Emergency settings
        config.emergency.auto_activation_enabled = True
        config.emergency.disaster_mode_compression = True
        
        # Custom demo settings
        config.custom_settings = {
            "facility_id": "DEMO_HOSPITAL_001",
            "demo_mode": True,
            "generate_synthetic_data": True
        }
        
        return config
    
    async def run_demo(self):
        """Run the interactive AI demo."""
        print("🚨 ERAIF AI/ML Emergency Radiology Demo")
        print("=" * 50)
        print()
        
        while True:
            print("Select a demo scenario:")
            print("1. 🩻 AI-Powered Emergency Case Analysis")
            print("2. 🏥 Mass Casualty Incident with AI Coordination")
            print("3. 🌪️ Disaster Response with LangGraph Workflows")
            print("4. 🔬 Medical Imaging AI Analysis")
            print("5. 🧠 Intelligent Resource Optimization")
            print("6. 📊 System Status and AI Metrics")
            print("7. 🎯 Custom Emergency Scenario")
            print("8. 🔄 Continuous Monitoring Demo")
            print("0. Exit")
            print()
            
            choice = input("Enter your choice (0-8): ").strip()
            print()
            
            try:
                if choice == "1":
                    await self.demo_emergency_case_analysis()
                elif choice == "2":
                    await self.demo_mass_casualty_incident()
                elif choice == "3":
                    await self.demo_disaster_response()
                elif choice == "4":
                    await self.demo_imaging_analysis()
                elif choice == "5":
                    await self.demo_resource_optimization()
                elif choice == "6":
                    await self.demo_system_status()
                elif choice == "7":
                    await self.demo_custom_scenario()
                elif choice == "8":
                    await self.demo_continuous_monitoring()
                elif choice == "0":
                    print("👋 Thank you for trying ERAIF AI Demo!")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                
            except KeyboardInterrupt:
                print("\n\n⏸️  Demo interrupted by user.")
                break
            except Exception as e:
                print(f"❌ Error running demo: {str(e)}")
            
            print("\n" + "─" * 50 + "\n")
    
    async def demo_emergency_case_analysis(self):
        """Demo AI-powered emergency case analysis."""
        print("🩻 AI-POWERED EMERGENCY CASE ANALYSIS")
        print("=" * 40)
        print()
        
        # Generate synthetic emergency case
        case_data = self._generate_demo_case()
        
        print("📋 Generated Emergency Case:")
        self._print_case_summary(case_data)
        print()
        
        print("🤖 Processing case through AI pipeline...")
        print("   ⚡ Performing intelligent triage...")
        print("   🔍 Analyzing medical imaging with deep learning...")
        print("   🧠 Generating clinical recommendations...")
        print("   📊 Executing LangGraph workflow...")
        print()
        
        # Process case through AI system
        start_time = datetime.now()
        results = await self.emergency_system.process_emergency_case(
            case_data, 
            priority=case_data.get("priority", "medium")
        )
        processing_time = (datetime.now() - start_time).total_seconds()
        
        print(f"✅ Case processed in {processing_time:.2f} seconds")
        print()
        
        # Display AI analysis results
        self._display_ai_results(results)
        
        # Store for later analysis
        self.demo_cases.append(case_data)
        self.demo_results.append(results)
        
        input("\n🔍 Press Enter to continue...")
    
    async def demo_mass_casualty_incident(self):
        """Demo mass casualty incident with AI coordination."""
        print("🏥 MASS CASUALTY INCIDENT - AI COORDINATION")
        print("=" * 45)
        print()
        
        print("🚨 SCENARIO: Multi-vehicle accident on highway")
        print("   📍 Location: Interstate 95, Mile Marker 127")
        print("   👥 Estimated casualties: 15-20 people")
        print("   🚑 Multiple ambulances en route")
        print()
        
        # Activate emergency mode
        print("⚠️  Activating Emergency Mode...")
        emergency_result = await self.emergency_system.activate_emergency_mode(
            "Mass Casualty Incident - Highway Accident",
            "high",
            4  # 4 hour estimated duration
        )
        
        print(f"✅ Emergency mode activated: {emergency_result['status']}")
        print(f"   🆔 Workflow ID: {emergency_result.get('workflow_id', 'N/A')}")
        print()
        
        # Generate multiple casualties
        casualties = []
        for i in range(random.randint(12, 18)):
            casualty = self._generate_casualty_case(i + 1)
            casualties.append(casualty)
        
        print(f"👥 Processing {len(casualties)} casualties through AI triage...")
        print()
        
        # Process each casualty
        triage_results = []
        for i, casualty in enumerate(casualties[:5]):  # Process first 5 for demo
            print(f"   🔍 Analyzing casualty #{i+1}...")
            result = await self.emergency_system.process_emergency_case(
                casualty, 
                priority="urgent"
            )
            triage_results.append(result)
            
            # Show triage decision
            ai_analysis = result.get("ai_analysis", {})
            triage = ai_analysis.get("triage_results", {})
            priority = triage.get("priority", "unknown")
            confidence = triage.get("confidence", 0.0)
            
            print(f"      ➤ Priority: {priority.upper()} (confidence: {confidence:.2f})")
        
        print()
        print("📊 MASS CASUALTY AI COORDINATION SUMMARY:")
        self._display_mass_casualty_summary(triage_results)
        
        # Deactivate emergency mode
        print("\n🔄 Deactivating emergency mode...")
        deactivation_result = await self.emergency_system.deactivate_emergency_mode(
            "Mass casualty incident successfully managed"
        )
        print(f"✅ Emergency mode deactivated after {deactivation_result.get('duration_hours', 0):.1f} hours")
        
        input("\n🔍 Press Enter to continue...")
    
    async def demo_disaster_response(self):
        """Demo disaster response with LangGraph workflows."""
        print("🌪️ DISASTER RESPONSE - LANGGRAPH WORKFLOWS")
        print("=" * 45)
        print()
        
        print("🌪️ SCENARIO: Category 4 Hurricane approaching")
        print("   📍 Affected area: Coastal region, 200-mile radius")
        print("   🏥 12 hospitals in projected path")
        print("   ⏰ Landfall expected in 18 hours")
        print()
        
        # Activate disaster response
        disaster_data = {
            "disaster_type": "hurricane",
            "severity": "category_4",
            "affected_facilities": 12,
            "estimated_impact_hours": 18,
            "evacuation_required": True
        }
        
        print("🤖 Executing AI-powered disaster response workflow...")
        workflow_result = await self.emergency_system.emergency_workflow.execute_workflow(
            "disaster_response",
            disaster_data
        )
        
        print("✅ Disaster response workflow completed")
        print(f"   🆔 Workflow ID: {workflow_result.get('workflow_id')}")
        print()
        
        # Display workflow timeline
        print("📋 DISASTER RESPONSE TIMELINE:")
        timeline = workflow_result.get("timeline", [])
        for event in timeline:
            timestamp = event.get("timestamp", "")[:19]  # Remove microseconds
            description = event.get("description", "")
            print(f"   {timestamp} - {description}")
        
        print()
        print("🎯 KEY DECISIONS MADE BY AI:")
        decisions = workflow_result.get("decisions", [])
        for decision in decisions:
            print(f"   • {decision.get('decision', 'N/A')}")
            print(f"     Rationale: {decision.get('rationale', 'N/A')}")
            print(f"     Confidence: {decision.get('confidence', 0.0):.2f}")
        
        input("\n🔍 Press Enter to continue...")
    
    async def demo_imaging_analysis(self):
        """Demo medical imaging AI analysis."""
        print("🔬 MEDICAL IMAGING AI ANALYSIS")
        print("=" * 35)
        print()
        
        # Generate synthetic imaging studies
        imaging_studies = [
            {
                "study_id": "CT_001",
                "modality": "CT",
                "study_type": "trauma",
                "body_part": "head",
                "indication": "Motor vehicle accident, altered mental status"
            },
            {
                "study_id": "XRAY_001", 
                "modality": "X-Ray",
                "study_type": "chest",
                "body_part": "chest",
                "indication": "Shortness of breath, chest pain"
            },
            {
                "study_id": "MRI_001",
                "modality": "MRI",
                "study_type": "brain",
                "body_part": "brain", 
                "indication": "Acute stroke symptoms"
            }
        ]
        
        print("🔍 Available imaging studies for AI analysis:")
        for i, study in enumerate(imaging_studies, 1):
            print(f"   {i}. {study['modality']} - {study['indication']}")
        
        choice = input(f"\nSelect study to analyze (1-{len(imaging_studies)}): ").strip()
        
        try:
            study_index = int(choice) - 1
            selected_study = imaging_studies[study_index]
        except (ValueError, IndexError):
            print("❌ Invalid selection. Using first study.")
            selected_study = imaging_studies[0]
        
        print(f"\n🤖 Analyzing {selected_study['modality']} study with AI...")
        print(f"   📋 Study: {selected_study['indication']}")
        print("   🧠 Loading deep learning models...")
        print("   🔍 Performing image analysis...")
        print("   📊 Generating radiological report...")
        print()
        
        # Simulate AI analysis
        await asyncio.sleep(2)  # Simulate processing time
        
        # Generate mock AI analysis results
        analysis_result = self._generate_imaging_analysis_result(selected_study)
        
        print("✅ AI Analysis Complete")
        print()
        print("📋 RADIOLOGICAL AI FINDINGS:")
        print(f"   🎯 Study Quality: {analysis_result['study_quality']}")
        print(f"   🚨 Urgency Level: {analysis_result['urgency_level'].upper()}")
        print(f"   🎯 Confidence: {analysis_result['confidence']:.2f}")
        print()
        
        if analysis_result.get("critical_findings"):
            print("🚨 CRITICAL FINDINGS:")
            for finding in analysis_result["critical_findings"]:
                print(f"   • {finding}")
        
        if analysis_result.get("significant_findings"):
            print("\n📊 SIGNIFICANT FINDINGS:")
            for finding in analysis_result["significant_findings"]:
                print(f"   • {finding}")
        
        print(f"\n💡 AI IMPRESSION:")
        print(f"   {analysis_result.get('impression', 'No significant abnormalities detected.')}")
        
        if analysis_result.get("recommendations"):
            print(f"\n🎯 RECOMMENDATIONS:")
            for rec in analysis_result["recommendations"]:
                print(f"   • {rec}")
        
        input("\n🔍 Press Enter to continue...")
    
    async def demo_resource_optimization(self):
        """Demo intelligent resource optimization."""
        print("🧠 INTELLIGENT RESOURCE OPTIMIZATION")
        print("=" * 40)
        print()
        
        # Generate current facility status
        facility_data = {
            "total_beds": 200,
            "occupied_beds": 165,
            "icu_beds": 40,
            "icu_occupied": 35,
            "er_beds": 20,
            "er_occupied": 18,
            "ventilators": 25,
            "ventilators_in_use": 20,
            "staff_on_duty": {
                "physicians": 12,
                "nurses": 45,
                "technicians": 18
            }
        }
        
        current_demand = {
            "incoming_patients": 8,
            "critical_patients": 3,
            "surgical_cases": 2,
            "imaging_requests": 15
        }
        
        print("📊 CURRENT FACILITY STATUS:")
        print(f"   🏥 Bed Occupancy: {facility_data['occupied_beds']}/{facility_data['total_beds']} "
              f"({facility_data['occupied_beds']/facility_data['total_beds']*100:.1f}%)")
        print(f"   🚨 ICU Occupancy: {facility_data['icu_occupied']}/{facility_data['icu_beds']} "
              f"({facility_data['icu_occupied']/facility_data['icu_beds']*100:.1f}%)")
        print(f"   🫁 Ventilator Usage: {facility_data['ventilators_in_use']}/{facility_data['ventilators']} "
              f"({facility_data['ventilators_in_use']/facility_data['ventilators']*100:.1f}%)")
        print()
        
        print("📈 INCOMING DEMAND:")
        print(f"   👥 Incoming patients: {current_demand['incoming_patients']}")
        print(f"   🚨 Critical patients: {current_demand['critical_patients']}")
        print(f"   🔬 Imaging requests: {current_demand['imaging_requests']}")
        print()
        
        print("🤖 Running AI resource optimization...")
        
        # Run resource optimization
        optimization_result = await self.emergency_system.optimize_resources(
            facility_data,
            current_demand
        )
        
        print("✅ Resource optimization complete")
        print()
        
        # Display optimization results
        print("🎯 AI OPTIMIZATION RECOMMENDATIONS:")
        
        # Mock optimization recommendations
        recommendations = [
            "Discharge 3 stable patients to free ICU beds",
            "Call in 2 additional nurses for next shift",
            "Prioritize 5 imaging studies for critical patients",
            "Prepare overflow area for 4 additional patients",
            "Alert nearby facilities about potential transfers"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        print()
        print("📊 PREDICTED IMPACT:")
        print("   ⬆️ Available ICU beds: +3")
        print("   ⬆️ Nursing capacity: +15%")
        print("   ⬇️ Patient wait times: -25%")
        print("   ⬆️ Emergency preparedness: +40%")
        
        input("\n🔍 Press Enter to continue...")
    
    async def demo_system_status(self):
        """Demo system status and AI metrics."""
        print("📊 SYSTEM STATUS & AI METRICS")
        print("=" * 32)
        print()
        
        # Get system status
        status = await self.emergency_system.get_system_status()
        
        print("🖥️  SYSTEM OVERVIEW:")
        print(f"   Status: {status['system_status'].upper()}")
        print(f"   Uptime: {status['metrics']['uptime_hours']:.1f} hours")
        print(f"   Active Cases: {status['active_cases']}")
        print(f"   Emergency Mode: {'ACTIVE' if status['emergency_mode']['active'] else 'INACTIVE'}")
        print()
        
        print("🤖 AI/ML PIPELINE STATUS:")
        ai_status = status['components']['ai_pipeline']
        print(f"   Pipeline Status: {ai_status['status'].upper()}")
        print(f"   GPU Enabled: {status['configuration']['gpu_enabled']}")
        print(f"   Graph Nodes: {ai_status['graph_nodes']}")
        print()
        
        print("📈 PROCESSING METRICS:")
        metrics = status['metrics']
        print(f"   Cases Processed: {metrics['cases_processed']}")
        print(f"   AI Analyses: {metrics['ai_analyses_completed']}")
        print(f"   Workflows Executed: {metrics['workflows_executed']}")
        print(f"   Alerts Generated: {metrics['alerts_generated']}")
        print()
        
        print("🔧 COMPONENT STATUS:")
        components = status['components']
        for component, comp_status in components.items():
            if isinstance(comp_status, dict):
                comp_status = comp_status.get('status', 'unknown')
            print(f"   {component.replace('_', ' ').title()}: {comp_status.upper()}")
        
        # Show recent cases if any
        if self.demo_results:
            print("\n📋 RECENT AI ANALYSES:")
            for i, result in enumerate(self.demo_results[-3:], 1):
                case_id = result.get('case_id', 'Unknown')[:8]
                processing_time = result.get('processing_time_seconds', 0)
                critical_findings = len(result.get('critical_findings', []))
                
                print(f"   {i}. Case {case_id}: {processing_time:.1f}s, "
                      f"{critical_findings} critical findings")
        
        input("\n🔍 Press Enter to continue...")
    
    async def demo_custom_scenario(self):
        """Demo custom emergency scenario."""
        print("🎯 CUSTOM EMERGENCY SCENARIO")
        print("=" * 30)
        print()
        
        print("Create your own emergency scenario:")
        print()
        
        # Get user input
        scenario_type = input("Emergency type (trauma/cardiac/stroke/other): ").strip() or "trauma"
        patient_age = input("Patient age (default: 45): ").strip() or "45"
        severity = input("Severity (low/medium/high/critical): ").strip() or "medium"
        
        try:
            age = int(patient_age)
        except ValueError:
            age = 45
        
        print()
        print(f"🚨 Creating {severity.upper()} {scenario_type} scenario for {age}-year-old patient...")
        
        # Generate custom case
        custom_case = {
            "patient_id": f"CUSTOM_{random.randint(1000, 9999)}",
            "age": age,
            "chief_complaint": f"{scenario_type} emergency",
            "priority": severity,
            "vital_signs": {
                "heart_rate": random.randint(60, 120),
                "blood_pressure_systolic": random.randint(90, 180),
                "blood_pressure_diastolic": random.randint(60, 110),
                "respiratory_rate": random.randint(12, 24),
                "temperature": round(random.uniform(97.0, 102.0), 1),
                "oxygen_saturation": random.randint(88, 100)
            },
            "custom_scenario": True
        }
        
        print("\n🤖 Processing custom scenario through AI pipeline...")
        
        # Process custom case
        result = await self.emergency_system.process_emergency_case(
            custom_case,
            priority=severity
        )
        
        print("✅ Custom scenario processed successfully")
        print()
        
        # Display results
        self._display_ai_results(result)
        
        input("\n🔍 Press Enter to continue...")
    
    async def demo_continuous_monitoring(self):
        """Demo continuous monitoring with real-time updates."""
        print("🔄 CONTINUOUS MONITORING DEMO")
        print("=" * 32)
        print()
        
        print("🔄 Starting continuous monitoring (press Ctrl+C to stop)...")
        print("   Simulating real-time emergency case processing...")
        print()
        
        try:
            case_count = 0
            while True:
                case_count += 1
                
                # Generate random case
                case_data = self._generate_demo_case()
                
                print(f"🚨 New case #{case_count}: {case_data.get('chief_complaint', 'Unknown')}")
                
                # Process case
                result = await self.emergency_system.process_emergency_case(case_data)
                
                # Show brief result
                ai_analysis = result.get("ai_analysis", {})
                triage = ai_analysis.get("triage_results", {})
                priority = triage.get("priority", "unknown")
                confidence = triage.get("confidence", 0.0)
                processing_time = result.get("processing_time_seconds", 0)
                
                print(f"   ➤ AI Triage: {priority.upper()} (confidence: {confidence:.2f})")
                print(f"   ⏱️  Processing time: {processing_time:.2f}s")
                
                critical_findings = result.get("critical_findings", [])
                if critical_findings:
                    print(f"   🚨 {len(critical_findings)} critical findings detected!")
                
                print()
                
                # Wait before next case
                await asyncio.sleep(random.uniform(3, 8))
                
        except KeyboardInterrupt:
            print("\n⏹️  Continuous monitoring stopped")
            print(f"   Processed {case_count} cases during monitoring session")
        
        input("\n🔍 Press Enter to continue...")
    
    # Helper methods
    
    def _generate_demo_case(self) -> Dict[str, Any]:
        """Generate a realistic demo emergency case."""
        scenarios = [
            {
                "chief_complaint": "Motor vehicle accident with head trauma",
                "priority": "critical",
                "age": random.randint(25, 65),
                "vital_signs": {
                    "heart_rate": random.randint(90, 130),
                    "blood_pressure_systolic": random.randint(80, 160),
                    "blood_pressure_diastolic": random.randint(50, 100),
                    "respiratory_rate": random.randint(16, 28),
                    "temperature": round(random.uniform(97.5, 99.5), 1),
                    "oxygen_saturation": random.randint(85, 98)
                }
            },
            {
                "chief_complaint": "Chest pain with shortness of breath",
                "priority": "high",
                "age": random.randint(45, 80),
                "vital_signs": {
                    "heart_rate": random.randint(70, 110),
                    "blood_pressure_systolic": random.randint(120, 180),
                    "blood_pressure_diastolic": random.randint(70, 110),
                    "respiratory_rate": random.randint(18, 26),
                    "temperature": round(random.uniform(98.0, 100.0), 1),
                    "oxygen_saturation": random.randint(90, 100)
                }
            },
            {
                "chief_complaint": "Sudden onset severe headache",
                "priority": "urgent",
                "age": random.randint(30, 70),
                "vital_signs": {
                    "heart_rate": random.randint(60, 100),
                    "blood_pressure_systolic": random.randint(140, 200),
                    "blood_pressure_diastolic": random.randint(90, 120),
                    "respiratory_rate": random.randint(14, 22),
                    "temperature": round(random.uniform(98.0, 101.0), 1),
                    "oxygen_saturation": random.randint(95, 100)
                }
            }
        ]
        
        scenario = random.choice(scenarios)
        
        case_data = {
            "patient_id": f"DEMO_{random.randint(10000, 99999)}",
            "timestamp": datetime.now().isoformat(),
            **scenario
        }
        
        # Add imaging studies for some cases
        if random.random() > 0.3:  # 70% chance of imaging
            case_data["imaging_studies"] = [
                {
                    "study_id": f"IMG_{random.randint(1000, 9999)}",
                    "modality": random.choice(["CT", "X-Ray", "MRI", "Ultrasound"]),
                    "body_part": random.choice(["head", "chest", "abdomen", "extremity"]),
                    "indication": case_data["chief_complaint"]
                }
            ]
        
        return case_data
    
    def _generate_casualty_case(self, casualty_number: int) -> Dict[str, Any]:
        """Generate a casualty case for mass casualty demo."""
        severity_levels = ["critical", "urgent", "moderate", "minor"]
        weights = [0.1, 0.2, 0.4, 0.3]  # Distribution of severity
        
        severity = random.choices(severity_levels, weights=weights)[0]
        
        complaints = {
            "critical": ["Multiple trauma with head injury", "Severe internal bleeding", "Respiratory distress"],
            "urgent": ["Chest trauma", "Abdominal pain", "Possible fractures"],
            "moderate": ["Lacerations requiring sutures", "Minor fractures", "Contusions"],
            "minor": ["Minor cuts and bruises", "Anxiety", "Minor sprains"]
        }
        
        return {
            "patient_id": f"MCI_{casualty_number:03d}",
            "chief_complaint": random.choice(complaints[severity]),
            "priority": severity,
            "age": random.randint(18, 75),
            "incident_type": "mass_casualty",
            "vital_signs": self._generate_vital_signs(severity)
        }
    
    def _generate_vital_signs(self, severity: str) -> Dict[str, Any]:
        """Generate vital signs based on severity."""
        if severity == "critical":
            return {
                "heart_rate": random.randint(110, 150),
                "blood_pressure_systolic": random.randint(70, 120),
                "blood_pressure_diastolic": random.randint(40, 80),
                "respiratory_rate": random.randint(24, 35),
                "temperature": round(random.uniform(96.0, 102.0), 1),
                "oxygen_saturation": random.randint(75, 92)
            }
        elif severity == "urgent":
            return {
                "heart_rate": random.randint(90, 120),
                "blood_pressure_systolic": random.randint(100, 160),
                "blood_pressure_diastolic": random.randint(60, 100),
                "respiratory_rate": random.randint(18, 28),
                "temperature": round(random.uniform(97.0, 101.0), 1),
                "oxygen_saturation": random.randint(88, 96)
            }
        else:  # moderate or minor
            return {
                "heart_rate": random.randint(70, 100),
                "blood_pressure_systolic": random.randint(110, 140),
                "blood_pressure_diastolic": random.randint(70, 90),
                "respiratory_rate": random.randint(14, 22),
                "temperature": round(random.uniform(98.0, 99.5), 1),
                "oxygen_saturation": random.randint(95, 100)
            }
    
    def _generate_imaging_analysis_result(self, study: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock imaging analysis result."""
        modality = study["modality"]
        study_type = study["study_type"]
        
        # Mock results based on modality
        if modality == "CT" and "trauma" in study_type:
            return {
                "study_quality": "excellent",
                "urgency_level": "critical",
                "confidence": 0.92,
                "critical_findings": [
                    "Small subdural hematoma in right frontal region",
                    "Cerebral edema with midline shift"
                ],
                "significant_findings": [
                    "Multiple facial fractures",
                    "Soft tissue swelling"
                ],
                "impression": "Acute traumatic brain injury with subdural hematoma requiring immediate neurosurgical evaluation",
                "recommendations": [
                    "Immediate neurosurgical consultation",
                    "Serial neurological assessments",
                    "Consider repeat CT in 6 hours"
                ]
            }
        elif modality == "X-Ray" and "chest" in study_type:
            return {
                "study_quality": "good",
                "urgency_level": "urgent",
                "confidence": 0.87,
                "critical_findings": [
                    "Right-sided pneumothorax (20%)"
                ],
                "significant_findings": [
                    "Rib fractures (ribs 4-6 right side)",
                    "Pulmonary contusion"
                ],
                "impression": "Pneumothorax and rib fractures consistent with blunt chest trauma",
                "recommendations": [
                    "Consider chest tube placement",
                    "Monitor respiratory status",
                    "Pain management for rib fractures"
                ]
            }
        else:  # MRI brain
            return {
                "study_quality": "excellent",
                "urgency_level": "critical",
                "confidence": 0.94,
                "critical_findings": [
                    "Acute infarct in left middle cerebral artery territory",
                    "No hemorrhagic transformation"
                ],
                "significant_findings": [
                    "Moderate cerebral edema",
                    "Patent circle of Willis"
                ],
                "impression": "Acute ischemic stroke in MCA distribution, candidate for intervention",
                "recommendations": [
                    "Immediate stroke team activation",
                    "Consider thrombolytic therapy",
                    "Neurological monitoring"
                ]
            }
    
    def _print_case_summary(self, case_data: Dict[str, Any]):
        """Print a summary of the case data."""
        print(f"   👤 Patient ID: {case_data.get('patient_id', 'Unknown')}")
        print(f"   🎂 Age: {case_data.get('age', 'Unknown')}")
        print(f"   🚨 Chief Complaint: {case_data.get('chief_complaint', 'Unknown')}")
        print(f"   📊 Priority: {case_data.get('priority', 'medium').upper()}")
        
        vital_signs = case_data.get('vital_signs', {})
        if vital_signs:
            print(f"   💓 Vital Signs:")
            print(f"      HR: {vital_signs.get('heart_rate', 'N/A')} bpm")
            print(f"      BP: {vital_signs.get('blood_pressure_systolic', 'N/A')}/{vital_signs.get('blood_pressure_diastolic', 'N/A')} mmHg")
            print(f"      RR: {vital_signs.get('respiratory_rate', 'N/A')} /min")
            print(f"      Temp: {vital_signs.get('temperature', 'N/A')}°F")
            print(f"      SpO2: {vital_signs.get('oxygen_saturation', 'N/A')}%")
        
        imaging_studies = case_data.get('imaging_studies', [])
        if imaging_studies:
            print(f"   🔬 Imaging Studies:")
            for study in imaging_studies:
                print(f"      {study.get('modality', 'Unknown')} - {study.get('body_part', 'Unknown')}")
    
    def _display_ai_results(self, results: Dict[str, Any]):
        """Display AI analysis results."""
        print("🤖 AI ANALYSIS RESULTS:")
        print(f"   🆔 Case ID: {results.get('case_id', 'Unknown')}")
        print(f"   ⏱️  Processing Time: {results.get('processing_time_seconds', 0):.2f} seconds")
        print()
        
        # Triage results
        ai_analysis = results.get("ai_analysis", {})
        triage_results = ai_analysis.get("triage_results", {})
        
        if triage_results:
            print("🏥 TRIAGE ANALYSIS:")
            print(f"   Priority: {triage_results.get('priority', 'unknown').upper()}")
            print(f"   Confidence: {triage_results.get('confidence', 0.0):.2f}")
            print(f"   Max Wait Time: {triage_results.get('max_wait_time', 'N/A')} minutes")
            
            red_flags = triage_results.get('red_flags', [])
            if red_flags:
                print("   🚨 Red Flags:")
                for flag in red_flags[:3]:  # Show first 3
                    print(f"      • {flag}")
            print()
        
        # Imaging results
        imaging_results = ai_analysis.get("imaging_results", {})
        if imaging_results and imaging_results.get("studies_analyzed", 0) > 0:
            print("🔬 IMAGING ANALYSIS:")
            print(f"   Studies Analyzed: {imaging_results.get('studies_analyzed', 0)}")
            summary = imaging_results.get('summary', 'No summary available')
            print(f"   Summary: {summary}")
            print()
        
        # Critical findings
        critical_findings = results.get("critical_findings", [])
        if critical_findings:
            print("🚨 CRITICAL FINDINGS:")
            for finding in critical_findings:
                print(f"   • {finding.get('description', 'N/A')} "
                      f"(confidence: {finding.get('confidence', 0.0):.2f})")
            print()
        
        # Recommendations
        ai_recommendations = ai_analysis.get("recommendations", [])
        if ai_recommendations:
            print("💡 AI RECOMMENDATIONS:")
            for rec in ai_recommendations[:5]:  # Show first 5
                priority = rec.get('priority', 3)
                timeframe = rec.get('timeframe', 'routine')
                print(f"   {priority}. {rec.get('recommendation', 'N/A')} ({timeframe})")
            print()
        
        # Next actions
        next_actions = results.get("next_actions", [])
        if next_actions:
            print("📋 NEXT ACTIONS:")
            for action in next_actions[:3]:  # Show first 3
                print(f"   • {action.get('action', 'N/A')} ({action.get('timeframe', 'routine')})")
    
    def _display_mass_casualty_summary(self, triage_results: List[Dict[str, Any]]):
        """Display mass casualty triage summary."""
        priority_counts = {"critical": 0, "urgent": 0, "moderate": 0, "minor": 0}
        
        for result in triage_results:
            ai_analysis = result.get("ai_analysis", {})
            triage = ai_analysis.get("triage_results", {})
            priority = triage.get("priority", "moderate")
            
            if priority in ["immediate", "critical"]:
                priority_counts["critical"] += 1
            elif priority in ["urgent", "high"]:
                priority_counts["urgent"] += 1
            elif priority in ["less_urgent", "moderate"]:
                priority_counts["moderate"] += 1
            else:
                priority_counts["minor"] += 1
        
        print(f"   🔴 Critical (Red): {priority_counts['critical']} patients")
        print(f"   🟡 Urgent (Yellow): {priority_counts['urgent']} patients")
        print(f"   🟢 Moderate (Green): {priority_counts['moderate']} patients")
        print(f"   🔵 Minor (Blue): {priority_counts['minor']} patients")
        print()
        
        total_critical_findings = sum(
            len(result.get("critical_findings", []))
            for result in triage_results
        )
        
        print(f"   🚨 Total Critical Findings: {total_critical_findings}")
        print(f"   🤖 AI Processing Success Rate: 100%")
        print(f"   ⏱️  Average Processing Time: {sum(result.get('processing_time_seconds', 0) for result in triage_results) / len(triage_results):.2f}s")


async def main():
    """Main demo function."""
    try:
        demo = ERAIFAIDemo()
        await demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
