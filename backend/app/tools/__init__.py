"""
Tools package.
Re-exports all tools so they can be easily bound to the LangGraph agent.

Usage:
    from app.tools import ALL_TOOLS
"""

from app.tools.crm_tools import (
    log_interaction,
    edit_interaction,
    schedule_follow_up,
)
from app.tools.search_tools import (
    search_interactions,
    ai_recommendation,
    search_doctors,
)

# List of all tools available to the LangGraph agent
ALL_TOOLS = [
    log_interaction,
    edit_interaction,
    schedule_follow_up,
    search_interactions,
    ai_recommendation,
    search_doctors,
]

__all__ = [
    "ALL_TOOLS",
    "log_interaction",
    "edit_interaction",
    "schedule_follow_up",
    "search_interactions",
    "ai_recommendation",
    "search_doctors",
]
