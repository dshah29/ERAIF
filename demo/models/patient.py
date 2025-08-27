"""
ERAIF Patient Data Models

This module contains data models for patient information including
demographics, emergency contacts, and medical record numbers.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List
from enum import Enum
import hashlib
import uuid


class Gender(str, Enum):
    """Patient gender options."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class BloodType(str, Enum):
    """Blood type options."""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    UNKNOWN = "unknown"


@dataclass
class Demographics:
    """Patient demographic information."""
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender = Gender.UNKNOWN
    middle_name: Optional[str] = None
    suffix: Optional[str] = None
    prefix: Optional[str] = None
    ethnicity: Optional[str] = None
    race: Optional[str] = None
    language: Optional[str] = None
    marital_status: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get patient's full name."""
        parts = []
        if self.prefix:
            parts.append(self.prefix)
        parts.append(self.first_name)
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)
    
    @property
    def age(self) -> int:
        """Calculate patient's age."""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth.isoformat(),
            "gender": self.gender.value,
            "middle_name": self.middle_name,
            "suffix": self.suffix,
            "prefix": self.prefix,
            "ethnicity": self.ethnicity,
            "race": self.race,
            "language": self.language,
            "marital_status": self.marital_status
        }


@dataclass
class EmergencyContact:
    """Emergency contact information."""
    name: str
    relationship: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    is_primary: bool = True
    can_consent: bool = False
    notes: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "relationship": self.relationship,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "is_primary": self.is_primary,
            "can_consent": self.can_consent,
            "notes": self.notes
        }


@dataclass
class MedicalHistory:
    """Patient medical history information."""
    allergies: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    surgeries: List[str] = field(default_factory=list)
    family_history: List[str] = field(default_factory=list)
    social_history: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "allergies": self.allergies,
            "medications": self.medications,
            "conditions": self.conditions,
            "surgeries": self.surgeries,
            "family_history": self.family_history,
            "social_history": self.social_history
        }


@dataclass
class Patient:
    """Complete patient record."""
    demographics: Demographics
    patient_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mrn: Optional[str] = None  # Medical Record Number
    emergency_contacts: List[EmergencyContact] = field(default_factory=list)
    medical_history: Optional[MedicalHistory] = None
    insurance: Optional[str] = None
    primary_care_physician: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_active: bool = True
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if not self.created_at:
            self.created_at = date.today().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    @property
    def full_name(self) -> str:
        """Get patient's full name."""
        return self.demographics.full_name
    
    @property
    def age(self) -> int:
        """Get patient's age."""
        return self.demographics.age
    
    @property
    def primary_contact(self) -> Optional[EmergencyContact]:
        """Get primary emergency contact."""
        for contact in self.emergency_contacts:
            if contact.is_primary:
                return contact
        return self.emergency_contacts[0] if self.emergency_contacts else None
    
    def add_emergency_contact(self, contact: EmergencyContact):
        """Add an emergency contact."""
        if contact.is_primary:
            # Remove primary flag from existing contacts
            for existing in self.emergency_contacts:
                existing.is_primary = False
        self.emergency_contacts.append(contact)
    
    def remove_emergency_contact(self, contact_id: str):
        """Remove an emergency contact by ID."""
        self.emergency_contacts = [
            c for c in self.emergency_contacts 
            if c.name != contact_id
        ]
    
    def update_medical_history(self, history: MedicalHistory):
        """Update medical history."""
        self.medical_history = history
        self.updated_at = date.today().isoformat()
    
    def generate_hash(self) -> str:
        """Generate a hash for patient identification."""
        content = f"{self.mrn}{self.demographics.first_name}{self.demographics.last_name}{self.demographics.date_of_birth}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "patient_id": self.patient_id,
            "mrn": self.mrn,
            "demographics": self.demographics.to_dict(),
            "emergency_contacts": [c.to_dict() for c in self.emergency_contacts],
            "medical_history": self.medical_history.to_dict() if self.medical_history else None,
            "insurance": self.insurance,
            "primary_care_physician": self.primary_care_physician,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Patient':
        """Create Patient instance from dictionary."""
        demographics = Demographics(
            first_name=data['demographics']['first_name'],
            last_name=data['demographics']['last_name'],
            date_of_birth=date.fromisoformat(data['demographics']['date_of_birth']),
            gender=Gender(data['demographics']['gender']),
            middle_name=data['demographics'].get('middle_name'),
            suffix=data['demographics'].get('suffix'),
            prefix=data['demographics'].get('prefix'),
            ethnicity=data['demographics'].get('ethnicity'),
            race=data['demographics'].get('race'),
            language=data['demographics'].get('language'),
            marital_status=data['demographics'].get('marital_status')
        )
        
        emergency_contacts = []
        for contact_data in data.get('emergency_contacts', []):
            contact = EmergencyContact(
                name=contact_data['name'],
                relationship=contact_data['relationship'],
                phone=contact_data['phone'],
                email=contact_data.get('email'),
                address=contact_data.get('address'),
                is_primary=contact_data.get('is_primary', False),
                can_consent=contact_data.get('can_consent', False),
                notes=contact_data.get('notes')
            )
            emergency_contacts.append(contact)
        
        medical_history = None
        if data.get('medical_history'):
            history_data = data['medical_history']
            medical_history = MedicalHistory(
                allergies=history_data.get('allergies', []),
                medications=history_data.get('medications', []),
                conditions=history_data.get('conditions', []),
                surgeries=history_data.get('surgeries', []),
                family_history=history_data.get('family_history', []),
                social_history=history_data.get('social_history')
            )
        
        return cls(
            patient_id=data.get('patient_id'),
            mrn=data.get('mrn'),
            demographics=demographics,
            emergency_contacts=emergency_contacts,
            medical_history=medical_history,
            insurance=data.get('insurance'),
            primary_care_physician=data.get('primary_care_physician'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            is_active=data.get('is_active', True)
        )
