"""
ERAIF Study Data Models

This module contains data models for imaging studies, image series,
and AI analysis results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class Modality(str, Enum):
    """Medical imaging modalities."""
    CT = "CT"
    MRI = "MRI"
    XR = "XR"  # X-Ray
    US = "US"  # Ultrasound
    NM = "NM"  # Nuclear Medicine
    CR = "CR"  # Computed Radiography
    DX = "DX"  # Digital Radiography
    MG = "MG"  # Mammography
    PT = "PT"  # Positron Emission Tomography
    SR = "SR"  # Structured Report


class BodyPart(str, Enum):
    """Anatomical body parts for imaging."""
    HEAD = "HEAD"
    NECK = "NECK"
    CHEST = "CHEST"
    ABDOMEN = "ABDOMEN"
    PELVIS = "PELVIS"
    SPINE = "SPINE"
    UPPER_EXTREMITY = "UPPER_EXTREMITY"
    LOWER_EXTREMITY = "LOWER_EXTREMITY"
    HEART = "HEART"
    BRAIN = "BRAIN"
    LUNG = "LUNG"
    LIVER = "LIVER"
    KIDNEY = "KIDNEY"
    UNKNOWN = "UNKNOWN"


class Urgency(str, Enum):
    """Study urgency levels."""
    ROUTINE = "ROUTINE"
    URGENT = "URGENT"
    STAT = "STAT"
    CRITICAL = "CRITICAL"
    LIFE_THREATENING = "LIFE_THREATENING"


class StudyStatus(str, Enum):
    """Study status options."""
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ON_HOLD = "ON_HOLD"
    ERROR = "ERROR"


class AIAnalysisStatus(str, Enum):
    """AI analysis status options."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class ImageSeries:
    """Individual image series within a study."""
    series_number: int
    modality: Modality
    body_part: BodyPart
    series_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: Optional[str] = None
    images: List[str] = field(default_factory=list)  # List of image file paths/URLs
    acquisition_date: Optional[datetime] = None
    institution: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    software_version: Optional[str] = None
    protocol_name: Optional[str] = None
    technique: Optional[str] = None
    kvp: Optional[float] = None  # Kilovoltage peak
    ma: Optional[float] = None   # Milliamperage
    exposure_time: Optional[float] = None
    slice_thickness: Optional[float] = None
    spacing: Optional[float] = None
    
    def __post_init__(self):
        """Initialize acquisition date if not provided."""
        if not self.acquisition_date:
            self.acquisition_date = datetime.now()
    
    @property
    def image_count(self) -> int:
        """Get the number of images in this series."""
        return len(self.images)
    
    def add_image(self, image_path: str):
        """Add an image to the series."""
        self.images.append(image_path)
    
    def remove_image(self, image_path: str):
        """Remove an image from the series."""
        if image_path in self.images:
            self.images.remove(image_path)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "series_id": self.series_id,
            "series_number": self.series_number,
            "modality": self.modality.value,
            "body_part": self.body_part.value,
            "description": self.description,
            "images": self.images,
            "acquisition_date": self.acquisition_date.isoformat() if self.acquisition_date else None,
            "institution": self.institution,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "software_version": self.software_version,
            "protocol_name": self.protocol_name,
            "technique": self.technique,
            "kvp": self.kvp,
            "ma": self.ma,
            "exposure_time": self.exposure_time,
            "slice_thickness": self.slice_thickness,
            "spacing": self.spacing
        }


@dataclass
class AIAnalysis:
    """AI analysis results for imaging studies."""
    model_name: str
    model_version: str
    analysis_type: str  # e.g., "detection", "segmentation", "classification"
    analysis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: AIAnalysisStatus = AIAnalysisStatus.PENDING
    confidence_score: Optional[float] = None
    results: Dict[str, Any] = field(default_factory=dict)
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    processing_time: Optional[float] = None  # seconds
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if not self.created_at:
            self.created_at = datetime.now()
    
    def add_finding(self, finding: str):
        """Add a finding to the analysis."""
        self.findings.append(finding)
    
    def add_recommendation(self, recommendation: str):
        """Add a recommendation to the analysis."""
        self.recommendations.append(recommendation)
    
    def set_result(self, key: str, value: Any):
        """Set a result value."""
        self.results[key] = value
    
    def mark_completed(self, confidence_score: float = None):
        """Mark analysis as completed."""
        self.status = AIAnalysisStatus.COMPLETED
        self.completed_at = datetime.now()
        if confidence_score is not None:
            self.confidence_score = confidence_score
    
    def mark_failed(self, error_message: str):
        """Mark analysis as failed."""
        self.status = AIAnalysisStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "analysis_id": self.analysis_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "analysis_type": self.analysis_type,
            "status": self.status.value,
            "confidence_score": self.confidence_score,
            "results": self.results,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "processing_time": self.processing_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message
        }


