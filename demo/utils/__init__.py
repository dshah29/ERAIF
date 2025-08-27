"""
ERAIF Utilities Package

This package contains utility modules for the ERAIF system including
data generation, validation, and helper functions.
"""

from .data_generator import ERAIFDataGenerator, generate_quick_patient, generate_quick_study, generate_quick_emergency, generate_sample_data

__all__ = [
    "ERAIFDataGenerator",
    "generate_quick_patient", 
    "generate_quick_study",
    "generate_quick_emergency",
    "generate_sample_data"
]
