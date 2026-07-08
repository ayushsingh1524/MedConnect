from typing import Optional
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    """
    Represents a pharmaceutical sales representative (the application user).
    Handles authentication and maps actions (interactions, follow-ups) to a rep.
    """
    __tablename__ = "users"

    # Authentication
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50), default="field_rep", nullable=False
    )  # field_rep, manager, admin

    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
