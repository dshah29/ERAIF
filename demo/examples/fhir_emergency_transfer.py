"""
FHIR R4 Emergency Transfer Example

Demonstrates ERAIF's FHIR R4 integration capabilities for emergency
radiology data transfer between facilities using standardized FHIR resources.

This example shows:
1. Converting ERAIF data to FHIR R4 resources
2. Sending emergency patient and imaging data to a FHIR server
3. Retrieving and processing FHIR resources
4. Creating diagnostic reports from AI analysis

Usage:
    python demo/examples/fhir_emergency_transfer.py
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import FHIR integration directly to avoid heavy dependencies
import importlib.util
spec = importlib.util.spec_from_file_location(
    "fhir_integration",
    os.path.join(os.path.dirname(__file__), '../../src/core/fhir_integration.py')
)
fhir_module = importlib.util.module_from_spec(spec)

try:
    spec.loader.exec_module(fhir_module)
    FHIRConverter = fhir_module.FHIRConverter
    FHIRClient = fhir_module.FHIRClient
except Exception as e:
    print(f"Error importing FHIR integration: {e}")
    print("Make sure fhir.resources is installed: pip install fhir.resources")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Simple config class for demo
class DemoConfig:
    """Simple configuration for demo purposes."""
    def __init__(self):
        self.custom_settings = {}


class FHIREmergencyTransferDemo:
    """
    Demonstration of FHIR R4 emergency transfer workflow.
    """
    
    def __init__(self):
        """Initialize the demo."""
        # Create configuration
        self.config = DemoConfig()
        self.config.custom_settings = {
            "facility_id": "HOSPITAL_A",
            "fhir_server_url": "http://localhost:8080/fhir",  # HAPI FHIR server
            # "fhir_auth_token": "your_token_here"  # Add if authentication required
        }
        
        # Initialize FHIR converter
        self.converter = FHIRConverter()
        # Initialize FHIR client (won't connect without a real server)
        self.client = FHIRClient(self.config)
    
    def print_header(self, title: str):
        """Print formatted section header."""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70 + "\n")
    
    def print_resource(self, resource_type: str, resource_data: Dict[str, Any]):
        """Print FHIR resource details."""
        print(f"\n{resource_type}:")
        print("-" * 50)
        
        # Print key fields based on resource type
        if resource_type == "Patient":
            if resource_data.get("name"):
                name = resource_data["name"][0]
                full_name = f"{name.get('given', [''])[0]} {name.get('family', '')}"
                print(f"  Name: {full_name}")
            
            if resource_data.get("identifier"):
                mrn = resource_data["identifier"][0].get("value", "N/A")
                print(f"  MRN: {mrn}")
            
            print(f"  Gender: {resource_data.get('gender', 'N/A')}")
            print(f"  Birth Date: {resource_data.get('birthDate', 'N/A')}")
            
        elif resource_type == "ImagingStudy":
            print(f"  Study ID: {resource_data.get('id', 'N/A')}")
            print(f"  Status: {resource_data.get('status', 'N/A')}")
            print(f"  Started: {resource_data.get('started', 'N/A')}")
            
            if resource_data.get("modality"):
                modality = resource_data["modality"][0]
                print(f"  Modality: {modality.get('code', 'N/A')}")
            
            print(f"  Number of Series: {resource_data.get('numberOfSeries', 'N/A')}")
            print(f"  Number of Instances: {resource_data.get('numberOfInstances', 'N/A')}")
            
        elif resource_type == "DiagnosticReport":
            print(f"  Report ID: {resource_data.get('id', 'N/A')}")
            print(f"  Status: {resource_data.get('status', 'N/A')}")
            print(f"  Issued: {resource_data.get('issued', 'N/A')}")
            
            if resource_data.get("conclusion"):
                print(f"  Findings: {resource_data['conclusion'][:100]}...")
            
            # Check for AI confidence extension
            if resource_data.get("extension"):
                for ext in resource_data["extension"]:
                    if "ai-confidence" in ext.get("url", ""):
                        print(f"  AI Confidence: {ext.get('valueDecimal', 0):.2%}")
    
    async def demo_patient_conversion(self):
        """Demonstrate ERAIF to FHIR patient conversion."""
        self.print_header("1. ERAIF to FHIR Patient Conversion")
        
        # Sample ERAIF patient data
        eraif_patient = {
            "patientId": "PT-12345",
            "mrn": "MRN-789456",
            "firstName": "Sarah",
            "lastName": "Johnson",
            "middleName": "Marie",
            "dateOfBirth": "1985-06-15",
            "gender": "female",
            "phone": "+1-555-0123",
            "address": "123 Main St, Anytown, ST 12345"
        }
        
        print("ERAIF Patient Data:")
        print(f"  Name: {eraif_patient['firstName']} {eraif_patient['lastName']}")
        print(f"  MRN: {eraif_patient['mrn']}")
        print(f"  DOB: {eraif_patient['dateOfBirth']}")
        
        # Convert to FHIR
        fhir_patient = self.converter.eraif_to_fhir_patient(eraif_patient)
        
        print("\n✓ Converted to FHIR R4 Patient Resource")
        self.print_resource("Patient", fhir_patient.dict())
        
        return eraif_patient, fhir_patient
    
    async def demo_imaging_study_creation(self, patient_id: str):
        """Demonstrate FHIR ImagingStudy creation."""
        self.print_header("2. FHIR ImagingStudy Creation")
        
        # Sample study data
        study_data = {
            "studyId": "STUDY-67890",
            "studyInstanceUID": "1.2.840.113619.2.55.3.2831178572.123",
            "status": "available",
            "modality": "CT",
            "modalityDescription": "Computed Tomography",
            "studyDescription": "CT Head without contrast - Emergency",
            "studyDateTime": datetime.now(timezone.utc).isoformat(),
            "numberOfSeries": 3,
            "numberOfInstances": 450
        }
        
        print("Creating ImagingStudy from Emergency CT Scan:")
        print(f"  Modality: {study_data['modality']}")
        print(f"  Description: {study_data['studyDescription']}")
        print(f"  Series: {study_data['numberOfSeries']}")
        print(f"  Images: {study_data['numberOfInstances']}")
        
        # Create FHIR ImagingStudy
        fhir_study = self.converter.create_imaging_study(
            patient_id,
            study_data,
            study_data["studyInstanceUID"]
        )
        
        print("\n✓ Created FHIR R4 ImagingStudy Resource")
        self.print_resource("ImagingStudy", fhir_study.dict())
        
        return study_data, fhir_study
    
    async def demo_diagnostic_report(self, patient_id: str, study_id: str):
        """Demonstrate FHIR DiagnosticReport with AI analysis."""
        self.print_header("3. FHIR DiagnosticReport with AI Analysis")
        
        # Sample AI analysis report
        report_data = {
            "reportId": "REPORT-11223",
            "status": "final",
            "reportDateTime": datetime.now(timezone.utc).isoformat(),
            "findings": (
                "AI-assisted analysis of emergency CT Head scan reveals: "
                "No acute intracranial hemorrhage. No mass effect or midline shift. "
                "Ventricles and sulci are within normal limits. "
                "Recommendation: Clinical correlation advised. "
                "PRIORITY: Findings are within normal limits, no immediate intervention required."
            ),
            "confidence": 0.94,
            "priority": "NORMAL"
        }
        
        print("AI Analysis Results:")
        print(f"  Status: {report_data['status']}")
        print(f"  AI Confidence: {report_data['confidence']:.2%}")
        print(f"  Priority: {report_data['priority']}")
        print(f"\n  Findings:")
        print(f"    {report_data['findings'][:150]}...")
        
        # Create FHIR DiagnosticReport
        fhir_report = self.converter.create_diagnostic_report(
            patient_id,
            study_id,
            report_data
        )
        
        print("\n✓ Created FHIR R4 DiagnosticReport Resource with AI Confidence Extension")
        self.print_resource("DiagnosticReport", fhir_report.dict())
        
        return report_data, fhir_report
    
    async def demo_complete_emergency_transfer(self):
        """Demonstrate complete emergency transfer workflow."""
        self.print_header("4. Complete Emergency Transfer Workflow")
        
        print("Scenario: Rural hospital transferring patient to trauma center")
        print("Emergency CT scan shows potential intracranial injury")
        print("Using FHIR R4 to standardize data exchange\n")
        
        # Patient data
        patient_data = {
            "patientId": "PT-EMERG-99887",
            "mrn": "MRN-999888",
            "firstName": "Michael",
            "lastName": "Roberts",
            "dateOfBirth": "1972-03-22",
            "gender": "male",
            "phone": "+1-555-9876"
        }
        
        # Study data
        study_data = {
            "studyId": "STUDY-EMERG-456",
            "studyInstanceUID": "1.2.840.113619.2.55.3.2831178572.456",
            "status": "available",
            "modality": "CT",
            "studyDescription": "CT Head - Trauma Protocol",
            "studyDateTime": datetime.now(timezone.utc).isoformat(),
            "numberOfSeries": 4,
            "numberOfInstances": 680
        }
        
        # AI analysis report
        report_data = {
            "reportId": "REPORT-EMERG-789",
            "status": "preliminary",
            "reportDateTime": datetime.now(timezone.utc).isoformat(),
            "findings": (
                "URGENT: AI-detected abnormality. "
                "Possible acute subdural hematoma along right cerebral convexity. "
                "Approximate maximum thickness 8mm. Associated mass effect with "
                "minimal midline shift (3mm to the left). "
                "RECOMMENDATION: Immediate neurosurgical consultation required. "
                "Consider transfer to Level 1 Trauma Center."
            ),
            "confidence": 0.89,
            "priority": "CRITICAL"
        }
        
        print("Step 1: Converting ERAIF data to FHIR R4 resources...")
        print("Step 2: Preparing emergency transfer bundle...")
        print("Step 3: Sending to receiving facility's FHIR server...\n")
        
        # Note: In production, this would actually send to a FHIR server
        print("⚠️  Note: This demo runs in offline mode.")
        print("    To connect to a real FHIR server:")
        print("    1. Install HAPI FHIR server: https://hapifhir.io/")
        print("    2. Update fhir_server_url in config")
        print("    3. Run: docker run -p 8080:8080 hapiproject/hapi:latest\n")
        
        # Simulate the transfer process
        results = {
            "success": True,
            "resources_created": [
                f"Patient/{patient_data['patientId']}",
                f"ImagingStudy/{study_data['studyId']}",
                f"DiagnosticReport/{report_data['reportId']}"
            ],
            "transfer_time_ms": 234,
            "priority": "CRITICAL"
        }
        
        print("✓ Emergency Transfer Complete!")
        print(f"\n  Resources Created:")
        for resource in results["resources_created"]:
            print(f"    • {resource}")
        
        print(f"\n  Transfer Time: {results['transfer_time_ms']}ms")
        print(f"  Priority Level: {results['priority']}")
        print(f"\n  Status: Ready for immediate review at receiving facility")
        
        return results
    
    async def demo_fhir_search(self):
        """Demonstrate FHIR search capabilities."""
        self.print_header("5. FHIR Search Capabilities")
        
        print("FHIR search allows querying resources by various parameters:\n")
        
        search_examples = [
            {
                "name": "Find patient by MRN",
                "resource": "Patient",
                "params": {"identifier": "MRN-789456"}
            },
            {
                "name": "Find imaging studies by patient",
                "resource": "ImagingStudy",
                "params": {"patient": "Patient/PT-12345"}
            },
            {
                "name": "Find critical diagnostic reports",
                "resource": "DiagnosticReport",
                "params": {"status": "final", "code": "RAD"}
            },
            {
                "name": "Find studies by modality and date",
                "resource": "ImagingStudy",
                "params": {"modality": "CT", "started": "gt2024-01-01"}
            }
        ]
        
        for i, example in enumerate(search_examples, 1):
            print(f"{i}. {example['name']}")
            print(f"   GET {example['resource']}?", end="")
            print("&".join([f"{k}={v}" for k, v in example['params'].items()]))
            print()
        
        print("\n✓ FHIR provides powerful, standardized search capabilities")
        print("  Compatible with existing FHIR servers and EHR systems")
    
    async def run_all_demos(self):
        """Run all demonstration scenarios."""
        print("\n")
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 10 + "ERAIF FHIR R4 Integration Demonstration" + " " * 18 + "║")
        print("╚" + "=" * 68 + "╝")
        
        try:
            # Demo 1: Patient conversion
            eraif_patient, fhir_patient = await self.demo_patient_conversion()
            await asyncio.sleep(1)
            
            # Demo 2: Imaging study
            study_data, fhir_study = await self.demo_imaging_study_creation(
                fhir_patient.id
            )
            await asyncio.sleep(1)
            
            # Demo 3: Diagnostic report
            report_data, fhir_report = await self.demo_diagnostic_report(
                fhir_patient.id,
                fhir_study.id
            )
            await asyncio.sleep(1)
            
            # Demo 4: Complete transfer
            transfer_results = await self.demo_complete_emergency_transfer()
            await asyncio.sleep(1)
            
            # Demo 5: Search capabilities
            await self.demo_fhir_search()
            
            # Summary
            self.print_header("Summary")
            print("✓ FHIR R4 integration provides:")
            print("  • Standardized data exchange format")
            print("  • Interoperability with existing healthcare systems")
            print("  • Support for emergency radiology workflows")
            print("  • AI analysis integration with FHIR extensions")
            print("  • Comprehensive search and retrieval capabilities")
            print("\n✓ Phase 1 Milestone: FHIR R4 Integration Complete!")
            print("\nNext Steps:")
            print("  1. Deploy HAPI FHIR server for testing")
            print("  2. Integrate with hospital EHR systems")
            print("  3. Test with real emergency scenarios")
            print("  4. Proceed to Phase 2 pilot program")
            
            print("\n" + "=" * 70)
            print("Demo completed successfully!")
            print("=" * 70 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error during demo: {str(e)}")
            import traceback
            traceback.print_exc()


async def main():
    """Main entry point."""
    demo = FHIREmergencyTransferDemo()
    await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main())

