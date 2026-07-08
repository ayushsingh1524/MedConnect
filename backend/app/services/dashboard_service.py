"""
Service layer for Dashboard aggregation logic.
Computes KPIs and statistics for the main dashboard view.
"""

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.doctor import Doctor
from app.models.interaction import Interaction
from app.models.followup import FollowUp
from app.schemas.interaction import DashboardStats


async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
    """
    Compute aggregate statistics for the dashboard.
    Executes optimised COUNT queries rather than loading all rows.
    """
    # Total doctors
    doctor_count = await db.execute(select(func.count(Doctor.id)))
    total_doctors = doctor_count.scalar() or 0

    # Total interactions
    interaction_count = await db.execute(select(func.count(Interaction.id)))
    total_interactions = interaction_count.scalar() or 0

    # Pending follow-ups
    pending_count = await db.execute(
        select(func.count(FollowUp.id)).where(FollowUp.status == "pending")
    )
    pending_follow_ups = pending_count.scalar() or 0

    # Positive sentiment percentage
    if total_interactions > 0:
        positive_count = await db.execute(
            select(func.count(Interaction.id)).where(
                Interaction.sentiment == "positive"
            )
        )
        positive = positive_count.scalar() or 0
        positive_sentiment_pct = round((positive / total_interactions) * 100, 1)
    else:
        positive_sentiment_pct = 0.0

    return DashboardStats(
        total_doctors=total_doctors,
        total_interactions=total_interactions,
        pending_follow_ups=pending_follow_ups,
        positive_sentiment_pct=positive_sentiment_pct,
    )


async def get_recent_interactions(db: AsyncSession, limit: int = 10):
    """Retrieve the most recent interactions for the dashboard timeline."""
    result = await db.execute(
        select(Interaction)
        .order_by(Interaction.interaction_date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_upcoming_follow_ups(db: AsyncSession, limit: int = 10):
    """Retrieve the nearest pending follow-ups sorted by due date."""
    result = await db.execute(
        select(FollowUp)
        .where(FollowUp.status == "pending")
        .order_by(FollowUp.due_date.asc())
        .limit(limit)
    )
    return list(result.scalars().all())
