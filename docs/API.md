# ERAIF API Reference

## Base URL
- **Production**: `https://api.eraif.org/v1`
- **Development**: `http://localhost:8080/v1`

## Authentication

All API requests require authentication using JWT tokens or client certificates.

### JWT Authentication
```bash
curl -H "Authorization: Bearer <jwt_token>" \
     https://api.eraif.org/v1/studies
```

### Certificate Authentication
```bash
curl --cert client.pem --key client.key \
     https://api.eraif.org/v1/studies
```

## Core API Endpoints

### System Status

#### GET /health
Check system health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "components": {
    "database": "healthy",
    "storage": "healthy",
    "external_services": "degraded"
  }
}
```

#### GET /emergency/status
Check emergency system readiness.

**Response:**
```json
{
  "emergency_mode": false,
  "readiness": "ready",
  "last_test": "2024-01-15T09:00:00Z",
  "backup_systems": {
    "offline_storage": "ready",
    "satellite_link": "ready",
    "battery_backup": "90%"
  }
}
```

### Emergency Management

#### POST /emergency/activate
Activate emergency mode.

**Request:**
```json
{
  "reason": "Hurricane Category 5",
  "estimated_duration": "72h",
  "priority_level": "CRITICAL",
  "affected_facilities": ["HOSP001", "HOSP002"]
}
```

**Response:**
```json
{
  "emergency_id": "emg_12345",
  "status": "activated",
  "activation_time": "2024-01-15T10:30:00Z",
  "estimated_end": "2024-01-18T10:30:00Z"
}
```

#### POST /emergency/deactivate
Deactivate emergency mode.

**Request:**
```json
{
  "emergency_id": "emg_12345",
  "reason": "Situation resolved"
}
```

### Study Management

#### GET /studies
List imaging studies.

**Query Parameters:**
- `patient_id` (string): Filter by patient ID
- `modality` (string): Filter by modality (CT, MRI, XR, US)
- `priority` (string): Filter by priority (CRITICAL, HIGH, NORMAL, LOW)
- `date_from` (string): Start date (ISO-8601)
- `date_to` (string): End date (ISO-8601)
- `limit` (integer): Maximum results (default: 50)
- `offset` (integer): Pagination offset (default: 0)

**Response:**
```json
{
  "studies": [
    {
      "study_id": "1.2.3.4.5",
      "patient_id": "PAT001",
      "modality": "CT",
      "body_part": "CHEST",
      "priority": "HIGH",
      "study_date": "2024-01-15",
      "status": "AVAILABLE",
      "image_count": 150,
      "file_size": "125MB"
    }
  ],
  "total": 1,
  "offset": 0,
  "limit": 50
}
```

#### GET /studies/{study_id}
Get detailed study information.

**Response:**
```json
{
  "study_id": "1.2.3.4.5",
  "patient": {
    "patient_id": "PAT001",
    "mrn": "MRN123456",
    "name": "John Doe",
    "dob": "1980-01-01",
    "gender": "M"
  },
  "study_info": {
    "modality": "CT",
    "body_part": "CHEST",
    "study_description": "CT Chest with Contrast",
    "study_date": "2024-01-15",
    "referring_physician": "Dr. Smith"
  },
  "images": [
    {
      "image_id": "1.2.3.4.5.1",
      "instance_number": 1,
      "slice_location": -100.0,
      "file_size": "2MB"
    }
  ],
  "ai_analysis": {
    "status": "completed",
    "findings": ["No acute abnormalities"],
    "confidence": 0.95
  }
}
```

#### POST /studies/transfer
Transfer study to another facility.

**Request:**
```json
{
  "study_id": "1.2.3.4.5",
  "destination": {
    "facility_id": "HOSP002",
    "ae_title": "REMOTE_PACS"
  },
  "priority": "HIGH",
  "compress": true,
  "notify_completion": true
}
```

**Response:**
```json
{
  "transfer_id": "xfer_67890",
  "status": "queued",
  "estimated_completion": "2024-01-15T11:00:00Z",
  "progress_url": "/transfers/xfer_67890"
}
```

### AI Analysis

#### POST /ai/analyze
Request AI analysis of a study.

**Request:**
```json
{
  "study_id": "1.2.3.4.5",
  "analysis_type": "trauma_detection",
  "priority": "HIGH",
  "parameters": {
    "sensitivity": "high",
    "include_measurements": true
  }
}
```

**Response:**
```json
{
  "analysis_id": "ai_54321",
  "status": "processing",
  "estimated_completion": "2024-01-15T10:35:00Z",
  "results_url": "/ai/results/ai_54321"
}
```

#### GET /ai/results/{analysis_id}
Get AI analysis results.

**Response:**
```json
{
  "analysis_id": "ai_54321",
  "study_id": "1.2.3.4.5",
  "status": "completed",
  "completion_time": "2024-01-15T10:33:00Z",
  "results": {
    "findings": [
      {
        "type": "fracture",
        "location": "left_rib_7",
        "confidence": 0.92,
        "severity": "moderate"
      }
    ],
    "measurements": [
      {
        "type": "pneumothorax",
        "size": "15%",
        "location": "left_pleural_space"
      }
    ],
    "summary": "Moderate left 7th rib fracture with small pneumothorax"
  }
}
```

### Patient Management

#### POST /patients
Create or update patient record.

**Request:**
```json
{
  "patient_id": "PAT001",
  "mrn": "MRN123456",
  "demographics": {
    "name": "John Doe",
    "dob": "1980-01-01",
    "gender": "M",
    "address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "ST",
      "zip": "12345"
    }
  },
  "emergency_contact": {
    "name": "Jane Doe",
    "relationship": "spouse",
    "phone": "555-1234"
  }
}
```

#### GET /patients/{patient_id}
Get patient information.

**Response:**
```json
{
  "patient_id": "PAT001",
  "mrn": "MRN123456",
  "demographics": {
    "name": "John Doe",
    "dob": "1980-01-01",
    "gender": "M"
  },
  "studies": [
    {
      "study_id": "1.2.3.4.5",
      "study_date": "2024-01-15",
      "modality": "CT",
      "status": "AVAILABLE"
    }
  ]
}
```

## WebSocket API

### Real-time Updates

Connect to WebSocket endpoint for real-time updates:
```javascript
const ws = new WebSocket('wss://api.eraif.org/v1/ws');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

