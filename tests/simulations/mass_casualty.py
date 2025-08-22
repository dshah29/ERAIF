#!/usr/bin/env python3
"""
Mass Casualty Event Simulation

This simulation tests ERAIF's response to a mass casualty incident,
focusing on rapid patient triage, imaging prioritization, and
multi-facility coordination.
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from enum import Enum

from src.eraif_core import ERAIFCore
from src.models.emergency import EmergencyMode
from src.models.study import Study
from src.models.patient import Patient


class TriageLevel(Enum):
    """Triage priority levels."""
    RED = "immediate"      # Life-threatening
    YELLOW = "urgent"      # Urgent but stable
    GREEN = "delayed"      # Walking wounded
    BLACK = "deceased"     # Deceased/expectant


class MassCasualtyScenario:
    """Simulate a mass casualty incident."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {
            "emergency": {
                "triggers": [
                    {"type": "mass_casualty", "threshold": 10},
                    {"type": "resource_overload", "threshold": 80}
                ],
                "disaster_mode": {
                    "compression": False,  # Need full quality for trauma
                    "priority_filter": ["CRITICAL", "HIGH", "URGENT"],
                    "batch_size": 20,  # Larger batches for efficiency
                    "parallel_processing": True
                }
            },
            "scenario": {
                "name": "Multi-Vehicle Highway Accident",
                "location": "Interstate 95, Mile Marker 147",
                "casualties": 85,
                "receiving_hospitals": [
                    {"id": "HOSP001_TRAUMA_L1", "capacity": 30, "trauma_level": 1},
                    {"id": "HOSP002_GENERAL", "capacity": 25, "trauma_level": 2},
                    {"id": "HOSP003_REGIONAL", "capacity": 20, "trauma_level": 3},
                    {"id": "HOSP004_SPECIALTY", "capacity": 15, "trauma_level": 2}
                ],
                "imaging_priorities": {
                    "RED": ["CT_HEAD", "CT_CHEST", "CT_ABDOMEN", "XRAY_CHEST"],
                    "YELLOW": ["CT_SPINE", "XRAY_EXTREMITY", "ULTRASOUND"],
                    "GREEN": ["XRAY_BASIC", "ULTRASOUND_LIMITED"]
                }
            }
        }
        
        self.eraif_core = None
        self.casualties = []
        self.hospital_status = {}
        self.simulation_data = {
            "total_casualties": 0,
            "casualties_by_triage": {"RED": 0, "YELLOW": 0, "GREEN": 0, "BLACK": 0},
            "studies_ordered": 0,
            "studies_completed": 0,
            "avg_door_to_scan_time": [],
            "hospital_utilization": {},
            "timeline": []
        }
    
    async def initialize(self):
        """Initialize the mass casualty scenario."""
        self.logger.info("Initializing Mass Casualty Scenario...")
        
        self.eraif_core = ERAIFCore(self.config)
        await self.eraif_core.initialize()
        
        # Initialize hospital status
        for hospital in self.config["scenario"]["receiving_hospitals"]:
            self.hospital_status[hospital["id"]] = {
                "current_patients": 0,
                "capacity": hospital["capacity"],
                "trauma_level": hospital["trauma_level"],
                "imaging_queue": [],
                "available_scanners": {
                    "CT": 2 if hospital["trauma_level"] == 1 else 1,
                    "MRI": 1,
                    "XRAY": 3,
                    "ULTRASOUND": 2
                }
            }
        
        self.logger.info("Mass casualty scenario initialized")
    
    async def run_simulation(self):
        """Run the complete mass casualty simulation."""
        try:
            await self.initialize()
            
            self.logger.warning("🚨 MASS CASUALTY INCIDENT SIMULATION STARTING")
            self.log_event("INCIDENT_START", "Multi-vehicle accident on Interstate 95")
            
            # Phase 1: Incident response and activation (0-15 minutes)
            await self.phase_1_activation()
            
            # Phase 2: Patient arrival surge (15-60 minutes)
            await self.phase_2_patient_surge()
            
            # Phase 3: Sustained operations (1-4 hours)
            await self.phase_3_sustained_ops()
            
            # Phase 4: Demobilization (4-6 hours)
            await self.phase_4_demobilization()
            
            # Generate final report
            await self.generate_report()
            
        except Exception as e:
            self.logger.error(f"Simulation failed: {e}")
            raise
        finally:
            if self.eraif_core:
                await self.eraif_core.shutdown()
    
    async def phase_1_activation(self):
        """Phase 1: Incident response and activation."""
        self.logger.info("🚨 Phase 1: Incident activation (0-15 minutes)")
        self.log_event("PHASE_1_START", "Mass casualty incident declared")
        
        # Activate emergency mode immediately
        await self.eraif_core.activate_emergency_mode(
            "Mass casualty incident: Multi-vehicle accident, 85+ casualties",
            "6h"
        )
        
        # Test all hospital systems
        for hospital_id in self.hospital_status.keys():
            await self.test_hospital_readiness(hospital_id)
        
        # Prepare receiving hospitals
        await self.prepare_hospitals()
        
        # Set up imaging priority protocols
        await self.configure_imaging_priorities()
        
        self.log_event("PHASE_1_COMPLETE", "All hospitals activated and ready")
    
    async def phase_2_patient_surge(self):
        """Phase 2: Patient arrival surge."""
        self.logger.warning("🏥 Phase 2: Patient surge (15-60 minutes)")
        self.log_event("PHASE_2_START", "First wave of casualties arriving")
        
        # Generate casualties with realistic distribution
        await self.generate_casualties()
        
        # Simulate patient arrivals in waves
        arrival_waves = [
            {"time": 0, "patients": 25, "severity_mix": [0.3, 0.4, 0.3, 0.0]},  # First responders
            {"time": 10, "patients": 35, "severity_mix": [0.2, 0.5, 0.25, 0.05]},  # Main wave
            {"time": 25, "patients": 20, "severity_mix": [0.15, 0.3, 0.5, 0.05]},  # Walking wounded
            {"time": 40, "patients": 5, "severity_mix": [0.4, 0.4, 0.2, 0.0]}   # Late arrivals
        ]
        
        for wave in arrival_waves:
            await asyncio.sleep(wave["time"] * 0.1)  # Compressed time
            await self.process_arrival_wave(wave)
        
        self.log_event("PHASE_2_COMPLETE", "Primary patient surge processed")
    
    async def phase_3_sustained_ops(self):
        """Phase 3: Sustained operations."""
        self.logger.info("⚕️ Phase 3: Sustained operations (1-4 hours)")
        self.log_event("PHASE_3_START", "Transition to sustained operations")
        
        # Continue processing patients and imaging studies
        for hour in range(3):  # 3 hours of sustained ops
            await asyncio.sleep(1.0)  # Compressed time
            
            # Process imaging queues
            await self.process_imaging_queues()
            
            # Handle transfers between hospitals
            await self.handle_hospital_transfers()
            
            # Monitor resource utilization
            await self.monitor_resources()
            
            self.logger.info(f"Hour {hour + 1}: "
                           f"Studies completed: {self.simulation_data['studies_completed']}, "
                           f"Queue backlog: {await self.get_total_queue_size()}")
        
        self.log_event("PHASE_3_COMPLETE", "Sustained operations phase complete")
    
    async def phase_4_demobilization(self):
        """Phase 4: Demobilization."""
        self.logger.info("📋 Phase 4: Demobilization (4-6 hours)")
        self.log_event("PHASE_4_START", "Beginning demobilization")
        
        # Process remaining imaging studies
        await self.clear_remaining_queues()
        
        # Generate patient disposition reports
        await self.generate_disposition_reports()
        
        # Deactivate emergency mode
        await self.eraif_core.deactivate_emergency_mode("Mass casualty incident resolved")
        
        self.log_event("PHASE_4_COMPLETE", "Demobilization complete")
    
    async def generate_casualties(self):
        """Generate realistic casualty distribution."""
        total_casualties = self.config["scenario"]["casualties"]
        
        # Realistic triage distribution for highway accident
        triage_distribution = {
            TriageLevel.RED: 0.15,     # 15% immediate
            TriageLevel.YELLOW: 0.35,  # 35% urgent
            TriageLevel.GREEN: 0.45,   # 45% delayed
            TriageLevel.BLACK: 0.05    # 5% deceased
        }
        
        casualty_id = 1
        for triage_level, percentage in triage_distribution.items():
            count = int(total_casualties * percentage)
            
            for _ in range(count):
                casualty = {
                    "id": f"MCI{casualty_id:03d}",
                    "triage": triage_level,
                    "age": random.randint(16, 85),
                    "gender": random.choice(["M", "F"]),
                    "injuries": self.generate_injuries(triage_level),
                    "arrival_time": None,
                    "door_to_scan_time": None,
                    "hospital": None,
                    "studies_ordered": [],
                    "studies_completed": []
                }
                self.casualties.append(casualty)
                casualty_id += 1
        
        self.simulation_data["total_casualties"] = len(self.casualties)
        for casualty in self.casualties:
            self.simulation_data["casualties_by_triage"][casualty["triage"].name] += 1
        
        self.log_event("CASUALTIES_GENERATED", 
                      f"Generated {total_casualties} casualties with realistic distribution")
    
    def generate_injuries(self, triage_level: TriageLevel) -> List[str]:
        """Generate realistic injuries based on triage level."""
        injury_patterns = {
            TriageLevel.RED: [
                "Traumatic brain injury", "Tension pneumothorax", 
                "Massive hemorrhage", "Airway obstruction",
                "Unstable pelvic fracture", "Cardiac tamponade"
            ],
            TriageLevel.YELLOW: [
                "Stable chest trauma", "Long bone fractures",
                "Abdominal pain", "Spinal injury concern",
                "Burns 10-20% BSA", "Multiple lacerations"
            ],
            TriageLevel.GREEN: [
                "Minor lacerations", "Contusions", 
                "Sprains/strains", "Minor burns",
                "Anxiety/stress reaction", "Minor abrasions"
            ],
            TriageLevel.BLACK: [
                "Massive head trauma", "Incompatible with life",
                "Cardiac arrest >20 min", "Severe burns >80% BSA"
            ]
        }
        
        available_injuries = injury_patterns.get(triage_level, ["Unknown injury"])
        num_injuries = random.randint(1, 3) if triage_level != TriageLevel.BLACK else 1
        
        return random.sample(available_injuries, 
                           min(num_injuries, len(available_injuries)))
    
    async def process_arrival_wave(self, wave: Dict[str, Any]):
        """Process a wave of arriving patients."""
        wave_casualties = []
        
        # Select casualties for this wave based on severity mix
        remaining_casualties = [c for c in self.casualties if c["arrival_time"] is None]
        
        for i, percentage in enumerate(wave["severity_mix"]):
            triage_level = list(TriageLevel)[i]
            count = int(wave["patients"] * percentage)
            
            available = [c for c in remaining_casualties if c["triage"] == triage_level]
            selected = available[:count]
            
            for casualty in selected:
                casualty["arrival_time"] = datetime.utcnow()
                wave_casualties.append(casualty)
        
        # Assign patients to hospitals
        for casualty in wave_casualties:
            hospital = await self.assign_to_hospital(casualty)
            casualty["hospital"] = hospital
            
            # Order imaging studies based on triage and injuries
            await self.order_imaging_studies(casualty)
        
        self.log_event("WAVE_PROCESSED", 
                      f"Processed wave: {len(wave_casualties)} patients")
    
    async def assign_to_hospital(self, casualty: Dict[str, Any]) -> str:
        """Assign patient to most appropriate hospital."""
        # Priority assignment based on triage level and hospital capabilities
        if casualty["triage"] == TriageLevel.RED:
            # Critical patients go to Level 1 trauma centers first
            for hospital in self.config["scenario"]["receiving_hospitals"]:
                if (hospital["trauma_level"] == 1 and 
                    self.hospital_status[hospital["id"]]["current_patients"] < 
                    hospital["capacity"]):
                    self.hospital_status[hospital["id"]]["current_patients"] += 1
                    return hospital["id"]
        
        # Find hospital with capacity
        for hospital in self.config["scenario"]["receiving_hospitals"]:
            if (self.hospital_status[hospital["id"]]["current_patients"] < 
                hospital["capacity"]):
                self.hospital_status[hospital["id"]]["current_patients"] += 1
                return hospital["id"]
        
        # If all hospitals at capacity, assign to least full Level 1 center
        level_1_hospitals = [h for h in self.config["scenario"]["receiving_hospitals"] 
                           if h["trauma_level"] == 1]
        
        if level_1_hospitals:
            best_hospital = min(level_1_hospitals, 
                              key=lambda h: self.hospital_status[h["id"]]["current_patients"])
            self.hospital_status[best_hospital["id"]]["current_patients"] += 1
            return best_hospital["id"]
        
        # Fallback to first hospital
        hospital_id = self.config["scenario"]["receiving_hospitals"][0]["id"]
        self.hospital_status[hospital_id]["current_patients"] += 1
        return hospital_id
    
    async def order_imaging_studies(self, casualty: Dict[str, Any]):
        """Order appropriate imaging studies based on triage and injuries."""
        triage_level = casualty["triage"].name
        imaging_priorities = self.config["scenario"]["imaging_priorities"]
        
        if triage_level == "BLACK":
            return  # No imaging for deceased
        
        # Determine required studies based on injuries and triage
        required_studies = []
        
        if triage_level in imaging_priorities:
            base_studies = imaging_priorities[triage_level]
            
            # Add injury-specific studies
            for injury in casualty["injuries"]:
                if "head" in injury.lower() or "brain" in injury.lower():
                    required_studies.append("CT_HEAD")
                elif "chest" in injury.lower() or "pneumothorax" in injury.lower():
                    required_studies.extend(["CT_CHEST", "XRAY_CHEST"])
                elif "abdomen" in injury.lower():
                    required_studies.append("CT_ABDOMEN")
                elif "spine" in injury.lower():
                    required_studies.append("CT_SPINE")
                elif "fracture" in injury.lower():
                    required_studies.append("XRAY_EXTREMITY")
            
            # Remove duplicates and limit based on triage
            required_studies = list(set(required_studies + base_studies))
            
            # Limit studies for lower priority patients
            if triage_level == "GREEN":
                required_studies = required_studies[:2]
            elif triage_level == "YELLOW":
                required_studies = required_studies[:4]
        
        # Create study objects and add to hospital queue
        hospital_id = casualty["hospital"]
        for study_type in required_studies:
            study = Study(
                study_id=f"{casualty['id']}_{study_type}_{datetime.now().strftime('%H%M%S')}",
                patient_id=casualty["id"],
                modality=study_type.split("_")[0],
                priority="CRITICAL" if triage_level == "RED" else "HIGH" if triage_level == "YELLOW" else "NORMAL",
                body_part=study_type.split("_")[1] if "_" in study_type else "UNKNOWN"
            )
            
            casualty["studies_ordered"].append(study)
            self.hospital_status[hospital_id]["imaging_queue"].append(study)
            self.simulation_data["studies_ordered"] += 1
        
        # Record door-to-scan time (time from arrival to first study)
        if required_studies:
            door_to_scan = random.uniform(15, 45)  # 15-45 minutes
            casualty["door_to_scan_time"] = door_to_scan
            self.simulation_data["avg_door_to_scan_time"].append(door_to_scan)
    
    async def process_imaging_queues(self):
        """Process imaging queues at all hospitals."""
        for hospital_id, status in self.hospital_status.items():
            queue = status["imaging_queue"]
            scanners = status["available_scanners"]
            
            # Process studies based on available scanners
            studies_to_remove = []
            
            for study in queue:
                modality = study.modality
                if scanners.get(modality, 0) > 0:
                    # Scanner available, process study
                    await self.process_imaging_study(study, hospital_id)
                    studies_to_remove.append(study)
                    
                    # Simulate scanner occupancy
                    scanners[modality] -= 1
                    
                    # Schedule scanner to become available again
                    asyncio.create_task(self.free_scanner(hospital_id, modality, 
                                                        self.get_scan_duration(modality)))
            
            # Remove processed studies from queue
            for study in studies_to_remove:
                queue.remove(study)
    
    async def process_imaging_study(self, study: Study, hospital_id: str):
        """Process a single imaging study."""
        # Find the casualty
        casualty = next((c for c in self.casualties if c["id"] == study.patient_id), None)
        if casualty:
            casualty["studies_completed"].append(study)
            self.simulation_data["studies_completed"] += 1
            
            # Log critical findings for RED triage patients
            if casualty["triage"] == TriageLevel.RED:
                await self.generate_critical_findings(study, casualty)
    
    async def generate_critical_findings(self, study: Study, casualty: Dict[str, Any]):
        """Generate and report critical findings."""
        critical_findings = {
            "CT_HEAD": ["Epidural hematoma", "Subdural hematoma", "Cerebral contusion"],
            "CT_CHEST": ["Tension pneumothorax", "Hemothorax", "Aortic injury"],
            "CT_ABDOMEN": ["Splenic laceration", "Liver laceration", "Retroperitoneal bleeding"]
        }
        
        study_type = f"{study.modality}_{study.body_part}"
        if study_type in critical_findings:
            finding = random.choice(critical_findings[study_type])
            
            self.log_event("CRITICAL_FINDING", 
                          f"{casualty['id']}: {finding} found on {study_type}")
            
            # In real system, this would trigger alerts and priority notifications
    
    async def free_scanner(self, hospital_id: str, modality: str, duration: float):
        """Free up a scanner after scan completion."""
        await asyncio.sleep(duration)
        self.hospital_status[hospital_id]["available_scanners"][modality] += 1
    
    def get_scan_duration(self, modality: str) -> float:
        """Get realistic scan duration in compressed time."""
        durations = {
            "CT": 0.1,        # ~5 minutes real time
            "MRI": 0.3,       # ~15 minutes real time
            "XRAY": 0.05,     # ~2 minutes real time
            "ULTRASOUND": 0.1 # ~5 minutes real time
        }
        return durations.get(modality, 0.1)
    
    async def get_total_queue_size(self) -> int:
        """Get total number of studies in all queues."""
        return sum(len(status["imaging_queue"]) for status in self.hospital_status.values())
    
    async def test_hospital_readiness(self, hospital_id: str):
        """Test individual hospital emergency readiness."""
        # Simulate hospital readiness test
        test_results = {
            "imaging_systems": random.choice([True, True, True, False]),  # 75% success
            "network_connectivity": random.choice([True, True, False]),   # 67% success
            "staff_availability": True,  # Always available in simulation
            "bed_capacity": True
        }
        
        overall_ready = all(test_results.values())
        status = "READY" if overall_ready else "DEGRADED"
        
        self.log_event("HOSPITAL_TEST", f"{hospital_id}: {status}")
        return overall_ready
    
    async def prepare_hospitals(self):
        """Prepare all receiving hospitals."""
        for hospital_id in self.hospital_status.keys():
            # Clear non-emergency patients (simulated)
            # Prepare additional imaging capacity
            # Staff emergency departments
            self.log_event("HOSPITAL_PREP", f"{hospital_id}: Emergency preparations complete")
    
    async def configure_imaging_priorities(self):
        """Configure imaging priority protocols."""
        # Set up priority queuing
        # Configure automatic routing
        # Enable emergency protocols
        self.log_event("IMAGING_CONFIG", "Emergency imaging protocols activated")
    
    async def handle_hospital_transfers(self):
        """Handle transfers between hospitals."""
        # Check for hospitals at capacity
        overloaded_hospitals = [
            h_id for h_id, status in self.hospital_status.items()
            if status["current_patients"] > status["capacity"] * 0.9
        ]
        
        for hospital_id in overloaded_hospitals:
            # Find patients who can be transferred
            transferable_patients = [
                c for c in self.casualties 
                if (c["hospital"] == hospital_id and 
                    c["triage"] in [TriageLevel.YELLOW, TriageLevel.GREEN])
            ]
            
            if transferable_patients:
                # Transfer to hospital with capacity
                for receiving_hospital in self.config["scenario"]["receiving_hospitals"]:
                    if (self.hospital_status[receiving_hospital["id"]]["current_patients"] < 
                        receiving_hospital["capacity"]):
                        
                        patient = transferable_patients[0]
                        patient["hospital"] = receiving_hospital["id"]
                        
                        self.hospital_status[hospital_id]["current_patients"] -= 1
                        self.hospital_status[receiving_hospital["id"]]["current_patients"] += 1
                        
                        self.log_event("PATIENT_TRANSFER", 
                                      f"{patient['id']}: {hospital_id} → {receiving_hospital['id']}")
                        break
    
    async def monitor_resources(self):
        """Monitor resource utilization across all hospitals."""
        for hospital_id, status in self.hospital_status.items():
            utilization = (status["current_patients"] / status["capacity"]) * 100
            self.simulation_data["hospital_utilization"][hospital_id] = utilization
            
            if utilization > 90:
                self.log_event("CAPACITY_WARNING", 
                              f"{hospital_id}: {utilization:.1f}% capacity")
    
    async def clear_remaining_queues(self):
        """Clear all remaining imaging queues."""
        total_remaining = await self.get_total_queue_size()
        
        if total_remaining > 0:
            self.log_event("QUEUE_CLEARING", f"Processing {total_remaining} remaining studies")
            
            # Process all remaining studies rapidly
            for hospital_id, status in self.hospital_status.items():
                for study in status["imaging_queue"]:
                    await self.process_imaging_study(study, hospital_id)
                status["imaging_queue"].clear()
    
    async def generate_disposition_reports(self):
        """Generate patient disposition reports."""
        dispositions = {
            "admitted": 0,
            "discharged": 0,
            "transferred": 0,
            "deceased": 0
        }
        
        for casualty in self.casualties:
            if casualty["triage"] == TriageLevel.BLACK:
                dispositions["deceased"] += 1
            elif casualty["triage"] == TriageLevel.RED:
                dispositions["admitted"] += 1
            elif casualty["triage"] == TriageLevel.YELLOW:
                if random.random() < 0.7:
                    dispositions["admitted"] += 1
                else:
                    dispositions["discharged"] += 1
            else:  # GREEN
                dispositions["discharged"] += 1
        
        self.log_event("DISPOSITION_REPORT", 
                      f"Final: {dispositions['admitted']} admitted, "
                      f"{dispositions['discharged']} discharged, "
                      f"{dispositions['deceased']} deceased")
    
    def log_event(self, event_type: str, description: str):
        """Log simulation event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "description": description
        }
        self.simulation_data["timeline"].append(event)
        self.logger.info(f"[{event_type}] {description}")
    
    async def generate_report(self):
        """Generate final simulation report."""
        self.logger.info("\n" + "="*60)
        self.logger.info("🚨 MASS CASUALTY SIMULATION REPORT")
        self.logger.info("="*60)
        
        stats = self.simulation_data
        
        # Casualty statistics
        self.logger.info(f"Total Casualties: {stats['total_casualties']}")
        for triage, count in stats['casualties_by_triage'].items():
            percentage = (count / stats['total_casualties']) * 100
            self.logger.info(f"  {triage}: {count} ({percentage:.1f}%)")
        
        # Imaging statistics
        self.logger.info(f"\nImaging Studies:")
        self.logger.info(f"  Ordered: {stats['studies_ordered']}")
        self.logger.info(f"  Completed: {stats['studies_completed']}")
        completion_rate = (stats['studies_completed'] / stats['studies_ordered']) * 100
        self.logger.info(f"  Completion Rate: {completion_rate:.1f}%")
        
        # Timing metrics
        if stats['avg_door_to_scan_time']:
            avg_time = sum(stats['avg_door_to_scan_time']) / len(stats['avg_door_to_scan_time'])
            self.logger.info(f"  Average Door-to-Scan Time: {avg_time:.1f} minutes")
        
        # Hospital utilization
        self.logger.info(f"\nHospital Utilization:")
        for hospital_id, utilization in stats['hospital_utilization'].items():
            self.logger.info(f"  {hospital_id}: {utilization:.1f}%")
        
        self.logger.info("="*60)
        
        # Performance assessment
        self.logger.info("PERFORMANCE ASSESSMENT:")
        if completion_rate > 90:
            self.logger.info("✅ EXCELLENT: >90% imaging completion rate")
        elif completion_rate > 80:
            self.logger.info("✅ GOOD: >80% imaging completion rate")
        elif completion_rate > 70:
            self.logger.info("⚠️ ACCEPTABLE: >70% imaging completion rate")
        else:
            self.logger.info("❌ NEEDS IMPROVEMENT: <70% imaging completion rate")
        
        return stats


async def main():
    """Run the mass casualty scenario simulation."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scenario = MassCasualtyScenario()
    
    try:
        results = await scenario.run_simulation()
        print(f"\n✅ Simulation completed successfully!")
        print(f"📊 Final stats: {results}")
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
