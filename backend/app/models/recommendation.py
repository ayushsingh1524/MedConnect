import uuid
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin

class AIRecommendation(Base, UUIDMixin, TimestampMixin):
    """
    Represents an AI-generated strategic recommendation for engaging a Doctor.
    """
    __tablename__ = "ai_recommendations"

    # Foreign Key linking to the Doctor
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )

    # Recommendation Details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Store dynamic metadata (e.g., confidence scores, source data, topics)
    metadata_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    # Track if the recommendation is still active or has been addressed
    status: Mapped[str] = mapped_column(String(50), default="active", index=True, nullable=False) # active, dismissed, completed

    # Relationships
    doctor: Mapped["Doctor"] = relationship("Doctor", foreign_keys=[doctor_id])
