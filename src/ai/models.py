"""
Medical Imaging AI Models for ERAIF

This module contains specialized AI models for medical imaging analysis,
including deep learning models for various imaging modalities.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
import pickle
import json

# Medical imaging libraries
import pydicom
import SimpleITK as sitk
from monai.transforms import (
    Compose, LoadImage, EnsureChannelFirst, Spacing, Orientation,
    ScaleIntensityRange, Resize, ToTensor
)
from monai.networks.nets import ResNet, DenseNet121, EfficientNetBN
from monai.data import DataLoader, Dataset

# ML libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import joblib

from ..core.config import ERAIFConfig


logger = logging.getLogger(__name__)


class MedicalImagingModel:
    """
    Main medical imaging AI model that orchestrates multiple specialized models
    for different imaging modalities and clinical tasks.
    """
    
    def __init__(self, config: ERAIFConfig):
        """Initialize the medical imaging model."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Model registry
        self.models = {}
        self.transforms = {}
        self.scalers = {}
        
        # Device configuration
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.logger.info(f"Using device: {self.device}")
        
        # Initialize models
        self._initialize_models()
        
        # Model status
        self.status = "ready"
        self.last_updated = datetime.now()
        
    def _initialize_models(self):
        """Initialize all specialized models."""
        try:
            # CT models
            self._initialize_ct_models()
            
            # X-ray models
            self._initialize_xray_models()
            
            # MRI models
            self._initialize_mri_models()
            
            # Ultrasound models
            self._initialize_ultrasound_models()
            
            # General classification models
            self._initialize_general_models()
            
            self.logger.info("All medical imaging models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing models: {str(e)}")
            self.status = "error"
    
    def _initialize_ct_models(self):
        """Initialize CT-specific models."""
        # Trauma detection model
        self.models["ct_trauma"] = CTTraumaModel(self.device)
        
        # Stroke detection model
        self.models["ct_stroke"] = CTStrokeModel(self.device)
        
        # Pulmonary embolism detection
        self.models["ct_pe"] = CTPulmonaryEmbolismModel(self.device)
        
        # CT transforms
        self.transforms["ct"] = Compose([
            LoadImage(image_only=True),
            EnsureChannelFirst(),
            Spacing(pixdim=(1.0, 1.0, 1.0), mode="bilinear"),
            Orientation(axcodes="RAS"),
            ScaleIntensityRange(a_min=-1000, a_max=1000, b_min=0.0, b_max=1.0, clip=True),
            Resize(spatial_size=(512, 512, 512)),
            ToTensor()
        ])
    
    def _initialize_xray_models(self):
        """Initialize X-ray specific models."""
        # Chest X-ray pathology detection
        self.models["xray_chest"] = ChestXRayModel(self.device)
        
        # Fracture detection
        self.models["xray_fracture"] = FractureDetectionModel(self.device)
        
        # X-ray transforms
        self.transforms["xray"] = Compose([
            LoadImage(image_only=True),
            EnsureChannelFirst(),
            ScaleIntensityRange(a_min=0, a_max=255, b_min=0.0, b_max=1.0, clip=True),
            Resize(spatial_size=(224, 224)),
            ToTensor()
        ])
    
    def _initialize_mri_models(self):
        """Initialize MRI-specific models."""
        # Brain MRI analysis
        self.models["mri_brain"] = BrainMRIModel(self.device)
        
        # Spine MRI analysis
        self.models["mri_spine"] = SpineMRIModel(self.device)
        
        # MRI transforms
        self.transforms["mri"] = Compose([
            LoadImage(image_only=True),
            EnsureChannelFirst(),
            Spacing(pixdim=(1.0, 1.0, 1.0), mode="bilinear"),
            Orientation(axcodes="RAS"),
            ScaleIntensityRange(a_min=0, a_max=4095, b_min=0.0, b_max=1.0, clip=True),
            Resize(spatial_size=(256, 256, 256)),
            ToTensor()
        ])
    
    def _initialize_ultrasound_models(self):
        """Initialize ultrasound-specific models."""
        # Cardiac ultrasound
        self.models["us_cardiac"] = CardiacUltrasoundModel(self.device)
        
        # FAST exam (Focused Assessment with Sonography in Trauma)
        self.models["us_fast"] = FASTExamModel(self.device)
        
        # Ultrasound transforms
        self.transforms["ultrasound"] = Compose([
            LoadImage(image_only=True),
            EnsureChannelFirst(),
            ScaleIntensityRange(a_min=0, a_max=255, b_min=0.0, b_max=1.0, clip=True),
            Resize(spatial_size=(224, 224)),
            ToTensor()
        ])
    
    def _initialize_general_models(self):
        """Initialize general classification models."""
        # Emergency priority classifier
        self.models["priority_classifier"] = EmergencyPriorityClassifier()
        
        # Resource demand predictor
        self.models["resource_predictor"] = ResourceDemandPredictor()
    
    async def analyze_study(
        self,
        study_data: Dict[str, Any],
        modality: str,
        study_type: str
    ) -> Dict[str, Any]:
        """
        Analyze a medical imaging study.
        
        Args:
            study_data: Study data including image paths/arrays
            modality: Imaging modality (CT, MRI, X-Ray, Ultrasound)
            study_type: Specific study type (e.g., trauma, stroke, chest)
            
        Returns:
            Analysis results with findings, confidence, and recommendations
        """
        try:
            # Determine appropriate model
            model_key = f"{modality.lower()}_{study_type.lower()}"
            
            if model_key not in self.models:
                # Fallback to general modality model
                model_key = modality.lower()
                if model_key not in self.models:
                    return {
                        "error": f"No model available for {modality} {study_type}",
                        "confidence": 0.0
                    }
            
            model = self.models[model_key]
            
            # Preprocess images
            processed_images = await self._preprocess_images(
                study_data, modality.lower()
            )
            
            # Run inference
            results = await model.predict(processed_images)
            
            # Post-process results
            analysis_result = self._post_process_results(results, modality, study_type)
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing study: {str(e)}")
            return {
                "error": str(e),
                "confidence": 0.0,
                "modality": modality,
                "study_type": study_type
            }
    
    async def _preprocess_images(
        self,
        study_data: Dict[str, Any],
        modality: str
    ) -> torch.Tensor:
        """Preprocess images for model input."""
        try:
            # Get appropriate transforms
            transform = self.transforms.get(modality)
            
            if not transform:
                raise ValueError(f"No transforms available for modality: {modality}")
            
            # Handle different input types
            if "image_paths" in study_data:
                # Load from file paths
                images = []
                for path in study_data["image_paths"]:
                    img = transform(path)
                    images.append(img)
                return torch.stack(images)
                
            elif "image_arrays" in study_data:
                # Process numpy arrays
                images = []
                for array in study_data["image_arrays"]:
                    img = transform(array)
                    images.append(img)
                return torch.stack(images)
                
            elif "dicom_data" in study_data:
                # Process DICOM data
                return await self._process_dicom_data(study_data["dicom_data"], transform)
                
            else:
                raise ValueError("No valid image data found in study_data")
                
        except Exception as e:
            self.logger.error(f"Error preprocessing images: {str(e)}")
            raise
    
    async def _process_dicom_data(
        self,
        dicom_data: List[Dict[str, Any]],
        transform
    ) -> torch.Tensor:
        """Process DICOM data into tensor format."""
        images = []
        
        for dcm_info in dicom_data:
            if "file_path" in dcm_info:
                # Load DICOM file
                ds = pydicom.dcmread(dcm_info["file_path"])
                pixel_array = ds.pixel_array
            elif "pixel_array" in dcm_info:
                pixel_array = dcm_info["pixel_array"]
            else:
                continue
                
            # Apply transforms
            img = transform(pixel_array)
            images.append(img)
        
        return torch.stack(images) if images else torch.empty(0)
    
    def _post_process_results(
        self,
        results: Dict[str, Any],
        modality: str,
        study_type: str
    ) -> Dict[str, Any]:
        """Post-process model results into standardized format."""
        return {
            "modality": modality,
            "study_type": study_type,
            "findings": results.get("findings", []),
            "confidence": results.get("confidence", 0.0),
            "abnormality_detected": results.get("abnormality_detected", False),
            "critical_findings": results.get("critical_findings", []),
            "recommendations": results.get("recommendations", []),
            "processing_time": results.get("processing_time", 0.0),
            "model_version": results.get("model_version", "1.0.0"),
            "timestamp": datetime.now().isoformat()
        }
    
    async def batch_analyze(
        self,
        studies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze multiple studies in batch."""
        results = []
        
        for study in studies:
            result = await self.analyze_study(
                study["data"],
                study["modality"],
                study["study_type"]
            )
            results.append(result)
        
        return results
    
    async def update_model(self, model_updates: Dict[str, Any]) -> bool:
        """Update models with new weights or configurations."""
        try:
            for model_name, update_data in model_updates.items():
                if model_name in self.models:
                    model = self.models[model_name]
                    
                    if hasattr(model, "update_weights"):
                        await model.update_weights(update_data)
                    elif hasattr(model, "load_state_dict"):
                        model.load_state_dict(update_data)
            
            self.last_updated = datetime.now()
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating models: {str(e)}")
            return False
    
    def get_status(self) -> str:
        """Get current model status."""
        return self.status
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about all loaded models."""
        return {
            "status": self.status,
            "device": str(self.device),
            "last_updated": self.last_updated.isoformat(),
            "models": list(self.models.keys()),
            "transforms": list(self.transforms.keys())
        }


class BaseImagingModel(nn.Module):
    """Base class for all imaging models."""
    
    def __init__(self, device: torch.device):
        super().__init__()
        self.device = device
        self.model_version = "1.0.0"
        self.last_updated = datetime.now()
    
    async def predict(self, images: torch.Tensor) -> Dict[str, Any]:
        """Make predictions on input images."""
        raise NotImplementedError
    
    async def update_weights(self, weights: Dict[str, Any]):
        """Update model weights."""
        self.load_state_dict(weights)
        self.last_updated = datetime.now()


class CTTraumaModel(BaseImagingModel):
    """CT model for trauma detection."""
    
    def __init__(self, device: torch.device):
        super().__init__(device)
        
        # Use ResNet-50 backbone for trauma detection
        self.backbone = ResNet(
            spatial_dims=3,
            n_input_channels=1,
            num_classes=5,  # hemorrhage, fracture, pneumothorax, etc.
            block="bottleneck",
            layers=[3, 4, 6, 3]
        ).to(device)
        
        self.trauma_types = [
            "intracranial_hemorrhage",
            "skull_fracture", 
            "pneumothorax",
            "hemothorax",
            "abdominal_bleeding"
        ]
    
    async def predict(self, images: torch.Tensor) -> Dict[str, Any]:
        """Predict trauma findings in CT images."""
        try:
            self.eval()
            with torch.no_grad():
                images = images.to(self.device)
                outputs = self.backbone(images)
                probabilities = torch.softmax(outputs, dim=1)
                
                # Extract findings
                findings = []
                critical_findings = []
                
                for i, trauma_type in enumerate(self.trauma_types):
                    prob = probabilities[0, i].item()
                    if prob > 0.5:  # Threshold for positive finding
                        finding = {
                            "type": trauma_type,
                            "confidence": prob,
                            "severity": "high" if prob > 0.8 else "moderate"
                        }
                        findings.append(finding)
                        
                        if prob > 0.8:
                            critical_findings.append(finding)
                
                return {
                    "findings": findings,
                    "critical_findings": critical_findings,
                    "confidence": probabilities.max().item(),
                    "abnormality_detected": len(findings) > 0,
                    "recommendations": self._generate_trauma_recommendations(findings)
                }
                
        except Exception as e:
            logger.error(f"Error in CT trauma prediction: {str(e)}")
            return {"error": str(e), "confidence": 0.0}
    
    def _generate_trauma_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on trauma findings."""
        recommendations = []
        
        for finding in findings:
            trauma_type = finding["type"]
            confidence = finding["confidence"]
            
            if trauma_type == "intracranial_hemorrhage" and confidence > 0.7:
                recommendations.append("Immediate neurosurgical consultation")
                recommendations.append("Serial neurological assessments")
            elif trauma_type == "pneumothorax" and confidence > 0.7:
                recommendations.append("Consider chest tube placement")
                recommendations.append("Serial chest X-rays")
            elif trauma_type == "abdominal_bleeding" and confidence > 0.7:
                recommendations.append("Immediate surgical consultation")
                recommendations.append("Type and crossmatch blood products")
        
        return recommendations


class ChestXRayModel(BaseImagingModel):
    """Chest X-ray pathology detection model."""
    
    def __init__(self, device: torch.device):
        super().__init__(device)
        
        # Use DenseNet for chest X-ray analysis
        self.backbone = DenseNet121(
            spatial_dims=2,
            in_channels=1,
            out_channels=14  # Common chest pathologies
        ).to(device)
        
        self.pathologies = [
            "pneumonia", "pneumothorax", "pleural_effusion", "cardiomegaly",
            "consolidation", "edema", "emphysema", "fibrosis",
            "pneumomediastinum", "pneumoperitoneum", "fracture",
            "foreign_body", "mass", "nodule"
        ]
    
    async def predict(self, images: torch.Tensor) -> Dict[str, Any]:
        """Predict pathologies in chest X-ray images."""
        try:
            self.eval()
            with torch.no_grad():
                images = images.to(self.device)
                outputs = self.backbone(images)
                probabilities = torch.sigmoid(outputs)  # Multi-label classification
                
                findings = []
                critical_findings = []
                
                for i, pathology in enumerate(self.pathologies):
                    prob = probabilities[0, i].item()
                    if prob > 0.3:  # Lower threshold for X-ray findings
                        finding = {
                            "type": pathology,
                            "confidence": prob,
                            "severity": self._assess_severity(pathology, prob)
                        }
                        findings.append(finding)
                        
                        if pathology in ["pneumothorax", "pneumonia"] and prob > 0.7:
                            critical_findings.append(finding)
                
                return {
                    "findings": findings,
                    "critical_findings": critical_findings,
                    "confidence": probabilities.max().item(),
                    "abnormality_detected": len(findings) > 0,
                    "recommendations": self._generate_xray_recommendations(findings)
                }
                
        except Exception as e:
            logger.error(f"Error in chest X-ray prediction: {str(e)}")
            return {"error": str(e), "confidence": 0.0}
    
    def _assess_severity(self, pathology: str, confidence: float) -> str:
        """Assess severity of X-ray finding."""
        if pathology in ["pneumothorax", "pneumonia"] and confidence > 0.8:
            return "high"
        elif confidence > 0.6:
            return "moderate"
        else:
            return "low"
    
    def _generate_xray_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on X-ray findings."""
        recommendations = []
        
        for finding in findings:
            pathology = finding["type"]
            confidence = finding["confidence"]
            
            if pathology == "pneumothorax" and confidence > 0.6:
                recommendations.append("Consider chest tube if tension pneumothorax")
                recommendations.append("Monitor respiratory status closely")
            elif pathology == "pneumonia" and confidence > 0.6:
                recommendations.append("Consider antibiotic therapy")
                recommendations.append("Monitor oxygen saturation")
        
        return recommendations


class EmergencyPriorityClassifier:
    """ML classifier for emergency priority assessment."""
    
    def __init__(self):
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            "age", "heart_rate", "blood_pressure_systolic", "blood_pressure_diastolic",
            "respiratory_rate", "temperature", "oxygen_saturation", "pain_score",
            "consciousness_level", "mechanism_of_injury_score"
        ]
    
    async def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict emergency priority based on clinical features."""
        try:
            if not self.is_trained:
                # Load pre-trained model if available
                await self._load_pretrained_model()
            
            # Extract and normalize features
            feature_vector = self._extract_features(features)
            scaled_features = self.scaler.transform([feature_vector])
            
            # Make prediction
            priority_probs = self.model.predict_proba(scaled_features)[0]
            priority_class = self.model.predict(scaled_features)[0]
            
            priority_labels = ["low", "medium", "high", "critical"]
            
            return {
                "priority": priority_labels[priority_class],
                "confidence": max(priority_probs),
                "probability_distribution": dict(zip(priority_labels, priority_probs))
            }
            
        except Exception as e:
            logger.error(f"Error in priority classification: {str(e)}")
            return {
                "priority": "medium",
                "confidence": 0.5,
                "error": str(e)
            }
    
    def _extract_features(self, data: Dict[str, Any]) -> List[float]:
        """Extract numerical features from emergency data."""
        features = []
        
        # Extract vital signs and clinical data
        vital_signs = data.get("vital_signs", {})
        
        features.append(data.get("age", 50))  # Default age
        features.append(vital_signs.get("heart_rate", 80))
        features.append(vital_signs.get("blood_pressure_systolic", 120))
        features.append(vital_signs.get("blood_pressure_diastolic", 80))
        features.append(vital_signs.get("respiratory_rate", 16))
        features.append(vital_signs.get("temperature", 98.6))
        features.append(vital_signs.get("oxygen_saturation", 98))
        features.append(data.get("pain_score", 5))
        features.append(data.get("consciousness_level", 15))  # GCS score
        features.append(self._assess_mechanism_of_injury(data))
        
        return features
    
    def _assess_mechanism_of_injury(self, data: Dict[str, Any]) -> float:
        """Assess mechanism of injury severity score."""
        complaint = data.get("chief_complaint", "").lower()
        
        high_risk_keywords = ["trauma", "accident", "fall", "assault", "gunshot"]
        moderate_risk_keywords = ["chest pain", "shortness of breath", "stroke"]
        
        if any(keyword in complaint for keyword in high_risk_keywords):
            return 8.0
        elif any(keyword in complaint for keyword in moderate_risk_keywords):
            return 6.0
        else:
            return 3.0
    
    async def _load_pretrained_model(self):
        """Load pre-trained model if available."""
        # This would load from a file in production
        # For now, we'll create a simple trained model
        
        # Generate some synthetic training data
        np.random.seed(42)
        X_train = np.random.randn(1000, len(self.feature_names))
        y_train = np.random.randint(0, 4, 1000)
        
        # Train the model
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        self.model.fit(X_train_scaled, y_train)
        
        self.is_trained = True


class ResourceDemandPredictor:
    """ML model for predicting resource demand during emergencies."""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
    
    async def predict_demand(
        self,
        current_cases: List[Dict[str, Any]],
        facility_capacity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict resource demand based on current cases."""
        try:
            # Calculate current demand metrics
            demand_metrics = self._calculate_demand_metrics(current_cases, facility_capacity)
            
            # Predict future demand (simplified)
            predicted_demand = {
                "beds": demand_metrics["current_bed_usage"] * 1.2,
                "ventilators": demand_metrics["current_ventilator_usage"] * 1.1,
                "staff": demand_metrics["current_staff_usage"] * 1.15,
                "imaging": demand_metrics["current_imaging_usage"] * 1.3
            }
            
            # Calculate strain levels
            strain_levels = {}
            for resource, demand in predicted_demand.items():
                capacity = facility_capacity.get(f"{resource}_capacity", 100)
                strain = demand / capacity if capacity > 0 else 1.0
                
                if strain > 0.9:
                    strain_levels[resource] = "critical"
                elif strain > 0.7:
                    strain_levels[resource] = "high"
                elif strain > 0.5:
                    strain_levels[resource] = "moderate"
                else:
                    strain_levels[resource] = "low"
            
            return {
                "predicted_demand": predicted_demand,
                "strain_levels": strain_levels,
                "recommendations": self._generate_demand_recommendations(strain_levels),
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Error predicting resource demand: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_demand_metrics(
        self,
        cases: List[Dict[str, Any]],
        capacity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate current demand metrics."""
        return {
            "current_bed_usage": len(cases),
            "current_ventilator_usage": sum(1 for case in cases if case.get("needs_ventilator", False)),
            "current_staff_usage": len(cases) * 0.3,  # Rough estimate
            "current_imaging_usage": sum(1 for case in cases if case.get("needs_imaging", False))
        }
    
    def _generate_demand_recommendations(self, strain_levels: Dict[str, str]) -> List[str]:
        """Generate recommendations based on strain levels."""
        recommendations = []
        
        for resource, strain in strain_levels.items():
            if strain == "critical":
                recommendations.append(f"URGENT: {resource} capacity critically strained - consider overflow protocols")
            elif strain == "high":
                recommendations.append(f"WARNING: {resource} capacity highly strained - prepare contingency plans")
        
        return recommendations


# Additional specialized models would be implemented similarly
class CTStrokeModel(BaseImagingModel):
    """Placeholder for CT stroke detection model."""
    
    def __init__(self, device: torch.device):
        super().__init__(device)
        # Implementation would include specialized stroke detection architecture
    
    async def predict(self, images: torch.Tensor) -> Dict[str, Any]:
        return {"findings": [], "confidence": 0.0}


class CTPulmonaryEmbolismModel(BaseImagingModel):
    """Placeholder for CT pulmonary embolism detection model."""
    
    def __init__(self, device: torch.device):
        super().__init__(device)
    
    async def predict(self, images: torch.Tensor) -> Dict[str, Any]:
        return {"findings": [], "confidence": 0.0}


class FractureDetectionModel(BaseImagingModel):
    """Placeholder for fracture detection model."""
    
    def __init__(self, device: torch.device):
        super().__init__(device)
    
    async def predict(self, images: torch.Tensor) -> Dict[str, Any]:
        return {"findings": [], "confidence": 0.0}


class BrainMRIModel(BaseImagingModel):
    """Placeholder for brain MRI analysis model."""
    
    def __init__(self, device: torch.device):
        super().__init__(device)
    
    async def predict(self, images: torch.Tensor) -> Dict[str, Any]:
        return {"findings": [], "confidence": 0.0}


class SpineMRIModel(BaseImagingModel):
    """Placeholder for spine MRI analysis model."""
    
    def __init__(self, device: torch.device):
        super().__init__(device)
    
    async def predict(self, images: torch.Tensor) -> Dict[str, Any]:
        return {"findings": [], "confidence": 0.0}


class CardiacUltrasoundModel(BaseImagingModel):
    """Placeholder for cardiac ultrasound analysis model."""
    
    def __init__(self, device: torch.device):
        super().__init__(device)
    
    async def predict(self, images: torch.Tensor) -> Dict[str, Any]:
        return {"findings": [], "confidence": 0.0}


class FASTExamModel(BaseImagingModel):
    """Placeholder for FAST exam analysis model."""
    
    def __init__(self, device: torch.device):
        super().__init__(device)
    
    async def predict(self, images: torch.Tensor) -> Dict[str, Any]:
        return {"findings": [], "confidence": 0.0}
