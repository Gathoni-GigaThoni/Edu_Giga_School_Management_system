from app.routers.team import router as team_router
from app.routers.students import router as students_router

# Optional: define __all__ for explicit exports
__all__ = ["team_router", "students_router"]