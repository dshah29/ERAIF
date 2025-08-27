#!/usr/bin/env python3
"""
ERAIF Demo with Sample Data

This script demonstrates how to use the ERAIF models with realistic
sample data to show the system's capabilities.
"""

import sys
import os
import json
from datetime import datetime

# Add the demo directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.patient import Patient
from models.study import Study, Modality, BodyPart, Urgency
from models.emergency import EmergencyEvent, EmergencyType, EmergencySeverity
from utils.data_generator import ERAIFDataGenerator

def demo_patient_management():
    """Demonstrate patient management capabilities."""
    print("\n🏥 PATIENT MANAGEMENT DEMO")
    print("=" * 40)
    
    # Generate a sample patient
    generator = ERAIFDataGenerator()
    patient = generator.generate_patient()
    
    print(f"Patient: {patient.full_name}")
    print(f"MRN: {patient.mrn}")
    print(f"Age: {patient.age} years")
    print(f"Gender: {patient.demographics.gender.value}")
    print(f"Insurance: {patient.insurance}")
    print(f"Primary Care: {patient.primary_care_physician}")
    
    # Show emergency contact
    if patient.primary_contact:
        contact = patient.primary_contact
        print(f"Emergency Contact: {contact.name} ({contact.relationship})")
        print(f"Phone: {contact.phone}")
    
    # Show medical history
    if patient.medical_history:
        history = patient.medical_history
        print(f"Allergies: {', '.join(history.allergies) if history.allergies else 'None'}")
        print(f"Conditions: {', '.join(history.conditions) if history.conditions else 'None'}")
        print(f"Medications: {', '.join(history.medications) if history.medications else 'None'}")
    
    return patient

def demo_study_management(patient_id: str):
    """Demonstrate study management capabilities."""
    print("\n📊 STUDY MANAGEMENT DEMO")
    print("=" * 40)
    
    # Generate a sample study
    generator = ERAIFDataGenerator()
    study = generator.generate_study(patient_id)
    
    print(f"Study ID: {study.study_id}")
    print(f"Accession: {study.accession_number}")
    print(f"Modality: {study.modality.value}")
    print(f"Body Part: {study.body_part.value}")
    print(f"Urgency: {study.urgency.value}")
    print(f"Status: {study.status.value}")
    print(f"Description: {study.description}")
    print(f"Clinical History: {study.clinical_history}")
    print(f"Referring Physician: {study.referring_physician}")
    
    # Show series information
    print(f"\nImage Series ({study.series_count}):")
    for series in study.series:
        print(f"  Series {series.series_number}: {series.modality.value} - {series.body_part.value}")
        print(f"    Images: {series.image_count}")
        print(f"    Protocol: {series.protocol_name}")
        print(f"    Technique: {series.technique}")
    
    # Show AI analysis
    print(f"\nAI Analysis ({study.ai_analysis_count}):")
    for analysis in study.ai_analyses:
        print(f"  Model: {analysis.model_name} v{analysis.model_version}")
        print(f"    Type: {analysis.analysis_type}")
        print(f"    Status: {analysis.status.value}")
        if analysis.confidence_score:
            print(f"    Confidence: {analysis.confidence_score:.2%}")
        if analysis.findings:
            print(f"    Findings: {', '.join(analysis.findings)}")
        if analysis.recommendations:
            print(f"    Recommendations: {', '.join(analysis.recommendations)}")
    
    return study

def demo_emergency_management():
    """Demonstrate emergency management capabilities."""
    print("\n🚨 EMERGENCY MANAGEMENT DEMO")
    print("=" * 40)
    
    # Generate a sample emergency event
    generator = ERAIFDataGenerator()
    emergency = generator.generate_emergency_event(EmergencyType.NATURAL_DISASTER)
    
    print(f"Emergency: {emergency.title}")
    print(f"Type: {emergency.event_type.value}")
    print(f"Severity: {emergency.severity.value}")
    print(f"Status: {emergency.status.value}")
    print(f"Location: {emergency.location}")
    print(f"Description: {emergency.description}")
    print(f"Affected Population: {emergency.affected_population:,}")
    print(f"Estimated Duration: {emergency.estimated_duration} hours")
    
    # Show affected facilities
    print(f"\nAffected Facilities ({len(emergency.affected_facilities)}):")
    for facility in emergency.affected_facilities:
        print(f"  - {facility}")
    
    # Show emergency contacts
    print(f"\nEmergency Contacts ({len(emergency.emergency_contacts)}):")
    for contact in emergency.emergency_contacts:
        primary = " (Primary)" if contact.is_primary else ""
        print(f"  - {contact.name} - {contact.role} at {contact.organization}{primary}")
        print(f"    Phone: {contact.phone}")
        if contact.email:
            print(f"    Email: {contact.email}")
    
    # Show resource status
    print(f"\nResource Status:")
    for resource in emergency.resource_status:
        status_color = "🟢" if resource.current_status == "operational" else "🟡" if resource.current_status == "degraded" else "🔴"
        print(f"  {status_color} {resource.resource_type}: {resource.current_status} ({resource.capacity_percent:.1f}%)")
        if resource.estimated_recovery_time:
            print(f"    Recovery: {resource.estimated_recovery_time} minutes")
        if resource.backup_available:
            print(f"    Backup: Available")
    
    # Show activated protocols
    print(f"\nActivated Protocols:")
    for protocol in emergency.protocols_activated:
        print(f"  - {protocol}")
    
    return emergency

