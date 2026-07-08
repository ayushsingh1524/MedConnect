"""
API routes for the Dashboard.
Provides aggregated KPIs, recent activity timeline, and upcoming tasks.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.interaction import (
    DashboardStats,
    InteractionResponse,
    FollowUpResponse,
)
from app.services import (
    get_dashboard_stats,
    get_recent_interactions,
    get_upcoming_follow_ups,
)
from app.routers.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def fetch_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve aggregated high-level KPIs for the dashboard.
    (Total doctors, total interactions, pending follow-ups, sentiment %).
    """
    return await get_dashboard_stats(db)


@router.get("/timeline", response_model=list[InteractionResponse])
async def fetch_recent_timeline(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve the most recent interactions to populate the dashboard timeline widget.
    """
    return await get_recent_interactions(db, limit=limit)


@router.get("/tasks", response_model=list[FollowUpResponse])
async def fetch_upcoming_tasks(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve upcoming pending follow-ups to populate the dashboard tasks widget.
    """
    return await get_upcoming_follow_ups(db, limit=limit)


@router.get("/summary")
async def fetch_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Aggregated dashboard endpoint that returns stats, recent interactions,
    and upcoming follow-ups in a single response. This is what the frontend
    Dashboard page consumes.
    """
    stats = await get_dashboard_stats(db)
    recent = await get_recent_interactions(db, limit=10)
    tasks = await get_upcoming_follow_ups(db, limit=10)
    return {
        "stats": stats,
        "recent_interactions": recent,
        "upcoming_follow_ups": tasks,
    }