@dataclass
class Study:
    """Complete imaging study information."""
    patient_id: str
    modality: Modality
    body_part: BodyPart
    study_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    accession_number: Optional[str] = None
    study_date: Optional[datetime] = None
    study_time: Optional[datetime] = None
    urgency: Urgency = Urgency.ROUTINE
    status: StudyStatus = StudyStatus.SCHEDULED
    description: Optional[str] = None
    clinical_history: Optional[str] = None
    referring_physician: Optional[str] = None
    performing_physician: Optional[str] = None
    reading_physician: Optional[str] = None
    institution: Optional[str] = None
    series: List[ImageSeries] = field(default_factory=list)
    ai_analyses: List[AIAnalysis] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    @property
    def total_images(self) -> int:
        """Get total number of images across all series."""
        return sum(series.image_count for series in self.series)
    
    @property
    def series_count(self) -> int:
        """Get number of series in the study."""
        return len(self.series)
    
    @property
    def ai_analysis_count(self) -> int:
        """Get number of AI analyses for this study."""
        return len(self.ai_analyses)
    
    def add_series(self, series: ImageSeries):
        """Add an image series to the study."""
        self.series.append(series)
        self.updated_at = datetime.now()
    
    def remove_series(self, series_id: str):
        """Remove a series from the study."""
        self.series = [s for s in self.series if s.series_id != series_id]
        self.updated_at = datetime.now()
    
    def add_ai_analysis(self, analysis: AIAnalysis):
        """Add an AI analysis to the study."""
        self.ai_analyses.append(analysis)
        self.updated_at = datetime.now()
    
    def get_series_by_modality(self, modality: Modality) -> List[ImageSeries]:
        """Get all series of a specific modality."""
        return [s for s in self.series if s.modality == modality]
    
    def get_series_by_body_part(self, body_part: BodyPart) -> List[ImageSeries]:
        """Get all series of a specific body part."""
        return [s for s in self.series if s.body_part == body_part]
    
    def get_completed_ai_analyses(self) -> List[AIAnalysis]:
        """Get all completed AI analyses."""
        return [a for a in self.ai_analyses if a.status == AIAnalysisStatus.COMPLETED]
    
    def update_status(self, new_status: StudyStatus):
        """Update study status."""
        self.status = new_status
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "study_id": self.study_id,
            "patient_id": self.patient_id,
            "accession_number": self.accession_number,
            "study_date": self.study_date.isoformat() if self.study_date else None,
            "study_time": self.study_time.isoformat() if self.study_time else None,
            "modality": self.modality.value,
            "body_part": self.body_part.value,
            "urgency": self.urgency.value,
            "status": self.status.value,
            "description": self.description,
            "clinical_history": self.clinical_history,
            "referring_physician": self.referring_physician,
            "performing_physician": self.performing_physician,
            "reading_physician": self.reading_physician,
            "institution": self.institution,
            "series": [s.to_dict() for s in self.series],
            "ai_analyses": [a.to_dict() for a in self.ai_analyses],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Study':
        """Create Study instance from dictionary."""
        # Parse series
        series = []
        for series_data in data.get('series', []):
            series_obj = ImageSeries(
                series_id=series_data.get('series_id'),
                series_number=series_data['series_number'],
                modality=Modality(series_data['modality']),
                body_part=BodyPart(series_data['body_part']),
                description=series_data.get('description'),
                images=series_data.get('images', []),
                acquisition_date=datetime.fromisoformat(series_data['acquisition_date']) if series_data.get('acquisition_date') else None,
                institution=series_data.get('institution'),
                manufacturer=series_data.get('manufacturer'),
                model=series_data.get('model'),
                software_version=series_data.get('software_version'),
                protocol_name=series_data.get('protocol_name'),
                technique=series_data.get('technique'),
                kvp=series_data.get('kvp'),
                ma=series_data.get('ma'),
                exposure_time=series_data.get('exposure_time'),
                slice_thickness=series_data.get('slice_thickness'),
                spacing=series_data.get('spacing')
            )
            series.append(series_obj)
        
        # Parse AI analyses
        ai_analyses = []
        for analysis_data in data.get('ai_analyses', []):
            analysis_obj = AIAnalysis(
                analysis_id=analysis_data.get('analysis_id'),
                model_name=analysis_data['model_name'],
                model_version=analysis_data['model_version'],
                analysis_type=analysis_data['analysis_type'],
                status=AIAnalysisStatus(analysis_data.get('status', 'PENDING')),
                confidence_score=analysis_data.get('confidence_score'),
                results=analysis_data.get('results', {}),
                findings=analysis_data.get('findings', []),
                recommendations=analysis_data.get('recommendations', []),
                processing_time=analysis_data.get('processing_time'),
                created_at=datetime.fromisoformat(analysis_data['created_at']) if analysis_data.get('created_at') else None,
                completed_at=datetime.fromisoformat(analysis_data['completed_at']) if analysis_data.get('completed_at') else None,
                error_message=analysis_data.get('error_message')
            )
            ai_analyses.append(analysis_obj)
        
        return cls(
            study_id=data.get('study_id'),
            patient_id=data['patient_id'],
            accession_number=data.get('accession_number'),
            study_date=datetime.fromisoformat(data['study_date']) if data.get('study_date') else None,
            study_time=datetime.fromisoformat(data['study_time']) if data.get('study_time') else None,
            modality=Modality(data['modality']),
            body_part=BodyPart(data['body_part']),
            urgency=Urgency(data.get('urgency', 'ROUTINE')),
            status=StudyStatus(data.get('status', 'SCHEDULED')),
            description=data.get('description'),
            clinical_history=data.get('clinical_history'),
            referring_physician=data.get('referring_physician'),
            performing_physician=data.get('performing_physician'),
            reading_physician=data.get('reading_physician'),
            institution=data.get('institution'),
            series=series,
            ai_analyses=ai_analyses,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            metadata=data.get('metadata', {})
        )
