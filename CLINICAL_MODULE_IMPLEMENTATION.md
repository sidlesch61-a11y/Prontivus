# Clinical Module Implementation

## Overview
Complete Clinical Module with SOAP notes, prescriptions, and exam requests integrated with appointments.

## ✅ Completed Features

### Database Schema

#### **ClinicalRecord Model** (`backend/app/models/clinical.py`)
- **One-to-One** relationship with Appointment
- **SOAP Format Fields:**
  - `subjective` - Patient's complaints and symptoms
  - `objective` - Physical exam findings, vital signs
  - `assessment` - Diagnosis or clinical impression
  - `plan` - Treatment plan
- **Relationships:**
  - `appointment` - Link to appointment
  - `prescriptions` - List of prescribed medications
  - `exam_requests` - List of requested exams
- **Cascade Delete** - When appointment is deleted, clinical record and all prescriptions/exams are deleted

#### **Prescription Model**
- Linked to ClinicalRecord
- **Fields:**
  - `medication_name` - Name of medication
  - `dosage` - Dosage amount (e.g., "500mg", "10ml")
  - `frequency` - How often to take (e.g., "3x ao dia", "8 em 8 horas")
  - `duration` - How long to take (e.g., "7 dias", "2 semanas")
  - `instructions` - Special instructions
  - `issued_date` - When prescription was issued
  - `is_active` - Whether prescription is still active

#### **ExamRequest Model**
- Linked to ClinicalRecord
- **Fields:**
  - `exam_type` - Type of exam (e.g., "Hemograma", "Raio-X", "Ultrassom")
  - `description` - Additional details
  - `reason` - Clinical indication
  - `urgency` - ROUTINE, URGENT, or EMERGENCY
  - `requested_date` - When exam was requested
  - `completed` - Whether exam has been completed
  - `completed_date` - When exam was completed

### Backend API Endpoints

#### **Clinical Records** (`/api/appointments/{id}/clinical-record`)

1. **POST /api/appointments/{appointment_id}/clinical-record**
   - Create or update SOAP note for an appointment
   - **Authorization:** Doctor or Admin only
   - **Validation:** Only the assigned doctor can create/update records
   - **Idempotent:** Creates new or updates existing record

2. **GET /api/appointments/{appointment_id}/clinical-record**
   - Get clinical record with all prescriptions and exam requests
   - **Authorization:** Staff only

3. **GET /api/patients/{patient_id}/clinical-records**
   - Get complete clinical history for a patient
   - Returns all appointments with their clinical records
   - **Authorization:** Staff only
   - **Ordered by:** Most recent appointments first

#### **Prescriptions**

1. **POST /api/clinical-records/{record_id}/prescriptions**
   - Add prescription to a clinical record
   - **Authorization:** Doctor or Admin only

2. **GET /api/clinical-records/{record_id}/prescriptions**
   - List all prescriptions for a clinical record
   - **Authorization:** Staff only

3. **PUT /api/prescriptions/{prescription_id}**
   - Update prescription details
   - **Authorization:** Doctor or Admin only

4. **DELETE /api/prescriptions/{prescription_id}**
   - Delete a prescription
   - **Authorization:** Doctor or Admin only

#### **Exam Requests**

1. **POST /api/clinical-records/{record_id}/exam-requests**
   - Add exam request to a clinical record
   - **Authorization:** Doctor or Admin only

2. **GET /api/clinical-records/{record_id}/exam-requests**
   - List all exam requests for a clinical record
   - **Authorization:** Staff only

3. **PUT /api/exam-requests/{exam_request_id}**
   - Update exam request (e.g., mark as completed)
   - **Authorization:** Doctor or Admin only

4. **DELETE /api/exam-requests/{exam_request_id}**
   - Delete an exam request
   - **Authorization:** Doctor or Admin only

### Pydantic Schemas (`backend/app/schemas/clinical.py`)

- `ClinicalRecordCreate` - Create/update SOAP note
- `ClinicalRecordResponse` - Clinical record data
- `ClinicalRecordDetailResponse` - Clinical record with prescriptions and exams
- `PrescriptionCreate` - Add prescription
- `PrescriptionResponse` - Prescription data
- `ExamRequestCreate` - Add exam request
- `ExamRequestResponse` - Exam request data
- `PatientClinicalHistoryResponse` - Patient history entry

## 🔐 Security & Authorization

1. **Doctor-Only Operations:**
   - Creating/updating clinical records
   - Adding/modifying prescriptions
   - Adding/modifying exam requests

