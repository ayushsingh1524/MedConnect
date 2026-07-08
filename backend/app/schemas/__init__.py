"""
Schemas package.
Centralizes all Pydantic schema imports for clean access across routers and services.

Usage:
    from app.schemas import DoctorCreate, InteractionResponse, ChatRequest
"""

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
)
from app.schemas.hcp import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    DoctorListResponse,
)
from app.schemas.interaction import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    InteractionListResponse,
    FollowUpCreate,
    FollowUpUpdate,
    FollowUpResponse,
    RecommendationResponse,
    DashboardStats,
    ChatRequest,
)

__all__ = [
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "DoctorCreate",
    "DoctorUpdate",
    "DoctorResponse",
    "DoctorListResponse",
    "InteractionCreate",
    "InteractionUpdate",
    "InteractionResponse",
    "InteractionListResponse",
    "FollowUpCreate",
    "FollowUpUpdate",
    "FollowUpResponse",
    "RecommendationResponse",
    "DashboardStats",
    "ChatRequest",
]