### Event Types
- `study_completed`: New study available
- `transfer_progress`: Study transfer progress
- `ai_analysis_complete`: AI analysis finished
- `emergency_activated`: Emergency mode activated
- `system_alert`: System alerts and warnings

## Error Handling

### HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: System maintenance

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "The study_id parameter is required",
    "details": {
      "parameter": "study_id",
      "expected_type": "string"
    },
    "request_id": "req_12345",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Rate Limiting

- **Standard endpoints**: 1000 requests/hour
- **Emergency endpoints**: 5000 requests/hour
- **AI analysis**: 100 requests/hour
- **File uploads**: 50 requests/hour

Rate limit headers included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248600
```

## SDKs and Libraries

### Python SDK
```bash
pip install eraif-python
```

```python
from eraif import ERAIFClient

client = ERAIFClient(
    base_url="https://api.eraif.org/v1",
    token="your_jwt_token"
)

# Get studies
studies = client.studies.list(patient_id="PAT001")

# Transfer study
transfer = client.studies.transfer(
    study_id="1.2.3.4.5",
    destination="HOSP002"
)
```

### JavaScript SDK
```bash
npm install @eraif/javascript-sdk
```

```javascript
import { ERAIFClient } from '@eraif/javascript-sdk';

const client = new ERAIFClient({
  baseUrl: 'https://api.eraif.org/v1',
  token: 'your_jwt_token'
});

// Get studies
const studies = await client.studies.list({ patientId: 'PAT001' });

// Request AI analysis
const analysis = await client.ai.analyze({
  studyId: '1.2.3.4.5',
  analysisType: 'trauma_detection'
});
```

## Testing

### Test Environment
- **Base URL**: `https://api-test.eraif.org/v1`
- **Test credentials available**: Contact support
- **Sample data**: Pre-loaded test studies and patients

### API Testing Tools
```bash
# Test emergency activation
curl -X POST https://api-test.eraif.org/v1/emergency/test \
  -H "Content-Type: application/json" \
  -d '{"scenario": "hurricane", "duration": "1h"}'
```
