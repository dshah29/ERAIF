#!/usr/bin/env python3
"""
ERAIF Demo Runner

This is the main entry point for running the ERAIF demo.
Run this script from the demo directory.
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from scripts.demo_with_data import main

if __name__ == "__main__":
    print("🚨 ERAIF Demo Runner")
    print("=" * 30)
    print("Starting the ERAIF system demonstration...")
    print()
    
    # Run the main demo
    exit(main())



