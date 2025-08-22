# ERAIF Implementation Guide

## Getting Started

### Prerequisites

- Python 3.8+
- Docker (recommended)
- SSL certificates for production
- Network access to medical imaging systems

### Installation Options

#### Option 1: Docker (Recommended)
```bash
docker pull eraif/emergency-connector:latest
docker run -d -p 8080:8080 -p 8443:8443 eraif/emergency-connector
```

#### Option 2: Python Package
```bash
pip install eraif
eraif-server --config /path/to/config.yml
```

#### Option 3: Source Installation
```bash
git clone https://github.com/[username]/ERAIF.git
cd ERAIF
pip install -r requirements.txt
python src/main.py
```

## Configuration

### Basic Configuration (`config.yml`)
```yaml
server:
  host: "0.0.0.0"
  port: 8080
  ssl_port: 8443
  
emergency:
  mode: "normal"  # normal, disaster, hybrid
  fallback_timeout: 30
  
security:
  ssl_cert: "/path/to/cert.pem"
  ssl_key: "/path/to/key.pem"
  
integrations:
  pacs:
    - name: "MainPACS"
      url: "https://pacs.hospital.com"
      auth_type: "certificate"
  
  ris:
    - name: "MainRIS"
      url: "https://ris.hospital.com"
      auth_type: "oauth2"
```

### Emergency Mode Configuration
```yaml
emergency:
  triggers:
    - type: "network_failure"
      threshold: 5  # seconds
    - type: "system_overload"
      threshold: 90  # percent CPU
    - type: "manual"
      
  disaster_mode:
    compression: true
    priority_filter: ["CRITICAL", "HIGH"]
    batch_size: 10
```

## Integration Patterns

### PACS Integration
```python
from eraif import PACSConnector

# Initialize connector
pacs = PACSConnector(
    host="pacs.hospital.com",
    port=11112,
    ae_title="ERAIF_EMERGENCY"
)

# Query for studies
studies = pacs.find_studies(
    patient_id="12345",
    modality="CT",
    date_range=("2024-01-01", "2024-12-31")
)

# Transfer study
pacs.transfer_study(study_id="1.2.3.4.5", destination="REMOTE_PACS")
```

### HL7/FHIR Integration
```python
from eraif import FHIRConnector

# Initialize FHIR client
fhir = FHIRConnector(base_url="https://fhir.hospital.com")

# Create emergency patient record
patient = fhir.create_patient({
    "identifier": [{"value": "EMR123"}],
    "name": [{"family": "Doe", "given": ["John"]}],
    "emergencyContact": [{"name": "Jane Doe", "phone": "555-1234"}]
})
```

### AI Integration
```python
from eraif import AIConnector

# Initialize AI service
ai = AIConnector(service_url="https://ai.radiology.com")

# Analyze CT scan for trauma
result = ai.analyze_study(
    study_id="1.2.3.4.5",
    analysis_type="trauma_detection",
    priority="CRITICAL"
)

print(f"Findings: {result.findings}")
print(f"Confidence: {result.confidence}")
```

## Emergency Procedures

### Activating Emergency Mode
```bash
# Manual activation
curl -X POST http://localhost:8080/emergency/activate \
  -H "Authorization: Bearer <token>" \
  -d '{"reason": "Hurricane", "duration": "72h"}'

# Automatic activation (configured in config.yml)
# Triggers on network failure, system overload, etc.
```

### Priority Handling
```python
# Set study priority
study.set_priority("CRITICAL")  # CRITICAL, HIGH, NORMAL, LOW

# Emergency routing
eraif.route_study(study, mode="emergency", destination="trauma_center")
```

### Offline Capabilities
```python
# Enable offline mode
eraif.enable_offline_mode()

# Queue studies for later transmission
eraif.queue_study(study, destination="remote_hospital")

# Sync when connection restored
eraif.sync_queued_studies()
```

## Monitoring and Logging

### Health Checks
```bash
# System health
curl http://localhost:8080/health

# Emergency readiness
curl http://localhost:8080/emergency/readiness

# Connection status
curl http://localhost:8080/connections/status
```

### Logging Configuration
```yaml
logging:
  level: INFO
  format: json
  destinations:
    - type: file
      path: "/var/log/eraif/emergency.log"
    - type: syslog
      facility: local0
    - type: elasticsearch
      url: "https://logs.hospital.com"
```

## Testing

### Unit Tests
```bash
pytest tests/test_core.py -v
```

### Integration Tests
```bash
pytest tests/test_emergency.py -v
```

### Disaster Simulation
```bash
python tests/simulations/hurricane_scenario.py
python tests/simulations/mass_casualty.py
```

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Check SSL certificates
   - Verify network connectivity
   - Review firewall rules

2. **Performance Issues**
   - Monitor system resources
   - Check database connections
   - Review log files

3. **Emergency Mode Not Activating**
   - Verify trigger thresholds
   - Check permissions
   - Review configuration

### Support Resources

- Documentation: https://docs.eraif.org
- Community Forum: https://forum.eraif.org
- Emergency Hotline: +1-800-ERAIF-911
