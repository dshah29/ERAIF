#!/usr/bin/env python3
"""
Cyber Attack Scenario Simulation

This simulation tests ERAIF's response to a cyber security incident
affecting medical imaging systems, including ransomware attacks,
system isolation, and secure failover procedures.
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


class AttackType(Enum):
    """Types of cyber attacks."""
    RANSOMWARE = "ransomware"
    DDOS = "distributed_denial_of_service"
    DATA_BREACH = "data_breach"
    MALWARE = "malware_infection"
    INSIDER_THREAT = "insider_threat"


class SystemStatus(Enum):
    """System security status."""
    SECURE = "secure"
    COMPROMISED = "compromised"
    ISOLATED = "isolated"
    RECOVERING = "recovering"
    OFFLINE = "offline"


class CyberAttackScenario:
    """Simulate a cyber security incident affecting medical systems."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {
            "emergency": {
                "triggers": [
                    {"type": "security_breach", "threshold": 1},
                    {"type": "system_compromise", "threshold": 1}
                ],
                "disaster_mode": {
                    "compression": True,
                    "priority_filter": ["CRITICAL", "HIGH"],
                    "batch_size": 5,  # Smaller batches for security
                    "encryption_required": True,
                    "air_gap_mode": True
                }
            },
            "scenario": {
                "name": "Healthcare Ransomware Attack",
                "attack_vector": "Phishing email with malicious attachment",
                "target_systems": [
                    {"id": "PACS_PRIMARY", "type": "imaging", "criticality": "high"},
                    {"id": "RIS_MAIN", "type": "radiology_info", "criticality": "high"},
                    {"id": "EMR_SYSTEM", "type": "medical_records", "criticality": "critical"},
                    {"id": "BACKUP_STORAGE", "type": "backup", "criticality": "medium"},
                    {"id": "WORKSTATIONS", "type": "endpoints", "criticality": "medium"}
                ],
                "backup_systems": [
                    {"id": "OFFLINE_PACS", "type": "air_gapped_backup"},
                    {"id": "MOBILE_UNITS", "type": "portable_imaging"},
                    {"id": "SATELLITE_LINK", "type": "emergency_communication"},
                    {"id": "PAPER_BACKUP", "type": "manual_processes"}
                ]
            }
        }
        
        self.eraif_core = None
        self.system_status = {}
        self.attack_timeline = []
        self.simulation_data = {
            "attack_start_time": None,
            "systems_compromised": 0,
            "systems_isolated": 0,
            "data_encrypted": 0,  # GB
            "studies_affected": 0,
            "studies_recovered": 0,
            "downtime_minutes": 0,
            "backup_systems_activated": 0,
            "security_events": [],
            "recovery_actions": []
        }
    
    async def initialize(self):
        """Initialize the cyber attack scenario."""
        self.logger.info("Initializing Cyber Attack Scenario...")
        
        self.eraif_core = ERAIFCore(self.config)
        await self.eraif_core.initialize()
        
        # Initialize system status
        for system in self.config["scenario"]["target_systems"]:
            self.system_status[system["id"]] = {
                "status": SystemStatus.SECURE,
                "last_backup": datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
                "data_size_gb": random.randint(100, 5000),
                "studies_count": random.randint(1000, 50000),
                "compromise_time": None,
                "recovery_time": None
            }
        
        self.logger.info("Cyber attack scenario initialized")
    
    async def run_simulation(self):
        """Run the complete cyber attack simulation."""
        try:
            await self.initialize()
            
            self.logger.error("🔴 CYBER SECURITY INCIDENT SIMULATION STARTING")
            self.log_security_event("INCIDENT_START", 
                                   "Suspected ransomware attack detected", "HIGH")
            
            # Phase 1: Attack initiation and detection (0-30 minutes)
            await self.phase_1_attack_detection()
            
            # Phase 2: Containment and isolation (30-60 minutes)
            await self.phase_2_containment()
            
            # Phase 3: Emergency operations (1-8 hours)
            await self.phase_3_emergency_ops()
            
            # Phase 4: Recovery and restoration (8-24 hours)
            await self.phase_4_recovery()
            
            # Generate final report
            await self.generate_report()
            
        except Exception as e:
            self.logger.error(f"Simulation failed: {e}")
            raise
        finally:
            if self.eraif_core:
                await self.eraif_core.shutdown()
    
    async def phase_1_attack_detection(self):
        """Phase 1: Attack initiation and detection."""
        self.logger.error("🚨 Phase 1: Attack detection (0-30 minutes)")
        self.simulation_data["attack_start_time"] = datetime.utcnow()
        
        # Simulate initial compromise
        await self.simulate_initial_compromise()
        
        # Detection delay (realistic for advanced persistent threats)
        await asyncio.sleep(1.5)  # Compressed time - represents 15 minutes
        
        # Security team detects anomalous activity
        await self.detect_security_breach()
        
        # Activate emergency protocols immediately
        await self.eraif_core.activate_emergency_mode(
            "SECURITY INCIDENT: Suspected ransomware attack on medical systems",
            "24h"
        )
        
        # Begin initial assessment
        await self.assess_initial_damage()
        
        self.log_security_event("PHASE_1_COMPLETE", 
                               "Initial detection and emergency activation complete", "HIGH")
    
    async def phase_2_containment(self):
        """Phase 2: Containment and isolation."""
        self.logger.error("🔒 Phase 2: Containment (30-60 minutes)")
        
        # Immediate network isolation
        await self.isolate_compromised_systems()
        
        # Activate backup systems
        await self.activate_backup_systems()
        
        # Secure unaffected systems
        await self.secure_clean_systems()
        
        # Assess full scope of compromise
        await self.assess_full_compromise()
        
        # Begin forensic preservation
        await self.preserve_forensic_evidence()
        
        self.log_security_event("PHASE_2_COMPLETE", 
                               "Containment measures implemented", "HIGH")
    
    async def phase_3_emergency_ops(self):
        """Phase 3: Emergency operations with limited systems."""
        self.logger.warning("⚡ Phase 3: Emergency operations (1-8 hours)")
        
        # Operate on backup/air-gapped systems only
        await self.switch_to_emergency_systems()
        
        # Process critical patients only
        for hour in range(7):  # 7 hours of emergency operations
            await asyncio.sleep(0.5)  # Compressed time
            
            # Handle critical imaging requests
            await self.process_critical_imaging()
            
            # Monitor for attack progression
            await self.monitor_attack_progression()
            
            # Communicate with authorities
            if hour == 2:
                await self.notify_authorities()
            
            # Attempt partial recovery
            if hour >= 4:
                await self.attempt_partial_recovery()
            
            self.logger.warning(f"Emergency ops hour {hour + 1}: "
                              f"{self.count_operational_systems()} systems operational")
        
        self.log_security_event("PHASE_3_COMPLETE", 
                               "Emergency operations phase complete", "MEDIUM")
    
    async def phase_4_recovery(self):
        """Phase 4: Recovery and restoration."""
        self.logger.info("🔧 Phase 4: Recovery (8-24 hours)")
        
        # Begin systematic recovery
        await self.begin_systematic_recovery()
        
        # Restore from clean backups
        await self.restore_from_backups()
        
        # Validate system integrity
        await self.validate_system_integrity()
        
        # Gradually restore services
        await self.gradual_service_restoration()
        
        # Conduct post-incident analysis
        await self.post_incident_analysis()
        
        # Deactivate emergency mode
        await self.eraif_core.deactivate_emergency_mode(
            "Cyber security incident contained, systems restored"
        )
        
        self.log_security_event("PHASE_4_COMPLETE", 
                               "Recovery and restoration complete", "LOW")
    
    async def simulate_initial_compromise(self):
        """Simulate the initial system compromise."""
        # Ransomware typically starts with endpoint compromise
        initial_target = "WORKSTATIONS"
        
        self.system_status[initial_target]["status"] = SystemStatus.COMPROMISED
        self.system_status[initial_target]["compromise_time"] = datetime.utcnow()
        self.simulation_data["systems_compromised"] += 1
        
        # Lateral movement to high-value targets
        await asyncio.sleep(0.5)  # Time for lateral movement
        
        high_value_targets = ["PACS_PRIMARY", "EMR_SYSTEM"]
        for target in high_value_targets:
            if random.random() < 0.8:  # 80% chance of successful lateral movement
                self.system_status[target]["status"] = SystemStatus.COMPROMISED
                self.system_status[target]["compromise_time"] = datetime.utcnow()
                self.simulation_data["systems_compromised"] += 1
                
                # Calculate encrypted data
                data_size = self.system_status[target]["data_size_gb"]
                self.simulation_data["data_encrypted"] += data_size
                
                self.log_security_event("SYSTEM_COMPROMISED", 
                                       f"{target} compromised - {data_size}GB encrypted", 
                                       "CRITICAL")
    
    async def detect_security_breach(self):
        """Simulate security breach detection."""
        detection_indicators = [
            "Unusual file system activity detected",
            "Suspicious network traffic to unknown domains", 
            "Multiple failed authentication attempts",
            "Unauthorized encryption processes running",
            "Ransom note files discovered"
        ]
        
        for indicator in random.sample(detection_indicators, 3):
            self.log_security_event("DETECTION", indicator, "HIGH")
            await asyncio.sleep(0.1)
        
        # Automated security tools trigger alerts
        self.log_security_event("AUTOMATED_ALERT", 
                               "Security monitoring systems triggered multiple alerts", 
                               "CRITICAL")
    
    async def assess_initial_damage(self):
        """Assess initial damage from the attack."""
        compromised_systems = [
            sys_id for sys_id, status in self.system_status.items()
            if status["status"] == SystemStatus.COMPROMISED
        ]
        
        total_studies_affected = sum(
            self.system_status[sys_id]["studies_count"] 
            for sys_id in compromised_systems
        )
        
        self.simulation_data["studies_affected"] = total_studies_affected
        
        self.log_security_event("DAMAGE_ASSESSMENT", 
                               f"Initial assessment: {len(compromised_systems)} systems, "
                               f"{total_studies_affected} studies affected", 
                               "HIGH")
    
    async def isolate_compromised_systems(self):
        """Isolate compromised systems from the network."""
        compromised_systems = [
            sys_id for sys_id, status in self.system_status.items()
            if status["status"] == SystemStatus.COMPROMISED
        ]
        
        for sys_id in compromised_systems:
            self.system_status[sys_id]["status"] = SystemStatus.ISOLATED
            self.simulation_data["systems_isolated"] += 1
            
            self.log_security_event("SYSTEM_ISOLATED", 
                                   f"{sys_id} isolated from network", "MEDIUM")
            await asyncio.sleep(0.1)
    
    async def activate_backup_systems(self):
        """Activate backup and air-gapped systems."""
        backup_systems = self.config["scenario"]["backup_systems"]
        
        for backup in backup_systems:
            if backup["type"] in ["air_gapped_backup", "emergency_communication"]:
                self.simulation_data["backup_systems_activated"] += 1
                
                self.log_security_event("BACKUP_ACTIVATED", 
                                       f"{backup['id']} backup system activated", 
                                       "MEDIUM")
                await asyncio.sleep(0.2)
    
    async def secure_clean_systems(self):
        """Secure systems that haven't been compromised."""
        clean_systems = [
            sys_id for sys_id, status in self.system_status.items()
            if status["status"] == SystemStatus.SECURE
        ]
        
        security_measures = [
            "Enhanced monitoring enabled",
            "Additional access controls applied",
            "Network segmentation enforced",
            "Endpoint protection updated"
        ]
        
        for sys_id in clean_systems:
            measure = random.choice(security_measures)
            self.log_security_event("SECURITY_HARDENING", 
                                   f"{sys_id}: {measure}", "LOW")
    
    async def assess_full_compromise(self):
        """Assess the full scope of the compromise."""
        # Discover additional compromised systems
        remaining_systems = [
            sys_id for sys_id, status in self.system_status.items()
            if status["status"] == SystemStatus.SECURE
        ]
        
        for sys_id in remaining_systems:
            if random.random() < 0.3:  # 30% chance of discovering additional compromise
                self.system_status[sys_id]["status"] = SystemStatus.COMPROMISED
                self.simulation_data["systems_compromised"] += 1
                
                self.log_security_event("ADDITIONAL_COMPROMISE", 
                                       f"{sys_id} found to be compromised", "HIGH")
    
    async def preserve_forensic_evidence(self):
        """Preserve forensic evidence for investigation."""
        forensic_actions = [
            "Memory dumps captured from compromised systems",
            "Network traffic logs preserved",
            "System artifacts collected",
            "Malware samples isolated for analysis"
        ]
        
        for action in forensic_actions:
            self.simulation_data["recovery_actions"].append(action)
            self.log_security_event("FORENSICS", action, "LOW")
            await asyncio.sleep(0.1)
    
    async def switch_to_emergency_systems(self):
        """Switch operations to emergency backup systems."""
        # Activate air-gapped PACS
        # Enable manual workflows
        # Use portable imaging units
        
        self.log_security_event("EMERGENCY_MODE", 
                               "Switched to air-gapped emergency systems", "HIGH")
        
        # Simulate reduced capacity
        self.simulation_data["downtime_minutes"] = 120  # 2 hours of reduced service
    
    async def process_critical_imaging(self):
        """Process only critical imaging requests during emergency operations."""
        # Only process STAT and emergency cases
        critical_studies = random.randint(5, 15)  # Reduced volume
        
        for _ in range(critical_studies):
            study = Study(
                study_id=f"EMRG_{datetime.now().strftime('%H%M%S')}_{random.randint(100, 999)}",
                patient_id=f"CRIT{random.randint(1000, 9999)}",
                modality=random.choice(["CT", "XR", "US"]),  # Limited modalities
                priority="CRITICAL",
                body_part=random.choice(["HEAD", "CHEST", "ABDOMEN"])
            )
            
            # Process on backup systems with delays
            await asyncio.sleep(0.05)  # Slower processing
        
        self.log_security_event("CRITICAL_PROCESSING", 
                               f"Processed {critical_studies} critical studies on backup systems", 
                               "MEDIUM")
    
    async def monitor_attack_progression(self):
        """Monitor for continued attack activity."""
        # Check for signs of continued compromise
        if random.random() < 0.2:  # 20% chance of detecting continued activity
            activities = [
                "Attempted lateral movement blocked",
                "Additional encryption attempts detected",
                "Command and control communication intercepted"
            ]
            
            activity = random.choice(activities)
            self.log_security_event("CONTINUED_ACTIVITY", activity, "HIGH")
    
    async def notify_authorities(self):
        """Notify relevant authorities about the incident."""
        notifications = [
            "FBI Cyber Division notified",
            "HHS Office for Civil Rights contacted",
            "State health department informed",
            "Cyber threat intelligence shared with CISA"
        ]
        
        for notification in notifications:
            self.simulation_data["recovery_actions"].append(notification)
            self.log_security_event("AUTHORITY_NOTIFICATION", notification, "MEDIUM")
            await asyncio.sleep(0.1)
    
    async def attempt_partial_recovery(self):
        """Attempt partial recovery of less critical systems."""
        isolated_systems = [
            sys_id for sys_id, status in self.system_status.items()
            if status["status"] == SystemStatus.ISOLATED
        ]
        
        for sys_id in isolated_systems:
            if self.system_status[sys_id].get("criticality") != "critical":
                if random.random() < 0.4:  # 40% chance of successful partial recovery
                    self.system_status[sys_id]["status"] = SystemStatus.RECOVERING
                    
                    self.log_security_event("PARTIAL_RECOVERY", 
                                           f"{sys_id} beginning recovery process", "MEDIUM")
    
    async def begin_systematic_recovery(self):
        """Begin systematic recovery of all systems."""
        recovery_steps = [
            "Malware removal from isolated systems",
            "System integrity verification",
            "Security patch deployment",
            "Configuration hardening",
            "Clean backup preparation"
        ]
        
        for step in recovery_steps:
            self.simulation_data["recovery_actions"].append(step)
            self.log_security_event("RECOVERY_STEP", step, "LOW")
            await asyncio.sleep(0.2)
    
    async def restore_from_backups(self):
        """Restore systems from clean backups."""
        compromised_systems = [
            sys_id for sys_id, status in self.system_status.items()
            if status["status"] in [SystemStatus.COMPROMISED, SystemStatus.ISOLATED]
        ]
        
        for sys_id in compromised_systems:
            # Check backup availability
            backup_age = datetime.utcnow() - self.system_status[sys_id]["last_backup"]
            
            if backup_age.total_seconds() < 86400:  # Less than 24 hours old
                # Successful restore
                self.system_status[sys_id]["status"] = SystemStatus.RECOVERING
                self.system_status[sys_id]["recovery_time"] = datetime.utcnow()
                
                studies_recovered = self.system_status[sys_id]["studies_count"]
                self.simulation_data["studies_recovered"] += studies_recovered
                
                self.log_security_event("BACKUP_RESTORE", 
                                       f"{sys_id} restored from backup - "
                                       f"{studies_recovered} studies recovered", 
                                       "MEDIUM")
            else:
                self.log_security_event("BACKUP_ISSUE", 
                                       f"{sys_id} backup too old - manual recovery required", 
                                       "HIGH")
            
            await asyncio.sleep(0.3)  # Time for restore process
    
    async def validate_system_integrity(self):
        """Validate the integrity of restored systems."""
        recovering_systems = [
            sys_id for sys_id, status in self.system_status.items()
            if status["status"] == SystemStatus.RECOVERING
        ]
        
        validation_checks = [
            "Antivirus scan completed",
            "System file integrity verified",
            "Network connectivity tested",
            "Application functionality confirmed"
        ]
        
        for sys_id in recovering_systems:
            for check in validation_checks:
                self.log_security_event("VALIDATION", f"{sys_id}: {check}", "LOW")
                await asyncio.sleep(0.05)
            
            # Mark as secure if validation passes
            if random.random() < 0.9:  # 90% success rate
                self.system_status[sys_id]["status"] = SystemStatus.SECURE
                self.log_security_event("SYSTEM_RESTORED", 
                                       f"{sys_id} fully restored and validated", "MEDIUM")
    
    async def gradual_service_restoration(self):
        """Gradually restore services to normal operations."""
        restoration_phases = [
            "Critical imaging services restored",
            "Emergency department systems online", 
            "Routine imaging capabilities restored",
            "Full system integration completed"
        ]
        
        for phase in restoration_phases:
            self.simulation_data["recovery_actions"].append(phase)
            self.log_security_event("SERVICE_RESTORATION", phase, "LOW")
            await asyncio.sleep(0.5)
    
    async def post_incident_analysis(self):
        """Conduct post-incident analysis and lessons learned."""
        analysis_items = [
            "Attack vector analysis completed",
            "Timeline reconstruction finished",
            "Security gaps identified",
            "Improvement recommendations drafted"
        ]
        
        for item in analysis_items:
            self.simulation_data["recovery_actions"].append(item)
            self.log_security_event("POST_INCIDENT", item, "LOW")
            await asyncio.sleep(0.1)
    
    def count_operational_systems(self) -> int:
        """Count currently operational systems."""
        return sum(
            1 for status in self.system_status.values()
            if status["status"] in [SystemStatus.SECURE, SystemStatus.RECOVERING]
        )
    
    def log_security_event(self, event_type: str, description: str, severity: str):
        """Log security event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "description": description,
            "severity": severity
        }
        self.simulation_data["security_events"].append(event)
        
        # Log with appropriate level based on severity
        if severity == "CRITICAL":
            self.logger.critical(f"[{event_type}] {description}")
        elif severity == "HIGH":
            self.logger.error(f"[{event_type}] {description}")
        elif severity == "MEDIUM":
            self.logger.warning(f"[{event_type}] {description}")
        else:
            self.logger.info(f"[{event_type}] {description}")
    
    async def generate_report(self):
        """Generate final incident report."""
        self.logger.info("\n" + "="*60)
        self.logger.info("🔴 CYBER SECURITY INCIDENT REPORT")
        self.logger.info("="*60)
        
        stats = self.simulation_data
        
        # Incident overview
        duration = datetime.utcnow() - stats["attack_start_time"]
        self.logger.info(f"Incident Duration: {duration}")
        self.logger.info(f"Systems Compromised: {stats['systems_compromised']}")
        self.logger.info(f"Systems Isolated: {stats['systems_isolated']}")
        self.logger.info(f"Data Encrypted: {stats['data_encrypted']} GB")
        
        # Impact assessment
        self.logger.info(f"\nImpact Assessment:")
        self.logger.info(f"  Studies Affected: {stats['studies_affected']}")
        self.logger.info(f"  Studies Recovered: {stats['studies_recovered']}")
        recovery_rate = (stats['studies_recovered'] / max(stats['studies_affected'], 1)) * 100
        self.logger.info(f"  Recovery Rate: {recovery_rate:.1f}%")
        self.logger.info(f"  Service Downtime: {stats['downtime_minutes']} minutes")
        
        # Response effectiveness
        self.logger.info(f"\nResponse Effectiveness:")
        self.logger.info(f"  Backup Systems Activated: {stats['backup_systems_activated']}")
        self.logger.info(f"  Recovery Actions Taken: {len(stats['recovery_actions'])}")
        
        # System status summary
        self.logger.info(f"\nFinal System Status:")
        status_counts = {}
        for status_info in self.system_status.values():
            status = status_info["status"].value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            self.logger.info(f"  {status.upper()}: {count} systems")
        
        # Key events timeline
        self.logger.info(f"\nKey Security Events:")
        critical_events = [
            event for event in stats["security_events"]
            if event["severity"] in ["CRITICAL", "HIGH"]
        ][:10]  # Show first 10 critical events
        
        for event in critical_events:
            self.logger.info(f"  {event['timestamp']}: {event['description']}")
        
        self.logger.info("="*60)
        
        # Lessons learned
        self.logger.info("LESSONS LEARNED:")
        self.logger.info("- Air-gapped backup systems were critical for maintaining operations")
        self.logger.info("- Rapid isolation prevented further lateral movement")
        self.logger.info("- Emergency protocols enabled continued critical care")
        self.logger.info("- Regular backups were essential for rapid recovery")
        self.logger.info("- Staff training on manual processes proved valuable")
        
        return stats


async def main():
    """Run the cyber attack scenario simulation."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scenario = CyberAttackScenario()
    
    try:
        results = await scenario.run_simulation()
        print(f"\n✅ Simulation completed successfully!")
        print(f"📊 Final stats: {results}")
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
