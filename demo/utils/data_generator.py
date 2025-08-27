"""
ERAIF Data Generator

This module generates realistic sample data for testing and demonstration
of the ERAIF system including patients, studies, and emergency scenarios.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

from models.patient import Patient, Demographics, EmergencyContact, MedicalHistory, Gender
from models.study import Study, ImageSeries, AIAnalysis, Modality, BodyPart, Urgency, StudyStatus, AIAnalysisStatus
from models.emergency import EmergencyEvent, EmergencyType, EmergencySeverity, EmergencyStatus, EmergencyContact as EmergencyContactEvent, ResourceStatus


class ERAIFDataGenerator:
    """Generates realistic sample data for ERAIF system."""
    
    def __init__(self):
        """Initialize the data generator with sample data."""
        self.hospital_names = [
            "County General Hospital",
            "St. Mary's Medical Center", 
            "Rural Community Hospital",
            "Metropolitan Medical Center",
            "University Hospital",
            "Emergency Trauma Center",
            "Regional Medical Center",
            "Community Health Hospital",
            "Memorial Hospital",
            "Central Medical Center"
        ]
        
        self.physician_names = [
            "Dr. Sarah Johnson",
            "Dr. Michael Chen",
            "Dr. Emily Rodriguez",
            "Dr. David Thompson",
            "Dr. Lisa Wang",
            "Dr. James Wilson",
            "Dr. Maria Garcia",
            "Dr. Robert Brown",
            "Dr. Jennifer Davis",
            "Dr. Christopher Lee"
        ]
        
        self.ai_models = [
            "EraifDetect-CT",
            "EraifSegment-MRI", 
            "EraifClassify-XR",
            "EraifAnalyze-US",
            "EraifEmergency-AI"
        ]
        
        self.emergency_scenarios = [
            {
                "type": EmergencyType.NATURAL_DISASTER,
                "title": "Hurricane Helene Impact",
                "description": "Major hurricane causing widespread infrastructure damage and mass casualties",
                "severity": EmergencySeverity.CATASTROPHIC,
                "affected_facilities": ["County General Hospital", "St. Mary's Medical Center"],
                "affected_population": 50000
            },
            {
                "type": EmergencyType.INFRASTRUCTURE_FAILURE,
                "title": "Regional Power Grid Failure",
                "description": "Complete power outage affecting multiple hospitals and emergency services",
                "severity": EmergencySeverity.MAJOR,
                "affected_facilities": ["Rural Community Hospital", "Metropolitan Medical Center"],
                "affected_population": 25000
            },
            {
                "type": EmergencyType.MASS_CASUALTY_INCIDENT,
                "title": "Multi-Vehicle Highway Accident",
                "description": "Major pileup on interstate causing 50+ casualties",
                "severity": EmergencySeverity.MAJOR,
                "affected_facilities": ["Emergency Trauma Center", "University Hospital"],
                "affected_population": 100
            },
            {
                "type": EmergencyType.TECHNOLOGICAL_FAILURE,
                "title": "PACS System Outage",
                "description": "Complete failure of primary imaging storage system",
                "severity": EmergencySeverity.MODERATE,
                "affected_facilities": ["Memorial Hospital", "Central Medical Center"],
                "affected_population": 15000
            }
        ]
    
    def generate_patient(self, patient_id: str = None, mrn: str = None) -> Patient:
        """Generate a realistic patient record."""
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Jennifer", "William", "Maria"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Generate realistic birth date (18-90 years old)
        years_ago = random.randint(18, 90)
        birth_date = datetime.now() - timedelta(days=years_ago * 365 + random.randint(0, 365))
        
        demographics = Demographics(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=birth_date.date(),
            gender=random.choice(list(Gender)),
            middle_name=random.choice([None, "A", "B", "C", "D"]),
            ethnicity=random.choice([None, "Hispanic", "Non-Hispanic", "Unknown"]),
            race=random.choice([None, "White", "Black", "Asian", "Other", "Unknown"]),
            language=random.choice([None, "English", "Spanish", "French", "German"])
        )
        
        # Generate emergency contact
        emergency_contact = EmergencyContact(
            name=f"{random.choice(first_names)} {random.choice(last_names)}",
            relationship=random.choice(["Spouse", "Parent", "Child", "Sibling", "Friend"]),
            phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            email=f"{first_name.lower()}.{last_name.lower()}@email.com",
            is_primary=True
        )
        
        # Generate medical history
        allergies = random.sample(["Penicillin", "Latex", "Iodine", "Aspirin", "Sulfa"], random.randint(0, 3))
        medications = random.sample(["Lisinopril", "Metformin", "Atorvastatin", "Metoprolol", "Omeprazole"], random.randint(0, 3))
        conditions = random.sample(["Hypertension", "Diabetes", "Heart Disease", "Asthma", "Arthritis"], random.randint(0, 2))
        
        medical_history = MedicalHistory(
            allergies=allergies,
            medications=medications,
            conditions=conditions,
            surgeries=random.sample(["Appendectomy", "Hernia Repair", "Cataract Surgery"], random.randint(0, 2))
        )
        
        patient = Patient(
            patient_id=patient_id,
            mrn=mrn or f"MRN{random.randint(100000, 999999)}",
            demographics=demographics,
            emergency_contacts=[emergency_contact],
            medical_history=medical_history,
            insurance=random.choice(["Blue Cross", "Aetna", "Cigna", "UnitedHealth", "Medicare", "Medicaid"]),
            primary_care_physician=random.choice(self.physician_names)
        )
        
        return patient
    
    def generate_study(self, patient_id: str, study_id: str = None) -> Study:
        """Generate a realistic imaging study."""
        modalities = list(Modality)
        body_parts = list(BodyPart)
        urgencies = list(Urgency)
        
        modality = random.choice(modalities)
        body_part = random.choice(body_parts)
        urgency = random.choice(urgencies)
        
        # Generate realistic study date (within last 30 days)
        study_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        study = Study(
            study_id=study_id,
            patient_id=patient_id,
            accession_number=f"ACC{random.randint(100000, 999999)}",
            study_date=study_date,
            modality=modality,
            body_part=body_part,
            urgency=urgency,
            status=random.choice([StudyStatus.COMPLETED, StudyStatus.IN_PROGRESS, StudyStatus.SCHEDULED]),
            description=f"{modality.value} of {body_part.value.lower()}",
            clinical_history=f"Patient presents with {random.choice(['pain', 'trauma', 'screening', 'follow-up'])}",
            referring_physician=random.choice(self.physician_names),
            performing_physician=random.choice(self.physician_names),
            reading_physician=random.choice(self.physician_names),
            institution=random.choice(self.hospital_names)
        )
        
        # Generate image series
        num_series = random.randint(1, 3)
        for i in range(num_series):
            series = self.generate_image_series(i + 1, modality, body_part)
            study.add_series(series)
        
        # Generate AI analysis
        if random.random() > 0.3:  # 70% chance of having AI analysis
            ai_analysis = self.generate_ai_analysis()
            study.add_ai_analysis(ai_analysis)
        
        return study
    
    def generate_image_series(self, series_number: int, modality: Modality, body_part: BodyPart) -> ImageSeries:
        """Generate a realistic image series."""
        num_images = random.randint(1, 50) if modality == Modality.CT else random.randint(1, 10)
        
        images = [f"/images/series_{series_number}/image_{i:03d}.dcm" for i in range(num_images)]
        
        series = ImageSeries(
            series_number=series_number,
            modality=modality,
            body_part=body_part,
            description=f"{modality.value} series {series_number} - {body_part.value.lower()}",
            images=images,
            institution=random.choice(self.hospital_names),
            manufacturer=random.choice(["GE Healthcare", "Siemens Healthineers", "Philips Healthcare", "Canon Medical"]),
            model=random.choice(["Revolution CT", "MAGNETOM Vida", "iCT Elite", "Ingenia Elition"]),
            software_version=f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            protocol_name=f"{modality.value}_{body_part.value.lower()}_protocol",
            technique=random.choice(["Standard", "Low Dose", "High Resolution", "Contrast Enhanced"]),
            kvp=random.uniform(80, 140) if modality in [Modality.CT, Modality.XR] else None,
            ma=random.uniform(50, 300) if modality in [Modality.CT, Modality.XR] else None,
            exposure_time=random.uniform(0.1, 2.0) if modality in [Modality.CT, Modality.XR] else None,
            slice_thickness=random.uniform(1.0, 5.0) if modality == Modality.CT else None
        )
        
        return series
    
    def generate_ai_analysis(self) -> AIAnalysis:
        """Generate a realistic AI analysis result."""
        model_name = random.choice(self.ai_models)
        analysis_type = random.choice(["detection", "segmentation", "classification", "measurement"])
        
        # Generate realistic findings
        findings = []
        if analysis_type == "detection":
            findings = random.sample([
                "No acute abnormalities detected",
                "Small nodule detected in right upper lobe",
                "Fracture detected in left tibia",
                "Pleural effusion detected bilaterally",
                "Pulmonary embolism detected in right pulmonary artery"
            ], random.randint(1, 2))
        elif analysis_type == "segmentation":
            findings = random.sample([
                "Lung volume: 4.2L (normal range: 3.5-5.0L)",
                "Liver volume: 1.8L (normal range: 1.4-1.8L)",
                "Heart volume: 850ml (normal range: 800-900ml)",
                "Kidney volume: 280ml (normal range: 250-300ml)"
            ], random.randint(1, 2))
        
        # Generate recommendations
        recommendations = random.sample([
            "Follow-up imaging recommended in 6 months",
            "Immediate consultation with specialist recommended",
            "Additional imaging with contrast recommended",
            "No additional imaging required at this time",
            "Consider biopsy for further evaluation"
        ], random.randint(1, 2))
        
        analysis = AIAnalysis(
            model_name=model_name,
            model_version=f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            analysis_type=analysis_type,
            status=random.choice([AIAnalysisStatus.COMPLETED, AIAnalysisStatus.FAILED]),
            confidence_score=random.uniform(0.7, 0.99) if analysis_type == "detection" else None,
            findings=findings,
            recommendations=recommendations,
            processing_time=random.uniform(2.0, 15.0)
        )
        
        if analysis.status == AIAnalysisStatus.COMPLETED:
            analysis.mark_completed(analysis.confidence_score)
        else:
            analysis.mark_failed("Processing timeout")
        
        return analysis
    
    def generate_emergency_event(self, event_type: EmergencyType = None) -> EmergencyEvent:
        """Generate a realistic emergency event."""
        if event_type is None:
            scenario = random.choice(self.emergency_scenarios)
            event_type = scenario["type"]
            title = scenario["title"]
            description = scenario["description"]
            severity = scenario["severity"]
            affected_facilities = scenario["affected_facilities"]
            affected_population = scenario["affected_population"]
        else:
            # Generate generic emergency event
            title = f"{event_type.value.replace('_', ' ').title()} Event"
            description = f"Emergency situation requiring immediate response and coordination"
            severity = random.choice(list(EmergencySeverity))
            affected_facilities = random.sample(self.hospital_names, random.randint(1, 3))
            affected_population = random.randint(1000, 100000)
        
        # Generate emergency contacts
        emergency_contacts = []
        for i, facility in enumerate(affected_facilities):
            contact = EmergencyContactEvent(
                name=f"Emergency Coordinator {i+1}",
                role="Emergency Coordinator",
                organization=facility,
                phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                email=f"emergency@{facility.lower().replace(' ', '').replace('-', '')}.org",
                is_primary=i == 0,
                can_escalate=True,
                response_time_minutes=random.randint(5, 30)
            )
            emergency_contacts.append(contact)
        
        # Generate resource status
        resource_status = []
        resources = ["power", "network", "storage", "bandwidth", "backup_systems"]
        for resource in resources:
            status = ResourceStatus(
                resource_type=resource,
                current_status=random.choice(["operational", "degraded", "failed"]),
                capacity_percent=random.uniform(20, 100),
                estimated_recovery_time=random.randint(30, 480) if resource in ["power", "network"] else None,
                backup_available=random.choice([True, False])
            )
            resource_status.append(status)
        
        event = EmergencyEvent(
            event_type=event_type,
            severity=severity,
            title=title,
            description=description,
            location=random.choice(["Downtown Area", "Suburban Region", "Rural County", "Metropolitan Area"]),
            affected_facilities=affected_facilities,
            affected_population=affected_population,
            estimated_duration=random.randint(2, 72),  # 2-72 hours
            emergency_contacts=emergency_contacts,
            resource_status=resource_status,
            protocols_activated=random.sample([
                "Mass Casualty Protocol",
                "Disaster Response Protocol", 
                "Emergency Communication Protocol",
                "Resource Allocation Protocol"
            ], random.randint(1, 3))
        )
        
        return event
    
    def generate_sample_dataset(self, num_patients: int = 50, num_emergencies: int = 5) -> Dict[str, Any]:
        """Generate a complete sample dataset."""
        print(f"Generating sample dataset with {num_patients} patients and {num_emergencies} emergencies...")
        
        # Generate patients
        patients = []
        for i in range(num_patients):
            patient = self.generate_patient()
            patients.append(patient)
            print(f"Generated patient {i+1}/{num_patients}: {patient.full_name}")
        
        # Generate studies for each patient
        studies = []
        for i, patient in enumerate(patients):
            num_studies = random.randint(1, 3)
            for j in range(num_studies):
                study = self.generate_study(patient.patient_id)
                studies.append(study)
            print(f"Generated {num_studies} studies for patient {i+1}")
        
        # Generate emergency events
        emergencies = []
        for i in range(num_emergencies):
            emergency = self.generate_emergency_event()
            emergencies.append(emergency)
            print(f"Generated emergency {i+1}/{num_emergencies}: {emergency.title}")
        
        # Create dataset summary
        dataset = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_patients": len(patients),
                "total_studies": len(studies),
                "total_emergencies": len(emergencies),
                "total_images": sum(study.total_images for study in studies),
                "total_ai_analyses": sum(study.ai_analysis_count for study in studies)
            },
            "patients": [patient.to_dict() for patient in patients],
            "studies": [study.to_dict() for study in studies],
            "emergencies": [emergency.to_dict() for emergency in emergencies]
        }
        
        print(f"Dataset generation complete!")
        print(f"  - Patients: {len(patients)}")
        print(f"  - Studies: {len(studies)}")
        print(f"  - Emergencies: {len(emergencies)}")
        print(f"  - Total Images: {dataset['metadata']['total_images']}")
        print(f"  - AI Analyses: {dataset['metadata']['total_ai_analyses']}")
        
        return dataset
    
    def save_dataset(self, dataset: Dict[str, Any], filename: str = "eraif_sample_dataset.json"):
        """Save the generated dataset to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(dataset, f, indent=2)
        print(f"Dataset saved to {filename}")
    
    def load_dataset(self, filename: str = "eraif_sample_dataset.json") -> Dict[str, Any]:
        """Load a dataset from a JSON file."""
        with open(filename, 'r') as f:
            dataset = json.load(f)
        print(f"Dataset loaded from {filename}")
        return dataset


# Convenience functions for quick data generation
def generate_quick_patient() -> Patient:
    """Generate a single patient quickly."""
    generator = ERAIFDataGenerator()
    return generator.generate_patient()

def generate_quick_study(patient_id: str) -> Study:
    """Generate a single study quickly."""
    generator = ERAIFDataGenerator()
    return generator.generate_study(patient_id)

def generate_quick_emergency() -> EmergencyEvent:
    """Generate a single emergency event quickly."""
    generator = ERAIFDataGenerator()
    return generator.generate_emergency_event()

def generate_sample_data(num_patients: int = 20) -> Dict[str, Any]:
    """Generate a small sample dataset for quick testing."""
    generator = ERAIFDataGenerator()
    return generator.generate_sample_dataset(num_patients, 3)


if __name__ == "__main__":
    # Example usage
    generator = ERAIFDataGenerator()
    
    # Generate a small sample dataset
    dataset = generator.generate_sample_dataset(10, 2)
    
    # Save to file
    generator.save_dataset(dataset, "eraif_demo_dataset.json")
    
    print("\nSample data generation complete!")
    print("You can now use this data in your ERAIF demo.")