2. **Staff Access:**
   - Viewing clinical records
   - Viewing patient history
   - Viewing prescriptions and exams

3. **Clinic Isolation:**
   - All records scoped to user's clinic
   - No cross-clinic access

4. **Doctor Assignment:**
   - Only the assigned doctor can create clinical records for their appointments
   - Admins can override

## 📋 Usage Examples

### Create SOAP Note

```http
POST /api/appointments/10/clinical-record
Authorization: Bearer {doctor_token}
Content-Type: application/json

{
  "appointment_id": 10,
  "subjective": "Paciente relata dor de cabeça persistente há 3 dias. Dor pulsátil, intensidade 7/10, piora com luz.",
  "objective": "PA: 120/80 mmHg, FC: 72 bpm, Temp: 36.5°C. Exame neurológico normal. Sem sinais meníngeos.",
  "assessment": "Cefaleia tensional provável. Descartar enxaqueca.",
  "plan": "1. Prescrever analgésico\n2. Solicitar exames\n3. Retorno em 7 dias se não melhorar"
}

Response: 201 Created
{
  "id": 5,
  "appointment_id": 10,
  "subjective": "Paciente relata dor de cabeça...",
  "objective": "PA: 120/80 mmHg...",
  "assessment": "Cefaleia tensional provável...",
  "plan": "1. Prescrever analgésico...",
  "created_at": "2025-10-26T00:30:00Z",
  "prescriptions": [],
  "exam_requests": []
}
```

### Add Prescription

```http
POST /api/clinical-records/5/prescriptions
Authorization: Bearer {doctor_token}
Content-Type: application/json

{
  "clinical_record_id": 5,
  "medication_name": "Paracetamol",
  "dosage": "500mg",
  "frequency": "8 em 8 horas",
  "duration": "7 dias",
  "instructions": "Tomar com alimentos. Não exceder 4g por dia."
}

Response: 201 Created
{
  "id": 12,
  "clinical_record_id": 5,
  "medication_name": "Paracetamol",
  "dosage": "500mg",
  "frequency": "8 em 8 horas",
  "duration": "7 dias",
  "instructions": "Tomar com alimentos. Não exceder 4g por dia.",
  "issued_date": "2025-10-26T00:35:00Z",
  "is_active": true
}
```

### Add Exam Request

```http
POST /api/clinical-records/5/exam-requests
Authorization: Bearer {doctor_token}
Content-Type: application/json

{
  "clinical_record_id": 5,
  "exam_type": "Hemograma Completo",
  "description": "Avaliar hemácias, leucócitos, plaquetas",
  "reason": "Investigação de cefaleia persistente",
  "urgency": "routine"
}

Response: 201 Created
{
  "id": 8,
  "clinical_record_id": 5,
  "exam_type": "Hemograma Completo",
  "description": "Avaliar hemácias, leucócitos, plaquetas",
  "reason": "Investigação de cefaleia persistente",
  "urgency": "routine",
  "requested_date": "2025-10-26T00:36:00Z",
  "completed": false,
  "completed_date": null
}
```

### Get Patient Clinical History

```http
GET /api/patients/1/clinical-records
Authorization: Bearer {staff_token}

Response: 200 OK
[
  {
    "appointment_id": 10,
    "appointment_date": "2025-10-26T14:30:00Z",
    "doctor_name": "John Smith",
    "appointment_type": "Consulta Geral",
    "clinical_record": {
      "id": 5,
      "subjective": "Paciente relata dor de cabeça...",
      "objective": "PA: 120/80 mmHg...",
      "assessment": "Cefaleia tensional provável...",
      "plan": "1. Prescrever analgésico...",
      "prescriptions": [
        {
          "id": 12,
          "medication_name": "Paracetamol",
          "dosage": "500mg",
          "frequency": "8 em 8 horas",
          "duration": "7 dias"
        }
      ],
      "exam_requests": [
        {
          "id": 8,
          "exam_type": "Hemograma Completo",
          "urgency": "routine",
          "completed": false
        }
      ]
    }
  },
  {
    "appointment_id": 5,
    "appointment_date": "2025-10-15T10:00:00Z",
    "doctor_name": "John Smith",
    "appointment_type": "Retorno",
    "clinical_record": null
  }
]
```

### Update Exam Status (Mark as Completed)

```http
PUT /api/exam-requests/8
Authorization: Bearer {doctor_token}
Content-Type: application/json

{
  "completed": true,
  "completed_date": "2025-10-28T09:00:00Z"
}

Response: 200 OK
```

