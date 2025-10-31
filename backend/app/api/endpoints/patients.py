"""
Patient management API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.auth import get_current_user, RoleChecker
from app.models import User, Patient, UserRole
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientListResponse
from database import get_async_session

router = APIRouter(prefix="/patients", tags=["Patients"])

# Role checker for staff (admin, secretary, doctor)
require_staff = RoleChecker([UserRole.ADMIN, UserRole.SECRETARY, UserRole.DOCTOR])


@router.get("", response_model=List[PatientListResponse])
async def list_patients(
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100,
):
    """
    List all patients for the current user's clinic
    """
    query = select(Patient).filter(
        Patient.clinic_id == current_user.clinic_id
    ).offset(skip).limit(limit).order_by(Patient.first_name, Patient.last_name)
    
    result = await db.execute(query)
    patients = result.scalars().all()
    return patients


@router.get("/me", response_model=PatientResponse)
async def get_my_patient_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get the current user's patient profile
    This endpoint is accessible to all authenticated users
    """
    # Find the patient record that corresponds to the current user
    # Since there's no direct user_id in Patient, we'll match by email
    from sqlalchemy import and_
    
    patient_query = select(Patient).filter(
        and_(
            Patient.email == current_user.email,
            Patient.clinic_id == current_user.clinic_id
        )
    )
    patient_result = await db.execute(patient_query)
    patient = patient_result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found. Please contact your clinic administrator."
        )
    
    return patient


@router.put("/me", response_model=PatientResponse)
async def update_my_patient_profile(
    patient_update: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Update the current user's patient profile
    This endpoint is accessible to all authenticated users
    """
    # Find the patient record that corresponds to the current user
    from sqlalchemy import and_
    
    patient_query = select(Patient).filter(
        and_(
            Patient.email == current_user.email,
            Patient.clinic_id == current_user.clinic_id
        )
    )
    patient_result = await db.execute(patient_query)
    patient = patient_result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found. Please contact your clinic administrator."
        )
    
    # Update patient fields
    update_data = patient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    await db.commit()
    await db.refresh(patient)
    
    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get a specific patient by ID
    """
    query = select(Patient).filter(
        Patient.id == patient_id,
        Patient.clinic_id == current_user.clinic_id
    )
    result = await db.execute(query)
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return patient


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_in: PatientCreate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Create a new patient
    """
    # Ensure the patient is created for the current user's clinic
    if patient_in.clinic_id != current_user.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create patient for a different clinic"
        )
    
    # Check if CPF already exists (if provided)
    if patient_in.cpf:
        existing_query = select(Patient).filter(
            Patient.cpf == patient_in.cpf,
            Patient.clinic_id == current_user.clinic_id
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient with this CPF already exists"
            )
    
    # Create patient
    db_patient = Patient(**patient_in.model_dump())
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)
    
    return db_patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_in: PatientUpdate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Update a patient
    """
    # Get existing patient
    query = select(Patient).filter(
        Patient.id == patient_id,
        Patient.clinic_id == current_user.clinic_id
    )
    result = await db.execute(query)
    db_patient = result.scalar_one_or_none()
    
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check if CPF is being changed and if it already exists
    if patient_in.cpf and patient_in.cpf != db_patient.cpf:
        existing_query = select(Patient).filter(
            Patient.cpf == patient_in.cpf,
            Patient.clinic_id == current_user.clinic_id,
            Patient.id != patient_id
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient with this CPF already exists"
            )
    
    # Update patient fields
    update_data = patient_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)
    
    await db.commit()
    await db.refresh(db_patient)
    
    return db_patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Delete a patient (only admins)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete patients"
        )
    
    query = select(Patient).filter(
        Patient.id == patient_id,
        Patient.clinic_id == current_user.clinic_id
    )
    result = await db.execute(query)
    db_patient = result.scalar_one_or_none()
    
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    await db.delete(db_patient)
    await db.commit()
    
    return None