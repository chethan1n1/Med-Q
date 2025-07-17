# API Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: `https://your-api-domain.com`

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Public Endpoints

#### POST /api/intake/voice
Upload and transcribe audio file.

**Request:**
- Content-Type: multipart/form-data
- Body: audio file (WAV, MP3, etc.)

**Response:**
```json
{
  "success": true,
  "data": {
    "transcript": "I have been experiencing headaches for the past two days"
  },
  "message": "Audio transcribed successfully"
}
```

#### POST /api/intake/text
Process text input and extract medical information.

**Request:**
```json
{
  "message": "My name is John Doe",
  "current_data": {
    "current_step": "name",
    "name": null,
    "age": null,
    // ... other fields
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "Thank you John! How old are you?",
    "extracted_data": {
      "name": "John Doe",
      "current_step": "age"
    },
    "next_step": "age"
  }
}
```

#### POST /api/intake/summarize
Generate AI medical summary from intake data.

**Request:**
```json
{
  "name": "John Doe",
  "age": 30,
  "gender": "male",
  "symptoms": "Headache and fever",
  "duration": "2 days",
  "medications": "Ibuprofen",
  "allergies": "None",
  "current_step": "complete"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 0,
    "patient_id": 0,
    "summary_text": "30-year-old male presents with a 2-day history of headache and fever...",
    "structured_data": {
      "chief_complaint": "Headache and fever",
      "symptoms": ["headache", "fever"],
      "severity": "moderate",
      // ... other structured fields
    },
    "icd_codes": ["R51", "R50.9"],
    "created_at": "2025-07-17T10:00:00Z"
  }
}
```

### Authentication Endpoints

#### POST /api/auth/login
Authenticate user and get access token.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@medq.com",
      "role": "admin",
      "created_at": "2025-07-17T10:00:00Z"
    }
  }
}
```

#### GET /api/auth/me
Get current user information (requires authentication).

### Patient Management (Protected)

#### GET /api/patients/
Get all patients with pagination.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 100, max: 1000)

#### GET /api/patients/{patient_id}
Get specific patient by ID.

#### POST /api/patients/
Create new patient record.

#### GET /api/patients/{patient_id}/summary
Get medical summary for a patient.

#### GET /api/patients/{patient_id}/export/pdf
Export patient data as PDF.

### Analytics (Protected)

#### GET /api/analytics/dashboard
Get dashboard statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_patients": 150,
    "today_patients": 12,
    "avg_consultation_time": 25.5,
    "top_symptoms": [
      {"symptom": "headache", "count": 45},
      {"symptom": "fever", "count": 32}
    ],
    "patients_by_date": [
      {"date": "2025-07-17", "count": 12},
      {"date": "2025-07-16", "count": 8}
    ]
  }
}
```

#### GET /api/analytics/export
Export analytics data as CSV.

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

## Error Handling

All endpoints return errors in this format:
```json
{
  "success": false,
  "error": "Error description",
  "detail": "Detailed error message"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Rate Limiting

- Voice endpoints: 10 requests per minute
- Text processing: 30 requests per minute
- Authentication: 5 requests per minute
- Other endpoints: 60 requests per minute
