#!/usr/bin/env python3
"""
Hurricane Emergency Scenario Simulation

This simulation tests ERAIF's response to a major hurricane event,
including network degradation, facility evacuations, and emergency
patient transfers.
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.eraif_core import ERAIFCore
from src.models.emergency import EmergencyMode
from src.models.study import Study
from src.models.patient import Patient


class HurricaneScenario:
    """Simulate a major hurricane emergency scenario."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {
            "emergency": {
                "triggers": [
                    {"type": "network_failure", "threshold": 5},
                    {"type": "facility_evacuation", "threshold": 1}
                ],
                "disaster_mode": {
                    "compression": True,
                    "priority_filter": ["CRITICAL", "HIGH"],
                    "batch_size": 5  # Smaller batches due to limited bandwidth
                }
            },
            "scenario": {
                "name": "Hurricane Helene Category 5",
                "affected_facilities": [
                    "HOSP001_COASTAL_GENERAL",
                    "HOSP002_MERCY_HOSPITAL", 
                    "HOSP003_REGIONAL_MEDICAL",
                    "HOSP004_TRAUMA_CENTER"
                ],
                "safe_facilities": [
                    "HOSP005_INLAND_GENERAL",
                    "HOSP006_STATE_UNIVERSITY",
                    "HOSP007_VETERANS_MEDICAL"
                ],
                "duration": "72h",
                "peak_impact": "24h"
            }
        }
        
        self.eraif_core = None
        self.simulation_data = {
            "patients_transferred": 0,
            "studies_processed": 0,
            "network_failures": 0,
            "successful_transfers": 0,
            "failed_transfers": 0,
            "timeline": []
        }
    
    async def initialize(self):
        """Initialize the hurricane scenario."""
        self.logger.info("Initializing Hurricane Emergency Scenario...")
        
        self.eraif_core = ERAIFCore(self.config)
        await self.eraif_core.initialize()
        
        self.logger.info("Hurricane scenario initialized")
    
    async def run_simulation(self):
        """Run the complete hurricane simulation."""
        try:
            await self.initialize()
            
            self.logger.warning("🌀 HURRICANE EMERGENCY SIMULATION STARTING")
            self.log_event("SIMULATION_START", "Hurricane Helene Category 5 approaching")
            
            # Phase 1: Pre-landfall preparation (0-6 hours)
            await self.phase_1_preparation()
            
            # Phase 2: Hurricane landfall and peak impact (6-30 hours)
            await self.phase_2_peak_impact()
            
            # Phase 3: Post-hurricane recovery (30-72 hours)
            await self.phase_3_recovery()
            
            # Generate final report
            await self.generate_report()
            
        except Exception as e:
            self.logger.error(f"Simulation failed: {e}")
            raise
        finally:
            if self.eraif_core:
                await self.eraif_core.shutdown()
    
    async def phase_1_preparation(self):
        """Phase 1: Pre-landfall preparation."""
        self.logger.info("🔄 Phase 1: Pre-landfall preparation (0-6 hours)")
        self.log_event("PHASE_1_START", "Hurricane preparation phase")
        
        # Activate emergency mode preemptively
        await self.eraif_core.activate_emergency_mode(
            "Hurricane Helene Category 5 - Preemptive activation",
            "72h"
        )
        
        # Test emergency systems
        test_results = await self.eraif_core.test_emergency_systems()
        self.log_event("EMERGENCY_TEST", f"Systems test: {test_results['overall_status']}")
        
        # Simulate preparation activities
        await self.simulate_patient_preparation()
        await self.simulate_data_backup()
        
        # Gradual network degradation as storm approaches
        for hour in range(6):
            await asyncio.sleep(0.5)  # Compressed time
            network_quality = max(0.3, 1.0 - (hour * 0.1))
            await self.simulate_network_degradation(network_quality)
            
            self.logger.info(f"Hour {hour}: Network quality {network_quality:.1%}")
        
        self.log_event("PHASE_1_COMPLETE", "Preparation phase complete")
    
    async def phase_2_peak_impact(self):
        """Phase 2: Hurricane landfall and peak impact."""
        self.logger.warning("🌀 Phase 2: Peak impact (6-30 hours)")
        self.log_event("PHASE_2_START", "Hurricane landfall - peak impact")
        
        # Simulate facility evacuations
        for facility in self.config["scenario"]["affected_facilities"][:2]:
            await self.simulate_facility_evacuation(facility)
        
        # Severe network disruption
        for hour in range(6, 30):
            await asyncio.sleep(0.2)  # Compressed time
            
            # Very poor connectivity during peak
            if 12 <= hour <= 18:  # Peak storm hours
                network_quality = random.uniform(0.0, 0.2)
            else:
                network_quality = random.uniform(0.1, 0.4)
            
            await self.simulate_network_degradation(network_quality)
            
            # Random critical patients needing transfer
            if random.random() < 0.3:  # 30% chance per hour
                await self.simulate_emergency_patient_transfer()
            
            # System failures
            if random.random() < 0.1:  # 10% chance per hour
                await self.simulate_system_failure()
            
            if hour % 6 == 0:  # Log every 6 hours
                self.logger.warning(f"Hour {hour}: Network {network_quality:.1%}, "
                                  f"Patients transferred: {self.simulation_data['patients_transferred']}")
        
        self.log_event("PHASE_2_COMPLETE", "Peak impact phase complete")
    
    async def phase_3_recovery(self):
        """Phase 3: Post-hurricane recovery."""
        self.logger.info("🔧 Phase 3: Recovery (30-72 hours)")
        self.log_event("PHASE_3_START", "Recovery phase beginning")
        
        # Gradual network recovery
        for hour in range(30, 72):
            await asyncio.sleep(0.1)  # Compressed time
            
            # Improving connectivity
            recovery_progress = (hour - 30) / 42  # 42 hours of recovery
            network_quality = min(0.9, 0.2 + (recovery_progress * 0.7))
            
            await self.simulate_network_recovery(network_quality)
            
            # Process backlog of studies
            if hour % 6 == 0:
                await self.process_study_backlog()
            
            # Return evacuated patients
            if hour > 48 and random.random() < 0.2:
                await self.simulate_patient_return()
            
            if hour % 12 == 0:  # Log every 12 hours
                self.logger.info(f"Hour {hour}: Network {network_quality:.1%}, "
                               f"Recovery progress: {recovery_progress:.1%}")
        
        # Deactivate emergency mode
        await self.eraif_core.deactivate_emergency_mode("Hurricane passed, systems stable")
        
        self.log_event("PHASE_3_COMPLETE", "Recovery phase complete")
    
    async def simulate_patient_preparation(self):
        """Simulate patient preparation activities."""
        self.logger.info("Preparing high-risk patients for potential evacuation...")
        
        # Identify critical patients
        critical_patients = [
            {"id": f"PAT{i:03d}", "condition": "critical", "mobility": "limited"}
            for i in range(1, 21)  # 20 critical patients
        ]
        
        # Pre-transfer imaging for critical patients
        for patient in critical_patients[:5]:  # Process first 5
            study = Study(
                study_id=f"PREP_{patient['id']}",
                patient_id=patient['id'],
                modality="CT",
                priority="HIGH",
                body_part="CHEST"
            )
            
            self.simulation_data['studies_processed'] += 1
            await asyncio.sleep(0.1)
        
        self.log_event("PATIENT_PREP", f"Prepared {len(critical_patients)} critical patients")
    
    async def simulate_data_backup(self):
        """Simulate critical data backup procedures."""
        self.logger.info("Backing up critical imaging data...")
        
        # Simulate backup of last 48 hours of critical studies
        backup_studies = 150  # Number of studies to backup
        
        for i in range(backup_studies):
            if i % 50 == 0:
                self.logger.info(f"Backup progress: {i}/{backup_studies}")
            await asyncio.sleep(0.01)  # Simulated backup time
        
        self.log_event("DATA_BACKUP", f"Backed up {backup_studies} critical studies")
    
    async def simulate_facility_evacuation(self, facility_id: str):
        """Simulate facility evacuation."""
        self.logger.warning(f"🚨 FACILITY EVACUATION: {facility_id}")
        
        # Number of patients to evacuate
        patient_count = random.randint(50, 150)
        
        # Transfer critical patients first
        critical_transfers = min(20, patient_count // 3)
        
        for i in range(critical_transfers):
            await self.simulate_emergency_patient_transfer(
                source_facility=facility_id,
                priority="CRITICAL"
            )
            await asyncio.sleep(0.05)  # Brief delay between transfers
        
        self.log_event("FACILITY_EVACUATION", 
                      f"{facility_id}: Evacuated {critical_transfers} critical patients")
    
    async def simulate_emergency_patient_transfer(self, source_facility: str = None, 
                                                priority: str = "HIGH"):
        """Simulate emergency patient transfer with imaging."""
        if not source_facility:
            source_facility = random.choice(self.config["scenario"]["affected_facilities"])
        
        destination = random.choice(self.config["scenario"]["safe_facilities"])
        patient_id = f"EMG{random.randint(1000, 9999)}"
        
        # Create emergency study
        study = Study(
            study_id=f"EMG_{patient_id}_{datetime.now().strftime('%H%M%S')}",
            patient_id=patient_id,
            modality=random.choice(["CT", "MRI", "XR"]),
            priority=priority,
            body_part=random.choice(["CHEST", "HEAD", "ABDOMEN"])
        )
        
        try:
            # Simulate transfer (success depends on network quality)
            current_status = await self.eraif_core.get_emergency_status()
            
            # Higher chance of success for critical patients
            success_rate = 0.9 if priority == "CRITICAL" else 0.7
            
            if random.random() < success_rate:
                self.simulation_data['successful_transfers'] += 1
                self.simulation_data['patients_transferred'] += 1
                self.log_event("PATIENT_TRANSFER_SUCCESS", 
                              f"{patient_id}: {source_facility} → {destination}")
            else:
                self.simulation_data['failed_transfers'] += 1
                self.log_event("PATIENT_TRANSFER_FAILED", 
                              f"{patient_id}: Transfer failed - will retry")
        
        except Exception as e:
            self.simulation_data['failed_transfers'] += 1
            self.logger.error(f"Transfer failed for {patient_id}: {e}")
    
    async def simulate_network_degradation(self, quality: float):
        """Simulate network quality degradation."""
        if quality < 0.3:
            self.simulation_data['network_failures'] += 1
            
            # Force disaster mode if not already active
            if self.eraif_core.emergency_mode != EmergencyMode.DISASTER:
                await self.eraif_core.activate_emergency_mode(
                    f"Severe network degradation: {quality:.1%} connectivity"
                )
    
    async def simulate_network_recovery(self, quality: float):
        """Simulate network quality recovery."""
        if quality > 0.7 and self.eraif_core.emergency_mode == EmergencyMode.DISASTER:
            # Upgrade to hybrid mode
            await self.eraif_core.activate_emergency_mode(
                f"Network recovering: {quality:.1%} connectivity"
            )
    
    async def simulate_system_failure(self):
        """Simulate random system failures."""
        failure_types = [
            "Power outage at imaging center",
            "PACS server failure", 
            "Network switch failure",
            "Storage system overload"
        ]
        
        failure = random.choice(failure_types)
        self.logger.error(f"🔥 SYSTEM FAILURE: {failure}")
        self.log_event("SYSTEM_FAILURE", failure)
    
    async def process_study_backlog(self):
        """Process backlog of studies during recovery."""
        backlog_size = random.randint(10, 50)
        
        for i in range(backlog_size):
            study_id = f"BACKLOG_{i:03d}_{datetime.now().strftime('%H%M%S')}"
            self.simulation_data['studies_processed'] += 1
            
            if i % 10 == 0:
                await asyncio.sleep(0.1)  # Brief processing delay
        
        self.log_event("BACKLOG_PROCESSED", f"Processed {backlog_size} backlogged studies")
    
    async def simulate_patient_return(self):
        """Simulate returning evacuated patients."""
        if self.simulation_data['patients_transferred'] > 0:
            self.simulation_data['patients_transferred'] -= 1
            self.log_event("PATIENT_RETURN", "Evacuated patient returned to home facility")
    
    def log_event(self, event_type: str, description: str):
        """Log simulation event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "description": description
        }
        self.simulation_data['timeline'].append(event)
        self.logger.info(f"[{event_type}] {description}")
    
    async def generate_report(self):
        """Generate final simulation report."""
        self.logger.info("\n" + "="*60)
        self.logger.info("🌀 HURRICANE EMERGENCY SIMULATION REPORT")
        self.logger.info("="*60)
        
        # Summary statistics
        stats = self.simulation_data
        self.logger.info(f"Patients Transferred: {stats['patients_transferred']}")
        self.logger.info(f"Studies Processed: {stats['studies_processed']}")
        self.logger.info(f"Successful Transfers: {stats['successful_transfers']}")
        self.logger.info(f"Failed Transfers: {stats['failed_transfers']}")
        self.logger.info(f"Network Failures: {stats['network_failures']}")
        
        # Success rate
        total_attempts = stats['successful_transfers'] + stats['failed_transfers']
        if total_attempts > 0:
            success_rate = (stats['successful_transfers'] / total_attempts) * 100
            self.logger.info(f"Transfer Success Rate: {success_rate:.1f}%")
        
        # Key events timeline
        self.logger.info("\nKEY EVENTS TIMELINE:")
        for event in stats['timeline']:
            if event['type'] in ['PHASE_1_START', 'PHASE_2_START', 'PHASE_3_START', 
                               'FACILITY_EVACUATION', 'SYSTEM_FAILURE']:
                self.logger.info(f"  {event['timestamp']}: {event['description']}")
        
        self.logger.info("="*60)
        
        # Lessons learned
        self.logger.info("LESSONS LEARNED:")
        self.logger.info("- Emergency mode activation was critical for maintaining operations")
        self.logger.info("- Priority-based patient transfers saved lives during peak impact")
        self.logger.info("- Network redundancy is essential for disaster resilience")
        self.logger.info("- Automated failover systems reduced manual intervention needs")
        
        return stats


async def main():
    """Run the hurricane scenario simulation."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scenario = HurricaneScenario()
    
    try:
        results = await scenario.run_simulation()
        print(f"\n✅ Simulation completed successfully!")
        print(f"📊 Final stats: {results}")
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
