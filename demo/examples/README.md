# ERAIF Working Examples

This directory contains real-world examples demonstrating ERAIF's capabilities in various healthcare interoperability scenarios.

## 📚 Available Examples

### 1. Hospital to Clinic Transfer (`hospital_to_clinic_transfer.py`)

**Scenario**: Secure transfer of patient imaging data from a hospital PACS system to an outpatient clinic's RIS system.

**What it demonstrates**:
- ✅ Secure handshake protocol between facilities
- ✅ HIPAA-compliant patient demographics transfer
- ✅ DICOM imaging study transfer with metadata
- ✅ AI analysis results sharing
- ✅ Data integrity verification
- ✅ Comprehensive audit logging
- ✅ Transfer reporting and compliance documentation

**Run the example**:
```bash
cd demo/examples
python hospital_to_clinic_transfer.py
```

**Expected output**:
- Detailed transfer workflow logs
- Security and compliance verification
- Transfer report JSON file

**Use cases**:
- Patient referred from ER to specialist clinic
- Follow-up imaging review at outpatient facility
- Telehealth consultation with remote specialist
- Second opinion requests

---

### 2. FHIR R4 Emergency Transfer (`fhir_emergency_transfer.py`)

**Scenario**: Emergency radiology data exchange using HL7 FHIR R4 standard for interoperability with existing healthcare systems.

**What it demonstrates**:
- ✅ ERAIF to FHIR R4 resource conversion
- ✅ FHIR Patient, ImagingStudy, and DiagnosticReport resources
- ✅ AI analysis integration with FHIR extensions
- ✅ Emergency transfer workflow with priority handling
- ✅ FHIR server communication (REST API)
- ✅ FHIR Bundle transactions for atomic operations
- ✅ FHIR search capabilities for resource retrieval

**Run the example**:
```bash
cd demo/examples
python fhir_emergency_transfer.py
```

**Expected output**:
- FHIR resource conversion demonstrations
- Emergency transfer workflow simulation
- FHIR search examples
- Integration guidelines

**Use cases**:
- Rural hospital transferring to trauma center
- Integration with existing EHR systems
- Multi-facility emergency response coordination
- Standardized data exchange with PACS/RIS systems
- Compliance with national healthcare data standards

**Prerequisites** (for live FHIR server connection):
```bash
# Optional: Run HAPI FHIR server for testing
docker run -p 8080:8080 hapiproject/hapi:latest
```

---

## 🏗️ Example Structure

Each example follows a consistent pattern:

1. **Protocol Initialization**: Setup secure communication channels
2. **Data Generation**: Create realistic sample data
3. **Transfer Workflow**: Execute step-by-step transfer process
4. **Verification**: Validate data integrity and compliance
5. **Reporting**: Generate comprehensive audit reports

## 🔐 Security Features

All examples demonstrate:

- **Encryption**: AES-256-GCM for data in transit
- **Authentication**: OAuth2 with mutual TLS (mTLS)
- **Authorization**: Role-based access control
- **Integrity**: SHA-256 hash verification
- **Compliance**: HIPAA, DICOM, HL7 FHIR standards

## 📊 Sample Data

Examples use the `ERAIFDataGenerator` utility to create:
- Realistic patient demographics
- Imaging studies with multiple series
- AI analysis results
- Emergency scenarios
- Clinical metadata

## 🚀 Creating Your Own Examples

To create a new example:

1. **Copy the template**:
   ```python
   from models.patient import Patient
   from models.study import Study
   from models.protocol import ECPMessage
   from utils.data_generator import ERAIFDataGenerator
   ```

2. **Define your protocol**:
   ```python
   class YourProtocol:
       def __init__(self):
           self.protocol_version = "1.0.0"

       def execute_workflow(self):
           # Your implementation here
           pass
   ```

3. **Add demonstration logic**:
   ```python
   def main():
       protocol = YourProtocol()
       protocol.execute_workflow()
   ```

4. **Document your example**: Add a section to this README

## 📝 Example Output Files

Examples may generate the following files:

- `*_transfer_report.json`: Comprehensive transfer audit log
- `*_export.json`: Sample data export
- `*_log.txt`: Detailed execution logs

## 🤝 Contributing Examples

We welcome new examples! Please ensure:

- ✅ Code is well-documented
- ✅ Follows ERAIF coding standards
- ✅ Includes realistic scenarios
- ✅ Demonstrates security best practices
- ✅ Provides clear output and logging
- ✅ Updates this README with documentation

## 📚 Additional Resources

- [ERAIF Documentation](../../docs/)
- [API Reference](../../docs/API.md)
- [Implementation Guide](../../docs/IMPLEMENTATION-GUIDE.md)
- [Security Model](../../docs/SECURITY.md)

## 🆘 Getting Help

If you have questions or issues:

1. Check the [main README](../../README.md)
2. Review the [demo documentation](../README_DEMO.md)
3. Open an issue on GitHub
4. Contact: info@eraif.org

---

**Remember**: These are demonstration examples. Always follow your organization's security policies and regulatory requirements when implementing in production environments.
