import uuid
from typing import Optional
from datetime import date
from sqlalchemy import String, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin

class FollowUp(Base, UUIDMixin, TimestampMixin):
    """
    Represents a scheduled follow-up action or task for a Doctor.
    """
    __tablename__ = "follow_ups"

    # Foreign Keys
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )
    # Optional link to the specific interaction that generated this follow-up
    interaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("interactions.id", ondelete="SET NULL"), 
        index=True, 
        nullable=True
    )

    # Follow-up Details
    due_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="medium", nullable=False) # low, medium, high, urgent
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True, nullable=False) # pending, completed, cancelled

    # Relationships
    doctor: Mapped["Doctor"] = relationship("Doctor", foreign_keys=[doctor_id])
    interaction: Mapped[Optional["Interaction"]] = relationship("Interaction", foreign_keys=[interaction_id])
