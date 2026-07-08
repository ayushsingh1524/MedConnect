from typing import Optional, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin

class Doctor(Base, UUIDMixin, TimestampMixin):
    """
    Represents a Healthcare Professional (HCP) / Doctor in the CRM.
    """
    __tablename__ = "doctors"

    # Core details
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    
    # Location
    hospital: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    
    # Contact information (Optional)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    # A doctor can have multiple interactions
    interactions: Mapped[List["Interaction"]] = relationship(
        "Interaction", 
        back_populates="doctor",
        cascade="all, delete-orphan"
    )
