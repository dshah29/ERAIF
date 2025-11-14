"""
ERAIF FHIR R4 Integration Module

Provides FHIR R4 resource handling, conversion between ERAIF and FHIR formats,
and integration with FHIR servers for emergency radiology workflows.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
import json

try:
    from fhir.resources.patient import Patient
    from fhir.resources.observation import Observation
    from fhir.resources.imagingstudy import ImagingStudy
    from fhir.resources.diagnosticreport import DiagnosticReport
    from fhir.resources.encounter import Encounter
    from fhir.resources.identifier import Identifier
    from fhir.resources.humanname import HumanName
    from fhir.resources.codeableconcept import CodeableConcept
    from fhir.resources.coding import Coding
    from fhir.resources.reference import Reference
    from fhir.resources.bundle import Bundle, BundleEntry
except ImportError:
    raise ImportError("fhir.resources package not found. Install with: pip install fhir.resources")

import httpx

try:
    from .config import ERAIFConfig
except ImportError:
    # Allow standalone usage without full ERAIF dependencies
    ERAIFConfig = None


logger = logging.getLogger(__name__)


class FHIRConverter:
    """
    Converts between ERAIF protocol messages and FHIR R4 resources.
    """
    
    @staticmethod
    def eraif_to_fhir_patient(patient_data: Dict[str, Any]) -> Patient:
        """
        Convert ERAIF patient data to FHIR Patient resource.
        
        Args:
            patient_data: ERAIF patient data dictionary
            
        Returns:
            FHIR Patient resource
        """
        # Build identifier
        identifiers = []
        if patient_data.get("mrn"):
            identifiers.append(Identifier(**{
                "system": "urn:oid:eraif.patient.mrn",
                "value": patient_data["mrn"],
                "use": "official"
            }))
        
        # Build name
        names = []
        if patient_data.get("firstName") or patient_data.get("lastName"):
            name_dict = {
                "use": "official",
                "family": patient_data.get("lastName", "Unknown"),
                "given": [patient_data.get("firstName", "Unknown")]
            }
            if patient_data.get("middleName"):
                name_dict["given"].append(patient_data["middleName"])
            names.append(HumanName(**name_dict))
        
        # Create Patient resource
        patient_dict = {
            "resourceType": "Patient",
            "id": patient_data.get("patientId", str(uuid.uuid4())),
            "identifier": identifiers,
            "name": names,
            "gender": patient_data.get("gender", "unknown").lower(),
            "birthDate": patient_data.get("dateOfBirth"),
            "active": True
        }
        
        # Add address if available
        if patient_data.get("address"):
            patient_dict["address"] = [{
                "use": "home",
                "text": patient_data["address"]
            }]
        
        # Add contact if available
        if patient_data.get("phone"):
            patient_dict["telecom"] = [{
                "system": "phone",
                "value": patient_data["phone"],
                "use": "mobile"
            }]
        
        return Patient(**patient_dict)
    
    @staticmethod
    def fhir_to_eraif_patient(fhir_patient: Patient) -> Dict[str, Any]:
        """
        Convert FHIR Patient resource to ERAIF patient data.
        
        Args:
            fhir_patient: FHIR Patient resource
            
        Returns:
            ERAIF patient data dictionary
        """
        patient_data = {
            "patientId": fhir_patient.id,
            "resourceType": "Patient"
        }
        
        # Extract MRN
        if fhir_patient.identifier:
            for identifier in fhir_patient.identifier:
                if "mrn" in identifier.system.lower() if identifier.system else False:
                    patient_data["mrn"] = identifier.value
                    break
        
        # Extract name
        if fhir_patient.name and len(fhir_patient.name) > 0:
            name = fhir_patient.name[0]
            patient_data["lastName"] = name.family if name.family else ""
            if name.given and len(name.given) > 0:
                patient_data["firstName"] = name.given[0]
                if len(name.given) > 1:
                    patient_data["middleName"] = name.given[1]
        
        # Extract other fields
        patient_data["gender"] = fhir_patient.gender if fhir_patient.gender else "unknown"
        patient_data["dateOfBirth"] = fhir_patient.birthDate.isoformat() if fhir_patient.birthDate else None
        
        # Extract address
        if fhir_patient.address and len(fhir_patient.address) > 0:
            patient_data["address"] = fhir_patient.address[0].text
        
        # Extract phone
        if fhir_patient.telecom:
            for telecom in fhir_patient.telecom:
                if telecom.system == "phone":
                    patient_data["phone"] = telecom.value
                    break
        
        return patient_data
    
    @staticmethod
    def create_imaging_study(
        patient_id: str,
        study_data: Dict[str, Any],
        dicom_study_uid: Optional[str] = None
    ) -> ImagingStudy:
        """
        Create FHIR ImagingStudy resource from ERAIF study data.
        
        Args:
            patient_id: FHIR Patient resource ID
            study_data: ERAIF study data dictionary
            dicom_study_uid: DICOM Study Instance UID
            
        Returns:
            FHIR ImagingStudy resource
        """
        study_dict = {
            "resourceType": "ImagingStudy",
            "id": study_data.get("studyId", str(uuid.uuid4())),
            "status": study_data.get("status", "available"),
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "started": study_data.get("studyDateTime", datetime.now().isoformat())
        }
        
        # Add DICOM Study UID
        if dicom_study_uid:
            study_dict["identifier"] = [{
                "system": "urn:dicom:uid",
                "value": f"urn:oid:{dicom_study_uid}"
            }]
        
        # Add modality - use CodeableConcept with Coding
        if study_data.get("modality"):
            study_dict["modality"] = [
                CodeableConcept(**{
                    "coding": [{
                        "system": "http://dicom.nema.org/resources/ontology/DCM",
                        "code": study_data["modality"],
                        "display": study_data.get("modalityDescription", study_data["modality"])
                    }]
                })
            ]
        
        # Add description
        if study_data.get("studyDescription"):
            study_dict["description"] = study_data["studyDescription"]
        
        # Add number of series and instances
        if study_data.get("numberOfSeries"):
            study_dict["numberOfSeries"] = study_data["numberOfSeries"]
        
        if study_data.get("numberOfInstances"):
            study_dict["numberOfInstances"] = study_data["numberOfInstances"]
        
        return ImagingStudy(**study_dict)
    
    @staticmethod
    def create_diagnostic_report(
        patient_id: str,
        imaging_study_id: str,
        report_data: Dict[str, Any]
    ) -> DiagnosticReport:
        """
        Create FHIR DiagnosticReport resource from AI analysis results.
        
        Args:
            patient_id: FHIR Patient resource ID
            imaging_study_id: FHIR ImagingStudy resource ID
            report_data: ERAIF report/analysis data
            
        Returns:
            FHIR DiagnosticReport resource
        """
        report_dict = {
            "resourceType": "DiagnosticReport",
            "id": report_data.get("reportId", str(uuid.uuid4())),
            "status": report_data.get("status", "final"),
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                    "code": "RAD",
                    "display": "Radiology"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "18748-4",
                    "display": "Diagnostic imaging study"
                }]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": report_data.get("reportDateTime", datetime.now().isoformat()),
            "issued": datetime.now().isoformat()
        }
        
        # Add imaging study reference - use 'study' field in FHIR R4
        if "study" not in report_dict:
            report_dict["study"] = []
        report_dict["study"].append(
            Reference(**{"reference": f"ImagingStudy/{imaging_study_id}"})
        )
        
        # Add conclusion/findings
        if report_data.get("findings"):
            report_dict["conclusion"] = report_data["findings"]
        
        # Add AI confidence if available
        if report_data.get("confidence"):
            if "extension" not in report_dict:
                report_dict["extension"] = []
            report_dict["extension"].append({
                "url": "http://eraif.org/fhir/StructureDefinition/ai-confidence",
                "valueDecimal": report_data["confidence"]
            })
        
        # Add priority/severity
        if report_data.get("priority"):
            report_dict["conclusionCode"] = [{
                "coding": [{
                    "system": "http://eraif.org/fhir/CodeSystem/finding-severity",
                    "code": report_data["priority"],
                    "display": report_data["priority"].capitalize()
                }]
            }]
        
        return DiagnosticReport(**report_dict)
    
    @staticmethod
    def create_observation(
        patient_id: str,
        observation_data: Dict[str, Any]
    ) -> Observation:
        """
        Create FHIR Observation resource from vital signs or measurements.
        
        Args:
            patient_id: FHIR Patient resource ID
            observation_data: Observation data dictionary
            
        Returns:
            FHIR Observation resource
        """
        obs_dict = {
            "resourceType": "Observation",
            "id": observation_data.get("observationId", str(uuid.uuid4())),
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs",
                    "display": "Vital Signs"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": observation_data.get("loincCode", "8867-4"),
                    "display": observation_data.get("observationType", "Observation")
                }]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": observation_data.get("timestamp", datetime.now().isoformat())
        }
        
        # Add value
        if observation_data.get("value"):
            obs_dict["valueQuantity"] = {
                "value": observation_data["value"],
                "unit": observation_data.get("unit", ""),
                "system": "http://unitsofmeasure.org"
            }
        
        return Observation(**obs_dict)


class FHIRClient:
    """
    FHIR R4 client for communicating with FHIR servers.
    """
    
    def __init__(self, config):
        """
        Initialize FHIR client.
        
        Args:
            config: ERAIF configuration or any object with custom_settings dict
        """
        self.config = config
        custom_settings = getattr(config, 'custom_settings', {})
        self.fhir_server_url = custom_settings.get(
            "fhir_server_url",
            "http://localhost:8080/fhir"
        )
        self.timeout = 30.0
        self.logger = logging.getLogger(__name__)
        
        # Authentication settings
        self.auth_token = custom_settings.get("fhir_auth_token")
        
        self.logger.info(f"FHIR Client initialized with server: {self.fhir_server_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for FHIR requests."""
        headers = {
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json"
        }
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        return headers
    
    async def create_resource(
        self,
        resource: Union[Patient, ImagingStudy, DiagnosticReport, Observation]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a FHIR resource on the server.
        
        Args:
            resource: FHIR resource to create
            
        Returns:
            Server response or None if failed
        """
        try:
            resource_type = resource.resource_type
            url = f"{self.fhir_server_url}/{resource_type}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=resource.dict(exclude_none=True),
                    headers=self._get_headers()
                )
                
                if response.status_code in [200, 201]:
                    self.logger.info(f"Successfully created {resource_type}/{resource.id}")
                    return response.json()
                else:
                    self.logger.error(
                        f"Failed to create {resource_type}: {response.status_code} - {response.text}"
                    )
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error creating FHIR resource: {str(e)}")
            return None
    
    async def get_resource(
        self,
        resource_type: str,
        resource_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a FHIR resource from the server.
        
        Args:
            resource_type: Type of FHIR resource (e.g., "Patient")
            resource_id: Resource ID
            
        Returns:
            FHIR resource or None if not found
        """
        try:
            url = f"{self.fhir_server_url}/{resource_type}/{resource_id}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    self.logger.info(f"Successfully retrieved {resource_type}/{resource_id}")
                    return response.json()
                else:
                    self.logger.error(
                        f"Failed to retrieve {resource_type}/{resource_id}: {response.status_code}"
                    )
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error retrieving FHIR resource: {str(e)}")
            return None
    
    async def search_resources(
        self,
        resource_type: str,
        search_params: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Search for FHIR resources.
        
        Args:
            resource_type: Type of FHIR resource
            search_params: Search parameters
            
        Returns:
            FHIR Bundle with search results or None if failed
        """
        try:
            url = f"{self.fhir_server_url}/{resource_type}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params=search_params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    results = response.json()
                    total = results.get("total", 0)
                    self.logger.info(f"Search returned {total} {resource_type} resources")
                    return results
                else:
                    self.logger.error(
                        f"Failed to search {resource_type}: {response.status_code}"
                    )
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error searching FHIR resources: {str(e)}")
            return None
    
    async def update_resource(
        self,
        resource: Union[Patient, ImagingStudy, DiagnosticReport, Observation]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a FHIR resource on the server.
        
        Args:
            resource: FHIR resource to update
            
        Returns:
            Server response or None if failed
        """
        try:
            resource_type = resource.resource_type
            url = f"{self.fhir_server_url}/{resource_type}/{resource.id}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    url,
                    json=resource.dict(exclude_none=True),
                    headers=self._get_headers()
                )
                
                if response.status_code in [200, 201]:
                    self.logger.info(f"Successfully updated {resource_type}/{resource.id}")
                    return response.json()
                else:
                    self.logger.error(
                        f"Failed to update {resource_type}/{resource.id}: {response.status_code}"
                    )
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error updating FHIR resource: {str(e)}")
            return None
    
    async def create_bundle(
        self,
        resources: List[Union[Patient, ImagingStudy, DiagnosticReport, Observation]],
        bundle_type: str = "transaction"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a FHIR Bundle to send multiple resources atomically.
        
        Args:
            resources: List of FHIR resources
            bundle_type: Bundle type (transaction, batch, etc.)
            
        Returns:
            Server response or None if failed
        """
        try:
            entries = []
            for resource in resources:
                entry = BundleEntry(**{
                    "resource": resource.dict(exclude_none=True),
                    "request": {
                        "method": "POST",
                        "url": resource.resource_type
                    }
                })
                entries.append(entry)
            
            bundle = Bundle(**{
                "resourceType": "Bundle",
                "type": bundle_type,
                "entry": entries
            })
            
            url = f"{self.fhir_server_url}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=bundle.dict(exclude_none=True),
                    headers=self._get_headers()
                )
                
                if response.status_code in [200, 201]:
                    self.logger.info(f"Successfully created bundle with {len(resources)} resources")
                    return response.json()
                else:
                    self.logger.error(
                        f"Failed to create bundle: {response.status_code} - {response.text}"
                    )
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error creating FHIR bundle: {str(e)}")
            return None


class ERAIFFHIRIntegration:
    """
    Main FHIR integration class that combines converter and client functionality.
    """
    
    def __init__(self, config):
        """
        Initialize FHIR integration.
        
        Args:
            config: ERAIF configuration or any object with custom_settings dict
        """
        self.config = config
        self.converter = FHIRConverter()
        self.client = FHIRClient(config)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("ERAIF FHIR R4 Integration initialized")
    
    async def process_emergency_transfer(
        self,
        patient_data: Dict[str, Any],
        study_data: Dict[str, Any],
        report_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process an emergency transfer by converting ERAIF data to FHIR and sending to server.
        
        Args:
            patient_data: ERAIF patient data
            study_data: ERAIF study data
            report_data: Optional AI analysis report data
            
        Returns:
            Dictionary with results and created resource IDs
        """
        results = {
            "success": False,
            "resources_created": [],
            "errors": []
        }
        
        try:
            # Convert and create patient
            fhir_patient = self.converter.eraif_to_fhir_patient(patient_data)
            patient_response = await self.client.create_resource(fhir_patient)
            
            if patient_response:
                patient_id = patient_response.get("id", fhir_patient.id)
                results["resources_created"].append(f"Patient/{patient_id}")
                
                # Convert and create imaging study
                fhir_study = self.converter.create_imaging_study(
                    patient_id,
                    study_data,
                    study_data.get("studyInstanceUID")
                )
                study_response = await self.client.create_resource(fhir_study)
                
                if study_response:
                    study_id = study_response.get("id", fhir_study.id)
                    results["resources_created"].append(f"ImagingStudy/{study_id}")
                    
                    # Create diagnostic report if AI analysis available
                    if report_data:
                        fhir_report = self.converter.create_diagnostic_report(
                            patient_id,
                            study_id,
                            report_data
                        )
                        report_response = await self.client.create_resource(fhir_report)
                        
                        if report_response:
                            report_id = report_response.get("id", fhir_report.id)
                            results["resources_created"].append(f"DiagnosticReport/{report_id}")
                        else:
                            results["errors"].append("Failed to create DiagnosticReport")
                    
                    results["success"] = True
                else:
                    results["errors"].append("Failed to create ImagingStudy")
            else:
                results["errors"].append("Failed to create Patient")
                
        except Exception as e:
            self.logger.error(f"Error processing emergency transfer: {str(e)}")
            results["errors"].append(str(e))
        
        return results
    
    async def retrieve_patient_studies(
        self,
        patient_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all imaging studies for a patient.
        
        Args:
            patient_id: FHIR Patient resource ID
            
        Returns:
            List of imaging studies
        """
        try:
            search_results = await self.client.search_resources(
                "ImagingStudy",
                {"patient": patient_id}
            )
            
            if search_results and search_results.get("entry"):
                return [entry["resource"] for entry in search_results["entry"]]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error retrieving patient studies: {str(e)}")
            return []

