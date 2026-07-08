"""
Service layer for Healthcare Professional (Doctor) operations.
Encapsulates all database logic for the Doctor entity.
"""

import uuid
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.doctor import Doctor
from app.schemas.hcp import DoctorCreate, DoctorUpdate


async def create_doctor(db: AsyncSession, data: DoctorCreate) -> Doctor:
    """Create a new doctor record."""
    doctor = Doctor(**data.model_dump())
    db.add(doctor)
    await db.flush()
    await db.refresh(doctor)
    return doctor


async def get_doctor_by_id(db: AsyncSession, doctor_id: uuid.UUID) -> Optional[Doctor]:
    """Retrieve a single doctor by UUID."""
    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    return result.scalar_one_or_none()


async def get_all_doctors(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    specialty: Optional[str] = None,
    city: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[list[Doctor], int]:
    """
    Retrieve a paginated list of doctors with optional filtering.
    Returns a tuple of (doctors, total_count).
    """
    query = select(Doctor)
    count_query = select(func.count(Doctor.id))

    # Apply filters
    if specialty:
        query = query.where(Doctor.specialty.ilike(f"%{specialty}%"))
        count_query = count_query.where(Doctor.specialty.ilike(f"%{specialty}%"))
    if city:
        query = query.where(Doctor.city.ilike(f"%{city}%"))
        count_query = count_query.where(Doctor.city.ilike(f"%{city}%"))
    if search:
        search_filter = Doctor.name.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(Doctor.name).offset(skip).limit(limit)
    result = await db.execute(query)
    doctors = list(result.scalars().all())

    return doctors, total


async def update_doctor(
    db: AsyncSession, doctor_id: uuid.UUID, data: DoctorUpdate
) -> Optional[Doctor]:
    """Update an existing doctor record. Only updates fields that are provided."""
    doctor = await get_doctor_by_id(db, doctor_id)
    if not doctor:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doctor, field, value)

    await db.flush()
    await db.refresh(doctor)
    return doctor


async def delete_doctor(db: AsyncSession, doctor_id: uuid.UUID) -> bool:
    """Delete a doctor record. Returns True if deleted, False if not found."""
    doctor = await get_doctor_by_id(db, doctor_id)
    if not doctor:
        return False

    await db.delete(doctor)
    await db.flush()
    return True
