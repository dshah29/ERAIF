#!/usr/bin/env python3
"""
ERAIF Demo Launcher

Quick launcher for the ERAIF demo system.
Run this from the root ERAIF directory.
"""

import os
import subprocess
import sys

def main():
    """Launch the ERAIF demo."""
    print("🚨 ERAIF Demo Launcher")
    print("=" * 30)
    
    # Check if demo directory exists
    demo_dir = os.path.join(os.path.dirname(__file__), 'demo')
    if not os.path.exists(demo_dir):
        print("❌ Demo directory not found!")
        print(f"Expected: {demo_dir}")
        return 1
    
    # Change to demo directory and run
    os.chdir(demo_dir)
    
    print("📍 Changed to demo directory")
    print("🚀 Launching ERAIF demo...")
    print()
    
    # Run the demo
    try:
        result = subprocess.run([sys.executable, 'run_demo.py'], 
                              cwd=demo_dir, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo failed with exit code: {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("❌ Python executable not found!")
        return 1

if __name__ == "__main__":
    exit(main())
