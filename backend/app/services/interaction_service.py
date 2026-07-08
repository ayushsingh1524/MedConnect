"""
Service layer for Interaction and Follow-up operations.
Unified sink for both REST form submissions and LangGraph tool calls.
"""

import uuid
from typing import Optional
from datetime import date
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.interaction import Interaction
from app.models.followup import FollowUp
from app.schemas.interaction import (
    InteractionCreate,
    InteractionUpdate,
    FollowUpCreate,
    FollowUpUpdate,
)


# ==================== Interaction Operations ====================

async def create_interaction(db: AsyncSession, data: InteractionCreate) -> Interaction:
    """
    Log a new interaction. This is the single entry point used by both
    the traditional REST form and the LangGraph agent tools.
    """
    interaction = Interaction(**data.model_dump())
    db.add(interaction)
    await db.flush()
    await db.refresh(interaction)
    return interaction


async def get_interaction_by_id(
    db: AsyncSession, interaction_id: uuid.UUID
) -> Optional[Interaction]:
    """Retrieve a single interaction by UUID."""
    result = await db.execute(
        select(Interaction).where(Interaction.id == interaction_id)
    )
    return result.scalar_one_or_none()


async def get_interactions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    doctor_id: Optional[uuid.UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
) -> tuple[list[Interaction], int]:
    """
    Retrieve a paginated list of interactions with optional filtering.
    Returns a tuple of (interactions, total_count).
    """
    query = select(Interaction)
    count_query = select(func.count(Interaction.id))

    # Apply filters
    if doctor_id:
        query = query.where(Interaction.doctor_id == doctor_id)
        count_query = count_query.where(Interaction.doctor_id == doctor_id)
    if date_from:
        query = query.where(Interaction.interaction_date >= date_from)
        count_query = count_query.where(Interaction.interaction_date >= date_from)
    if date_to:
        query = query.where(Interaction.interaction_date <= date_to)
        count_query = count_query.where(Interaction.interaction_date <= date_to)
    if search:
        search_filter = or_(
            Interaction.raw_notes.ilike(f"%{search}%"),
            Interaction.ai_summary.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    # Total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Pagination and ordering (most recent first)
    query = query.order_by(Interaction.interaction_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    interactions = list(result.scalars().all())

    return interactions, total


async def update_interaction(
    db: AsyncSession, interaction_id: uuid.UUID, data: InteractionUpdate
) -> Optional[Interaction]:
    """Update an existing interaction. Only updates fields that are provided."""
    interaction = await get_interaction_by_id(db, interaction_id)
    if not interaction:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interaction, field, value)

    await db.flush()
    await db.refresh(interaction)
    return interaction


async def delete_interaction(db: AsyncSession, interaction_id: uuid.UUID) -> bool:
    """Delete an interaction record."""
    interaction = await get_interaction_by_id(db, interaction_id)
    if not interaction:
        return False
    await db.delete(interaction)
    await db.flush()
    return True


# ==================== Follow-up Operations ====================

async def create_follow_up(db: AsyncSession, data: FollowUpCreate) -> FollowUp:
    """Schedule a new follow-up task."""
    follow_up = FollowUp(**data.model_dump())
    db.add(follow_up)
    await db.flush()
    await db.refresh(follow_up)
    return follow_up


async def get_follow_ups(
    db: AsyncSession,
    doctor_id: Optional[uuid.UUID] = None,
    status: Optional[str] = "pending",
    skip: int = 0,
    limit: int = 20,
) -> list[FollowUp]:
    """Retrieve follow-ups with optional filtering by doctor and status."""
    query = select(FollowUp)

    if doctor_id:
        query = query.where(FollowUp.doctor_id == doctor_id)
    if status:
        query = query.where(FollowUp.status == status)

    query = query.order_by(FollowUp.due_date.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_follow_up(
    db: AsyncSession, follow_up_id: uuid.UUID, data: FollowUpUpdate
) -> Optional[FollowUp]:
    """Update an existing follow-up."""
    result = await db.execute(
        select(FollowUp).where(FollowUp.id == follow_up_id)
    )
    follow_up = result.scalar_one_or_none()
    if not follow_up:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(follow_up, field, value)

    await db.flush()
    await db.refresh(follow_up)
    return follow_up
