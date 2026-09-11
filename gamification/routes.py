"""Project Volusia — Gamification Routes Bridge v3.0
Re-exports gamification endpoints from backend.gamification module.
This module bridges the standalone gamification routes module to the main app.
"""
from gamification import (
    get_gamification_routes,
    _init_gamification_db,
)

# Re-export the route registration function for backward compatibility
__all__ = ["get_gamification_routes", "_init_gamification_db"]