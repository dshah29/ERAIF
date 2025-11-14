#!/usr/bin/env python3
"""
ERAIF Demo Launcher

Enhanced demo launcher with AI/ML capabilities and multiple demo modes.
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Add paths to system
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "demo"))

def print_banner():
    """Print ERAIF demo banner."""
    print("🚨 ERAIF - Emergency Radiology AI Interoperability Framework")
    print("=" * 60)
    print("🤖 AI-Powered Emergency Response & Medical Imaging Analysis")
    print("🔗 LangGraph Workflows & Intelligent Decision Support")
    print("=" * 60)
    print()

def show_demo_menu():
    """Show available demo options."""
    print("Select a demo mode:")
    print()
    print("1. 🤖 AI/ML Demo - Advanced AI-powered emergency analysis")
    print("   • Intelligent triage with machine learning")
    print("   • Medical imaging analysis with deep learning")
    print("   • LangGraph workflow orchestration")
    print("   • Mass casualty incident coordination")
    print("   • Real-time decision support")
    print()
    print("2. 📊 Classic Demo - Original ERAIF system demonstration")
    print("   • Basic emergency protocols")
    print("   • System interoperability")
    print("   • Data management")
    print()
    print("3. 🎮 Interactive Web Demo - Browser-based demonstration")
    print("   • Visual interface")
    print("   • Real-time updates")
    print("   • Interactive scenarios")
    print()
    print("4. 🏥 Hospital to Clinic Transfer Example")
    print("   • Real-world protocol demonstration")
    print("   • HIPAA-compliant data transfer")
    print("   • DICOM imaging study transfer")
    print("   • AI analysis results sharing")
    print("   • Complete audit trail")
    print()
    print("5. 🔗 FHIR R4 Emergency Transfer Example")
    print("   • HL7 FHIR R4 standard integration")
    print("   • Interoperability with EHR systems")
    print("   • Emergency radiology workflows")
    print("   • AI analysis with FHIR extensions")
    print("   • FHIR resource conversion")
    print()
    print("0. Exit")
    print()

async def run_ai_demo():
    """Run the AI/ML demo."""
    try:
        from demo.scripts.ai_demo import main as ai_main
        await ai_main()
    except ImportError as e:
        print(f"❌ Error importing AI demo: {e}")
        print("   Make sure all AI dependencies are installed:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error running AI demo: {e}")

def run_classic_demo():
    """Run the classic demo."""
    demo_dir = Path(__file__).parent / "demo"

    if not demo_dir.exists():
        print("❌ Demo directory not found!")
        print(f"Expected: {demo_dir}")
        return 1

    print("📍 Running classic demo...")

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

def run_web_demo():
    """Run the web demo."""
    demo_html = Path(__file__).parent / "demo" / "demo.html"

    if demo_html.exists():
        print("🌐 Opening web demo in your default browser...")
        print(f"   File: {demo_html}")
        print()
        print("If the browser doesn't open automatically, navigate to:")
        print(f"   file://{demo_html.absolute()}")

        # Try to open in browser
        import webbrowser
        try:
            webbrowser.open(f"file://{demo_html.absolute()}")
            print("\n✅ Web demo opened successfully!")
            print("   Press Ctrl+C to return to the menu")

            # Keep the script running
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🔙 Returning to main menu...")

        except Exception as e:
            print(f"❌ Could not open browser: {e}")
    else:
        print("❌ Web demo file not found!")
        print(f"   Expected location: {demo_html}")

def run_hospital_clinic_example():
    """Run the hospital to clinic transfer example."""
    example_dir = Path(__file__).parent / "demo" / "examples"
    example_file = example_dir / "hospital_to_clinic_transfer.py"

    if not example_file.exists():
        print("❌ Hospital to clinic example not found!")
        print(f"   Expected: {example_file}")
        return 1

    print("🏥 Running hospital to clinic transfer example...")
    print()

    try:
        result = subprocess.run([sys.executable, 'hospital_to_clinic_transfer.py'],
                              cwd=example_dir, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Example failed with exit code: {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("❌ Python executable not found!")
        return 1

async def run_fhir_example():
    """Run the FHIR R4 emergency transfer example."""
    example_dir = Path(__file__).parent / "demo" / "examples"
    example_file = example_dir / "fhir_emergency_transfer.py"

    if not example_file.exists():
        print("❌ FHIR emergency transfer example not found!")
        print(f"   Expected: {example_file}")
        return 1

    print("🔗 Running FHIR R4 emergency transfer example...")
    print()

    try:
        result = subprocess.run([sys.executable, 'fhir_emergency_transfer.py'],
                              cwd=example_dir, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Example failed with exit code: {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("❌ Python executable not found!")
        return 1

async def main():
    """Main demo launcher."""
    print_banner()

    while True:
        show_demo_menu()

        try:
            choice = input("Enter your choice (0-5): ").strip()
            print()

            if choice == "1":
                print("🚀 Launching AI/ML Demo...")
                print("   Loading AI models and LangGraph workflows...")
                print()
                await run_ai_demo()

            elif choice == "2":
                print("🚀 Launching Classic Demo...")
                print()
                result = run_classic_demo()
                if result != 0:
                    print("❌ Classic demo exited with error")

            elif choice == "3":
                print("🚀 Launching Web Demo...")
                print()
                run_web_demo()

            elif choice == "4":
                print("🚀 Launching Hospital to Clinic Transfer Example...")
                print()
                result = run_hospital_clinic_example()
                if result != 0:
                    print("❌ Example exited with error")

            elif choice == "5":
                print("🚀 Launching FHIR R4 Emergency Transfer Example...")
                print()
                result = await run_fhir_example()
                if result != 0:
                    print("❌ Example exited with error")

            elif choice == "0":
                print("👋 Thank you for trying ERAIF!")
                print("   For more information, visit: https://eraif.org")
                break

            else:
                print("❌ Invalid choice. Please select 0-5.")

        except KeyboardInterrupt:
            print("\n\n⏸️  Demo interrupted by user.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

        print("\n" + "─" * 60 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
