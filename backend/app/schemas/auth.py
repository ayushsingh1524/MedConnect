"""
Pydantic schemas for authentication and user management.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# --- Request Schemas ---

class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


# --- Response Schemas ---

class UserResponse(BaseModel):
    """Schema returned when querying user data. Never exposes the password."""
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for JWT token response after successful authentication."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