## 🗄️ Database Schema

```sql
-- Clinical Records Table
CREATE TABLE clinical_records (
    id SERIAL PRIMARY KEY,
    subjective TEXT,
    objective TEXT,
    assessment TEXT,
    plan TEXT,
    appointment_id INTEGER UNIQUE NOT NULL REFERENCES appointments(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Prescriptions Table
CREATE TABLE prescriptions (
    id SERIAL PRIMARY KEY,
    clinical_record_id INTEGER NOT NULL REFERENCES clinical_records(id),
    medication_name VARCHAR(200) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    duration VARCHAR(100),
    instructions TEXT,
    issued_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Exam Requests Table
CREATE TABLE exam_requests (
    id SERIAL PRIMARY KEY,
    clinical_record_id INTEGER NOT NULL REFERENCES clinical_records(id),
    exam_type VARCHAR(200) NOT NULL,
    description TEXT,
    reason TEXT,
    urgency VARCHAR(20) DEFAULT 'routine',
    requested_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed BOOLEAN DEFAULT FALSE,
    completed_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## 🔧 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── clinical.py ✨ NEW
│   ├── models/
│   │   ├── __init__.py (updated with clinical_record relationship)
│   │   └── clinical.py ✨ NEW
│   └── schemas/
│       └── clinical.py ✨ NEW
├── alembic/
│   └── versions/
│       └── 2025_10_26_0015-xxx_add_clinical_tables.py ✨ NEW
└── main.py (clinical router registered)
```

## 🎯 Workflow Example

### Complete Appointment Workflow

1. **Appointment Created**
   - Patient schedules appointment
   - Status: SCHEDULED

2. **Patient Arrives**
   - Secretary checks patient in
   - Status: CHECKED_IN

3. **Doctor Consultation**
   - Doctor starts consultation
   - Status: IN_CONSULTATION
   - Doctor creates clinical record with SOAP notes
   - Doctor adds prescriptions
   - Doctor requests exams

4. **Complete Appointment**
   - Doctor finishes consultation
   - Status: COMPLETED
   - Patient receives prescriptions
   - Patient schedules requested exams

5. **Patient History**
   - All past appointments with clinical records available
   - Prescriptions history
   - Exam results

## 🚀 Testing

### Manual Testing Steps

1. **Complete an Appointment:**
   ```bash
   # Login as doctor
   # Navigate to appointment
   # Change status to "In Consultation"
   ```

2. **Create Clinical Record:**
   ```bash
   POST /api/appointments/10/clinical-record
   # Add SOAP notes
   ```

3. **Add Prescription:**
   ```bash
   POST /api/clinical-records/5/prescriptions
   # Add medication details
   ```

4. **Add Exam Request:**
   ```bash
   POST /api/clinical-records/5/exam-requests
   # Add exam details
   ```

5. **View Patient History:**
   ```bash
   GET /api/patients/1/clinical-records
   # See all past records
   ```

## ⚠️ Important Notes

1. **One-to-One Relationship:**
   - Each appointment can have only ONE clinical record
   - Creating a new clinical record for an appointment that already has one will UPDATE the existing record

2. **Cascade Delete:**
   - Deleting an appointment will delete its clinical record
   - Deleting a clinical record will delete all its prescriptions and exam requests

3. **Doctor Authorization:**
   - Only the assigned doctor (or admin) can create/update clinical records for an appointment
   - This prevents unauthorized access to patient medical records

4. **SOAP Format:**
   - All fields are optional to allow flexibility
   - Doctors can save partial notes and complete them later

## 📈 Future Enhancements

1. **Prescription Templates** - Common medications with pre-filled dosages
2. **Exam Result Uploads** - Attach PDF/image exam results
3. **ICD-10 Codes** - Link diagnoses to standard medical codes
4. **Clinical Templates** - Save and reuse common SOAP note templates
5. **E-Prescription** - Digital signature and electronic transmission
6. **Lab Integration** - Automatic exam result retrieval
7. **Medical History Summary** - Auto-generate patient summaries
8. **Drug Interaction Checker** - Alert for dangerous medication combinations

---

## 🎉 Implementation Complete!

The Clinical Module is fully functional with:
- ✅ SOAP note creation and management
- ✅ Prescription management
- ✅ Exam request management
- ✅ Patient clinical history
- ✅ Doctor-only authorization
- ✅ Complete CRUD operations
- ✅ Database migration applied

**Ready for clinical use!** 🏥

