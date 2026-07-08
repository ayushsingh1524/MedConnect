"""
Pydantic schemas for Interaction, Follow-up, and AI Recommendation management.
"""

import uuid
from typing import Optional, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field


# ==================== Interaction Schemas ====================

class InteractionCreate(BaseModel):
    """Schema for logging a new interaction (used by both REST form and AI agent)."""
    doctor_id: uuid.UUID
    interaction_date: date
    interaction_type: Literal["in-person", "phone", "email", "video", "conference"]
    raw_notes: Optional[str] = None
    ai_summary: Optional[str] = None
    sentiment: Optional[Literal["positive", "neutral", "negative"]] = "neutral"
    products_discussed: Optional[list[str]] = Field(default_factory=list)
    follow_up_date: Optional[date] = None
    status: Optional[str] = "completed"


class InteractionUpdate(BaseModel):
    """Schema for editing an existing interaction. All fields optional."""
    interaction_date: Optional[date] = None
    interaction_type: Optional[str] = None
    raw_notes: Optional[str] = None
    ai_summary: Optional[str] = None
    sentiment: Optional[str] = None
    products_discussed: Optional[list[str]] = None
    follow_up_date: Optional[date] = None
    status: Optional[str] = None


class InteractionResponse(BaseModel):
    """Schema returned when querying interaction data."""
    id: uuid.UUID
    doctor_id: uuid.UUID
    interaction_date: date
    interaction_type: str
    raw_notes: Optional[str] = None
    ai_summary: Optional[str] = None
    sentiment: Optional[str] = None
    products_discussed: Optional[list[str]] = None
    follow_up_date: Optional[date] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InteractionListResponse(BaseModel):
    """Paginated response for interaction listings."""
    total: int
    interactions: list[InteractionResponse]


# ==================== Follow-up Schemas ====================

class FollowUpCreate(BaseModel):
    """Schema for scheduling a new follow-up."""
    doctor_id: uuid.UUID
    interaction_id: Optional[uuid.UUID] = None
    due_date: date
    description: str = Field(..., min_length=1, max_length=500)
    priority: Literal["low", "medium", "high", "urgent"] = "medium"


class FollowUpUpdate(BaseModel):
    """Schema for updating an existing follow-up."""
    due_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[str] = None
    status: Optional[Literal["pending", "completed", "cancelled"]] = None


class FollowUpResponse(BaseModel):
    """Schema returned when querying follow-up data."""
    id: uuid.UUID
    doctor_id: uuid.UUID
    interaction_id: Optional[uuid.UUID] = None
    due_date: date
    description: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== AI Recommendation Schemas ====================

class RecommendationResponse(BaseModel):
    """Schema returned when querying AI recommendation data."""
    id: uuid.UUID
    doctor_id: uuid.UUID
    title: str
    description: str
    metadata_data: dict
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ==================== Dashboard Schemas ====================

class DashboardStats(BaseModel):
    """Aggregated statistics for the dashboard."""
    total_doctors: int
    total_interactions: int
    pending_follow_ups: int
    positive_sentiment_pct: float


# ==================== AI Chat Schemas ====================

class ChatRequest(BaseModel):
    """Schema for an incoming AI chat message."""
    message: str = Field(..., min_length=1)
    doctor_id: Optional[uuid.UUID] = None
