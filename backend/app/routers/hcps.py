"""
API routes for Healthcare Professionals (HCPs / Doctors).
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.hcp import DoctorCreate, DoctorUpdate, DoctorResponse, DoctorListResponse
from app.services import (
    create_doctor,
    get_doctor_by_id,
    get_all_doctors,
    update_doctor,
    delete_doctor,
)
from app.routers.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def create_new_doctor(
    data: DoctorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new doctor (HCP) record."""
    return await create_doctor(db, data)


@router.get("/", response_model=DoctorListResponse)
async def list_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    specialty: Optional[str] = None,
    city: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve a paginated list of doctors with optional filtering."""
    doctors, total = await get_all_doctors(
        db, skip=skip, limit=limit, specialty=specialty, city=city, search=search
    )
    return {"total": total, "doctors": doctors}


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(
    doctor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve a specific doctor by UUID."""
    doctor = await get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.get("/{doctor_id}/profile")
async def get_doctor_profile(
    doctor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve a specific doctor along with their interactions and recommendations."""
    doctor = await get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    from app.services.interaction_service import get_interactions
    interactions, _ = await get_interactions(db, doctor_id=doctor_id, limit=20)
    
    from app.models.recommendation import AIRecommendation
    from sqlalchemy import select
    result = await db.execute(select(AIRecommendation).where(AIRecommendation.doctor_id == doctor_id).order_by(AIRecommendation.created_at.desc()))
    recommendations = result.scalars().all()
    
    return {
        "doctor": doctor,
        "interactions": interactions,
        "recommendations": recommendations
    }


@router.patch("/{doctor_id}", response_model=DoctorResponse)
async def update_existing_doctor(
    doctor_id: uuid.UUID,
    data: DoctorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Partially update a doctor's information."""
    updated = await update_doctor(db, doctor_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return updated


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_doctor(
    doctor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a doctor record."""
    deleted = await delete_doctor(db, doctor_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Doctor not found")
