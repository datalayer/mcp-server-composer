"""API route modules."""

from .health import router as health_router
from .version import router as version_router

__all__ = ["health_router", "version_router"]
