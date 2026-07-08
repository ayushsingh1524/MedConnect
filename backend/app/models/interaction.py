import uuid
from typing import Optional, List
from datetime import date
from sqlalchemy import String, Text, ForeignKey, Date, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin

class Interaction(Base, UUIDMixin, TimestampMixin):
    """
    Represents an interaction (visit, call, email, etc.) between a rep and a Doctor.
    """
    __tablename__ = "interactions"

    # Foreign Key linking to the Doctor
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )

    # Core Interaction Data
    interaction_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., 'in-person', 'email', 'phone'
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    
    # Content & AI Extracted Data
    raw_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sentiment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # e.g., 'positive', 'neutral', 'negative'
    products_discussed: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Follow-up
    follow_up_date: Mapped[Optional[date]] = mapped_column(Date, index=True, nullable=True)

    # Relationships
    # Back-reference to the Doctor model
    doctor: Mapped["Doctor"] = relationship(
        "Doctor", 
        back_populates="interactions"
    )
