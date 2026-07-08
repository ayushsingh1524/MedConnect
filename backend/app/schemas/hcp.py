"""
Pydantic schemas for Healthcare Professional (Doctor) management.
"""

import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# --- Request Schemas ---

class DoctorCreate(BaseModel):
    """Schema for creating a new doctor record."""
    name: str = Field(..., min_length=1, max_length=255)
    specialty: str = Field(..., min_length=1, max_length=100)
    hospital: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)


class DoctorUpdate(BaseModel):
    """Schema for updating an existing doctor record. All fields are optional."""
    name: Optional[str] = Field(None, max_length=255)
    specialty: Optional[str] = Field(None, max_length=100)
    hospital: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)


# --- Response Schemas ---

class DoctorResponse(BaseModel):
    """Schema returned when querying doctor data."""
    id: uuid.UUID
    name: str
    specialty: str
    hospital: str
    city: str
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DoctorListResponse(BaseModel):
    """Paginated response for doctor listings."""
    total: int
    doctors: list[DoctorResponse]
