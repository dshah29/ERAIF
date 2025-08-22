#!/usr/bin/env python3
"""
ERAIF Setup Script

Setup script for the Emergency Radiology AI Interoperability Framework.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="eraif",
    version="1.0.0",
    author="Darshan Shah",
    author_email="info@eraif.org",
    description="Emergency Radiology AI Interoperability Framework",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/dshah29/ERAIF",
    project_urls={
        "Bug Tracker": "https://github.com/dshah29/ERAIF/issues",
        "Documentation": "https://docs.eraif.org",
        "Source Code": "https://github.com/dshah29/ERAIF",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Framework :: FastAPI",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "isort>=5.12.0",
        ],
        "docs": [
            "mkdocs>=1.5.3",
            "mkdocs-material>=9.4.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "eraif-server=src.main:main",
            "eraif-setup=scripts.setup:main",
            "eraif-test-hurricane=tests.simulations.hurricane_scenario:main",
            "eraif-test-mass-casualty=tests.simulations.mass_casualty:main",
            "eraif-test-cyber-attack=tests.simulations.cyber_attack:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "*.yml",
            "*.yaml",
            "*.json",
            "*.conf",
            "*.md",
        ],
    },
    keywords=[
        "emergency medicine",
        "radiology",
        "interoperability", 
        "DICOM",
        "HL7 FHIR",
        "artificial intelligence",
        "disaster response",
        "healthcare IT",
        "medical imaging",
        "PACS",
        "RIS",
    ],
    zip_safe=False,
)
