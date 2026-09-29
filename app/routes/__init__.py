"""
Routes package for Market Predictor
Contains all route modules organized by development phases
"""

from .phase1_5 import router as phase1_5_router
from .phase6_10 import router as phase6_10_router
from .phase11_18 import router as phase11_18_router

__all__ = [
    "phase1_5_router",
    "phase6_10_router", 
    "phase11_18_router"
]