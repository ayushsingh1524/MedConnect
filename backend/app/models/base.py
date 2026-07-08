import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy declarative models.
    """
    pass

class UUIDMixin:
    """
    Provides a UUID primary key for models.
    Using UUIDs over sequential integers is a best practice for distributed systems and API security.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4, 
        index=True
    )

class TimestampMixin:
    """
    Provides created_at and updated_at timestamps for models.
    Automatically manages the timestamps on creation and updates.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
