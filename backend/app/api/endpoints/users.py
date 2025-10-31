"""
User management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.auth import get_current_user, RoleChecker
from app.models import User, UserRole
from database import get_async_session
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])

# Role checker for staff
require_staff = RoleChecker([UserRole.ADMIN, UserRole.SECRETARY, UserRole.DOCTOR])


class UserListResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[UserListResponse])
async def list_users(
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_async_session),
    role: Optional[UserRole] = Query(None),
):
    """
    List users in the current clinic, optionally filtered by role
    """
    query = select(User).filter(
        User.clinic_id == current_user.clinic_id,
        User.is_active == True
    )
    
    if role:
        query = query.filter(User.role == role)
    
    query = query.order_by(User.first_name, User.last_name)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users


@router.get("/doctors", response_model=List[UserListResponse])
async def get_doctors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get list of doctors for patients to book appointments
    This endpoint is accessible to all authenticated users
    """
    query = select(User).filter(
        User.clinic_id == current_user.clinic_id,
        User.role == UserRole.DOCTOR,
        User.is_active == True
    ).order_by(User.first_name, User.last_name)
    
    result = await db.execute(query)
    doctors = result.scalars().all()
    
    return [UserListResponse.model_validate(doctor) for doctor in doctors]
