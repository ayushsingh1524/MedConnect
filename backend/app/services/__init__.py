"""
Services package.
Re-exports service functions for convenient access from routers and tools.

Usage:
    from app.services import create_doctor, create_interaction, get_dashboard_stats
"""

from app.services.hcp_service import (
    create_doctor,
    get_doctor_by_id,
    get_all_doctors,
    update_doctor,
    delete_doctor,
)
from app.services.interaction_service import (
    create_interaction,
    get_interaction_by_id,
    get_interactions,
    update_interaction,
    delete_interaction,
    create_follow_up,
    get_follow_ups,
    update_follow_up,
)
from app.services.dashboard_service import (
    get_dashboard_stats,
    get_recent_interactions,
    get_upcoming_follow_ups,
)

__all__ = [
    "create_doctor",
    "get_doctor_by_id",
    "get_all_doctors",
    "update_doctor",
    "delete_doctor",
    "create_interaction",
    "get_interaction_by_id",
    "get_interactions",
    "update_interaction",
    "delete_interaction",
    "create_follow_up",
    "get_follow_ups",
    "update_follow_up",
    "get_dashboard_stats",
    "get_recent_interactions",
    "get_upcoming_follow_ups",
]
