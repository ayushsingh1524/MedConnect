"""
FastAPI Dependencies.
Provides reusable dependencies for route handlers, such as database sessions
and authenticated user injection.
"""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User

# In a real production app, you would decode the JWT here.
# For this scaffolding, we simulate a mock auth dependency.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user based on the provided token.
    (Mock implementation: In production, verify JWT and lookup user).
    """
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    
    if not user:
        # For this scaffolding, auto-create a mock user if DB is empty
        import uuid
        user = User(
            id=uuid.uuid4(),
            email="demo@medconnect.com",
            full_name="Demo User",
            hashed_password="mock",
            is_active=True
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to ensure the current user is active.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
