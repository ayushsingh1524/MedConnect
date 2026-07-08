"""
Routers package.
Re-exports the individual APIRouters for clean access in main.py.

Usage:
    from app.routers import auth, hcps, interactions, dashboard, chat
"""

from app.routers import auth
from app.routers import hcps
from app.routers import interactions
from app.routers import dashboard
from app.routers import chat

__all__ = [
    "auth",
    "hcps",
    "interactions",
    "dashboard",
    "chat",
]
