"""
API routes for Interactions and Follow-ups.
Handles the REST form submissions for logging interactions.
"""

import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.interaction import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    InteractionListResponse,
    FollowUpCreate,
    FollowUpUpdate,
    FollowUpResponse,
)
from app.services import (
    create_interaction,
    get_interaction_by_id,
    get_interactions,
    update_interaction,
    delete_interaction,
    create_follow_up,
    get_follow_ups,
    update_follow_up,
)
from app.routers.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


# ==================== Interaction Routes ====================

@router.post("/", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def log_new_interaction(
    data: InteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Log a new interaction (REST API entry point)."""
    return await create_interaction(db, data)


@router.get("/", response_model=InteractionListResponse)
async def list_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    doctor_id: Optional[uuid.UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve a paginated list of interactions with optional filtering."""
    interactions, total = await get_interactions(
        db, skip=skip, limit=limit, doctor_id=doctor_id,
        date_from=date_from, date_to=date_to, search=search
    )
    return {"total": total, "interactions": interactions}


# ==================== Follow-up Routes ====================

@router.post("/follow-ups", response_model=FollowUpResponse, status_code=status.HTTP_201_CREATED)
async def create_new_follow_up(
    data: FollowUpCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Schedule a new follow-up."""
    return await create_follow_up(db, data)


@router.get("/follow-ups", response_model=list[FollowUpResponse])
async def list_follow_ups(
    doctor_id: Optional[uuid.UUID] = None,
    follow_up_status: Optional[str] = "pending",
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve follow-ups."""
    return await get_follow_ups(db, doctor_id=doctor_id, status=follow_up_status, skip=skip, limit=limit)


@router.patch("/follow-ups/{follow_up_id}", response_model=FollowUpResponse)
async def modify_follow_up(
    follow_up_id: uuid.UUID,
    data: FollowUpUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a follow-up task (e.g., mark as completed)."""
    updated = await update_follow_up(db, follow_up_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return updated


@router.get("/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(
    interaction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve a specific interaction by UUID."""
    interaction = await get_interaction_by_id(db, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.patch("/{interaction_id}", response_model=InteractionResponse)
async def modify_interaction(
    interaction_id: uuid.UUID,
    data: InteractionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Partially update an interaction."""
    updated = await update_interaction(db, interaction_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return updated


@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_interaction(
    interaction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an interaction."""
    deleted = await delete_interaction(db, interaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Interaction not found")



