"""API route modules."""

from .health import router as health_router
from .servers import router as servers_router
from .tools import router as tools_router
from .version import router as version_router

__all__ = ["health_router", "servers_router", "tools_router", "version_router"]
