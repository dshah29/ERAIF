#!/usr/bin/env python3
"""
Generate Sample Data for ERAIF Demo

This script generates realistic sample data including patients, studies,
and emergency scenarios for testing the ERAIF system.
"""

import sys
import os

# Add the demo directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.data_generator import ERAIFDataGenerator

def main():
    """Generate sample data for the ERAIF demo."""
    print("🚨 ERAIF Sample Data Generator")
    print("=" * 40)
    
    # Create data generator
    generator = ERAIFDataGenerator()
    
    # Generate a medium-sized dataset for demo purposes
    print("\nGenerating sample dataset...")
    dataset = generator.generate_sample_dataset(
        num_patients=25,  # 25 patients
        num_emergencies=4  # 4 emergency scenarios
    )
    
    # Save the dataset
    filename = "eraif_demo_dataset.json"
    generator.save_dataset(dataset, filename)
    
    print(f"\n✅ Sample data generated successfully!")
    print(f"📁 Dataset saved to: {filename}")
    print(f"📊 Dataset contains:")
    print(f"   - {dataset['metadata']['total_patients']} patients")
    print(f"   - {dataset['metadata']['total_studies']} imaging studies")
    print(f"   - {dataset['metadata']['total_emergencies']} emergency events")
    print(f"   - {dataset['metadata']['total_images']} total images")
    print(f"   - {dataset['metadata']['total_ai_analyses']} AI analyses")
    
    print(f"\n🎯 You can now:")
    print(f"   1. Use this data in your ERAIF demo")
    print(f"   2. Test patient lookup and study retrieval")
    print(f"   3. Simulate emergency scenarios")
    print(f"   4. Demonstrate AI analysis capabilities")
    
    print(f"\n📖 To use this data in your demo:")
    print(f"   - Load the JSON file in your application")
    print(f"   - Parse patients, studies, and emergencies")
    print(f"   - Display realistic information in your UI")
    
    return 0

if __name__ == "__main__":
    exit(main())