def demo_emergency_response(emergency: EmergencyEvent):
    """Demonstrate emergency response capabilities."""
    print("\n⚡ EMERGENCY RESPONSE DEMO")
    print("=" * 40)
    
    print(f"Current Emergency: {emergency.title}")
    print(f"Status: {emergency.status.value}")
    
    # Simulate emergency escalation
    print(f"\n🔄 Escalating emergency...")
    old_severity = emergency.severity
    emergency.escalate()
    print(f"Severity changed from {old_severity.value} to {emergency.severity.value}")
    
    # Simulate resource failure
    print(f"\n💥 Simulating resource failure...")
    power_status = emergency.get_resource_status("power")
    if power_status:
        power_status.current_status = "failed"
        power_status.capacity_percent = 0.0
        power_status.estimated_recovery_time = 120
        print(f"Power system failed! Recovery estimated in {power_status.estimated_recovery_time} minutes")
    
    # Simulate protocol activation
    print(f"\n🚨 Activating additional protocols...")
    emergency.activate_protocol("Emergency Power Protocol")
    emergency.activate_protocol("Backup Communication Protocol")
    
    # Add notes
    print(f"\n📝 Adding emergency notes...")
    emergency.add_note("Emergency power generators activated")
    emergency.add_note("Backup communication systems online")
    emergency.add_note("Staff notified of emergency procedures")
    
    # Show updated status
    print(f"\n📊 Updated Emergency Status:")
    print(f"  Status: {emergency.status.value}")
    print(f"  Severity: {emergency.severity.value}")
    print(f"  Protocols: {len(emergency.protocols_activated)}")
    print(f"  Notes: {len(emergency.notes)}")
    
    # Show recent notes
    print(f"\n📝 Recent Notes:")
    for note in emergency.notes[-3:]:  # Show last 3 notes
        print(f"  {note}")

def demo_data_export():
    """Demonstrate data export capabilities."""
    print("\n💾 DATA EXPORT DEMO")
    print("=" * 40)
    
    # Generate sample data
    generator = ERAIFDataGenerator()
    dataset = generator.generate_sample_dataset(5, 2)  # Small dataset for demo
    
    # Export to JSON
    filename = "eraif_demo_export.json"
    generator.save_dataset(dataset, filename)
    
    print(f"✅ Dataset exported to {filename}")
    print(f"📊 Export contains:")
    print(f"  - {dataset['metadata']['total_patients']} patients")
    print(f"  - {dataset['metadata']['total_studies']} studies")
    print(f"  - {dataset['metadata']['total_emergencies']} emergencies")
    
    # Load and verify
    loaded_dataset = generator.load_dataset(filename)
    print(f"✅ Dataset loaded and verified")
    
    return dataset

def main():
    """Run the complete ERAIF demo."""
    print("🚨 ERAIF SYSTEM DEMONSTRATION")
    print("=" * 50)
    print("This demo showcases the ERAIF system capabilities with realistic sample data.")
    print("=" * 50)
    
    try:
        # Run all demos
        patient = demo_patient_management()
        study = demo_study_management(patient.patient_id)
        emergency = demo_emergency_management()
        demo_emergency_response(emergency)
        dataset = demo_data_export()
        
        print("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("The ERAIF system has demonstrated:")
        print("✅ Patient management and demographics")
        print("✅ Imaging study management with AI analysis")
        print("✅ Emergency event coordination")
        print("✅ Resource status monitoring")
        print("✅ Protocol activation and escalation")
        print("✅ Data export and import capabilities")
        
        print(f"\n📁 Generated files:")
        print(f"  - eraif_demo_export.json (sample dataset)")
        
        print(f"\n🚀 Next steps:")
        print(f"  1. Open demo.html in your browser")
        print(f"  2. Use the generated data in your application")
        print(f"  3. Test different emergency scenarios")
        print(f"  4. Explore the model capabilities")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
