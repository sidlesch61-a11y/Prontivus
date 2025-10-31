# CliniCore Database Models - Summary

## ✅ Models Created

All core SQLAlchemy ORM models have been successfully created in `/backend/app/models/__init__.py`.

## 📊 Database Schema

### 1. **Clinic Model**
Healthcare facilities/clinics in the system.

**Fields:**
- `id` (PK) - Primary key
- `name` - Clinic name
- `legal_name` - Legal business name
- `tax_id` - Tax ID/CNPJ (unique)
- `address` - Physical address
- `phone` - Contact phone
- `email` - Contact email
- `is_active` - Active status
- `created_at`, `updated_at` - Timestamps

**Relationships:**
- Has many Users
- Has many Patients
- Has many Appointments

---

### 2. **User Model**
System users with role-based access.

**Fields:**
- `id` (PK) - Primary key
- `username` - Unique username
- `email` - Unique email
- `hashed_password` - Encrypted password
- `first_name`, `last_name` - User name
- `role` - Enum: admin, secretary, doctor, patient
- `is_active` - Account status
- `is_verified` - Email verification status
- `clinic_id` (FK) - Foreign key to Clinic
- `created_at`, `updated_at` - Timestamps

**Relationships:**
- Belongs to one Clinic
- Has many Appointments (as doctor)

**Enums:**
- `UserRole`: ADMIN, SECRETARY, DOCTOR, PATIENT

---

### 3. **Patient Model**
Patient records with medical history.

**Fields:**
- `id` (PK) - Primary key
- `first_name`, `last_name` - Patient name
- `date_of_birth` - Birth date
- `gender` - Enum: male, female, other, prefer_not_to_say
- `cpf` - Brazilian CPF (unique)
- `phone` - Contact phone
- `email` - Contact email
- `address` - Physical address
- `emergency_contact_name` - Emergency contact person
- `emergency_contact_phone` - Emergency phone
- `emergency_contact_relationship` - Relationship to patient
- `allergies` - Medical allergies
- `active_problems` - Current health issues
- `blood_type` - Blood type (A+, B-, O+, etc.)
- `notes` - Additional notes
- `is_active` - Active status
- `clinic_id` (FK) - Foreign key to Clinic
- `created_at`, `updated_at` - Timestamps

**Relationships:**
- Belongs to one Clinic
- Has many Appointments

**Computed Properties:**
- `full_name` - Returns "First Last"
- `age` - Calculates current age from date_of_birth

---

### 4. **Appointment Model**
Medical appointments with detailed tracking.

**Fields:**
- `id` (PK) - Primary key
- `scheduled_datetime` - Appointment date/time
- `duration_minutes` - Duration (default 30)
- `status` - Enum: scheduled, checked_in, in_consultation, completed, cancelled
- `appointment_type` - Type (consultation, follow-up, emergency, etc.)
- `notes` - General notes
- `reason` - Reason for visit
- `diagnosis` - Doctor's diagnosis
- `treatment_plan` - Prescribed treatment
- `checked_in_at` - Check-in timestamp
- `started_at` - Consultation start time
- `completed_at` - Completion time
- `cancelled_at` - Cancellation time
- `cancellation_reason` - Reason for cancellation
- `patient_id` (FK) - Foreign key to Patient
- `doctor_id` (FK) - Foreign key to User
- `clinic_id` (FK) - Foreign key to Clinic
- `created_at`, `updated_at` - Timestamps

**Relationships:**
- Belongs to one Patient
- Belongs to one Doctor (User)
- Belongs to one Clinic

**Enums:**
- `AppointmentStatus`: SCHEDULED, CHECKED_IN, IN_CONSULTATION, COMPLETED, CANCELLED

**Computed Properties:**
- `is_past` - Returns true if appointment is in the past

---

## 🔗 Relationships Summary

```
Clinic (1) ──→ (N) Users
Clinic (1) ──→ (N) Patients
Clinic (1) ──→ (N) Appointments

Patient (1) ──→ (N) Appointments
User/Doctor (1) ──→ (N) Appointments
```

## 📁 File Structure

```
backend/
├── app/
│   ├── __init__.py
│   └── models/
│       └── __init__.py          # All models defined here
├── alembic/
│   ├── versions/               # Migration files (to be created)
│   └── env.py                  # Updated to import from app.models
├── database.py                 # Database connection
└── requirements.txt            # Updated dependencies
```

## 🚀 Next Steps

### 1. Create PostgreSQL Database

```powershell
psql -U postgres
CREATE DATABASE clinicore;
\q
```

### 2. Update .env File

Edit `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/clinicore
```

### 3. Create and Run Migration

```powershell
cd backend
.\venv\Scripts\Activate.ps1

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 4. Verify Tables Created

```powershell
psql -U postgres -d clinicore
\dt
```

You should see:
- clinics
- users
- patients
- appointments

## 📝 Example Usage

### Creating a Clinic
```python
from app.models import Clinic
from database import AsyncSessionLocal

async with AsyncSessionLocal() as session:
    clinic = Clinic(
        name="HealthCare Plus",
        legal_name="HealthCare Plus LTDA",
        tax_id="12.345.678/0001-90",
        email="contact@healthcareplus.com",
        phone="+55 11 98765-4321"
    )
    session.add(clinic)
    await session.commit()
```

### Creating a Doctor
```python
from app.models import User, UserRole

doctor = User(
    username="dr.smith",
    email="dr.smith@clinic.com",
    hashed_password="...",  # Use password hashing
    first_name="John",
    last_name="Smith",
    role=UserRole.DOCTOR,
    clinic_id=1
)
```

### Creating a Patient
```python
from app.models import Patient, Gender
from datetime import date

patient = Patient(
    first_name="Maria",
    last_name="Silva",
    date_of_birth=date(1990, 5, 15),
    gender=Gender.FEMALE,
    cpf="123.456.789-00",
    phone="+55 11 91234-5678",
    email="maria@example.com",
    clinic_id=1
)
```

### Creating an Appointment
```python
from app.models import Appointment, AppointmentStatus
from datetime import datetime, timedelta

appointment = Appointment(
    scheduled_datetime=datetime.now() + timedelta(days=1),
    status=AppointmentStatus.SCHEDULED,
    appointment_type="consultation",
    reason="Regular checkup",
    patient_id=1,
    doctor_id=2,
    clinic_id=1
)
```

## 🔧 Features

### Enums for Type Safety
- `UserRole`: ADMIN, SECRETARY, DOCTOR, PATIENT
- `AppointmentStatus`: SCHEDULED, CHECKED_IN, IN_CONSULTATION, COMPLETED, CANCELLED
- `Gender`: MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY

### Timestamps
All models include:
- `created_at` - Automatically set on creation
- `updated_at` - Automatically updated on modification

### Cascading Deletes
- Deleting a Clinic cascades to all its Users, Patients, and Appointments
- Deleting a Patient cascades to all their Appointments

### Indexes
Strategic indexes on frequently queried fields:
- All foreign keys
- username, email (users)
- cpf, email (patients)
- scheduled_datetime, status (appointments)

---

**Status:** ✅ Models Created | ⏳ Awaiting Database Setup & Migration

