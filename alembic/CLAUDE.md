# Seven Oak Kindergarten Management System

## Stack
- Backend: FastAPI, SQLModel, PostgreSQL
- Migrations: Alembic
- Auth: JWT (python-jose + bcrypt)
- Testing: pytest + TestClient

## Architecture
- app/models/   – SQLModel database models
- app/schemas/  – Pydantic request/response schemas
- app/routers/  – FastAPI route handlers
- app/dependencies.py – authorization dependencies
- app/auth.py   – JWT creation/verification, password hashing

## Key Rules
- All database queries must use the session from Depends(get_session)
- Use the custom render_item in alembic/env.py to avoid sqlmodel import in migrations
- Role-based access: super_admin, manager, teacher, kitchen, utility (clearance levels 1-5)
- Teacher can only access their own homeroom students for certain endpoints
- Student ID format: OS-{seq}-{level}-{section}-{year}