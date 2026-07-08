"""
Models package.
Centralizes all SQLAlchemy ORM model imports so that Alembic and other
consumers can discover every table via a single import.

Usage:
    from app.models import Base, User, Doctor, Interaction, FollowUp, AIRecommendation
"""

from app.models.base import Base
from app.models.user import User
from app.models.doctor import Doctor
from app.models.interaction import Interaction
from app.models.followup import FollowUp
from app.models.recommendation import AIRecommendation

__all__ = [
    "Base",
    "User",
    "Doctor",
    "Interaction",
    "FollowUp",
    "AIRecommendation",
]
