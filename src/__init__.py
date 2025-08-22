"""
ERAIF - Emergency Radiology AI Interoperability Framework

A vendor-neutral framework for medical imaging system interoperability
during emergency situations.
"""

__version__ = "1.0.0"
__author__ = "Darshan Shah"
__email__ = "info@eraif.org"

from .eraif_core import ERAIFCore
from .main import main

__all__ = ["ERAIFCore", "main"]
