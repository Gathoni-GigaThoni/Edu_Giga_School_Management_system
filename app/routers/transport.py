# app/routers/transport.py
"""
Endpoints for transport routes and student route assignments.

Permissions matrix
──────────────────
Endpoint                                    Min clearance
POST   /routes/                             LEVEL_2
GET    /routes/                             LEVEL_5 (any staff)
GET    /routes/{id}                         LEVEL_5
PUT    /routes/{id}                         LEVEL_2
DELETE /routes/{id}                         LEVEL_1
POST   /students/{student_id}/transport     LEVEL_2
DELETE /students/{student_id}/transport     LEVEL_2
GET    /students/{student_id}/transport     LEVEL_5
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.route import Route
from app.models.student_route import StudentRoute
from app.models.student import Student
from app.models.team import Team
from app.models.enums import ClearanceLevel
from app.schemas.route import RouteCreate, RouteRead, RouteUpdate
from app.schemas.student_route import StudentRouteAssign, StudentRouteRead
from app.dependencies import get_current_staff, require_clearance

router = APIRouter(tags=["Transport"])


# ── Routes CRUD ──────────────────────────────────────────────────────────────

@router.post("/routes/", response_model=RouteRead, status_code=status.HTTP_201_CREATED)
def create_route(
    data: RouteCreate,
    session: Session = Depends(get_session),
    _: Team = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    existing = session.exec(select(Route).where(Route.name == data.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="A route with this name already exists")

    route = Route(**data.model_dump())
    session.add(route)
    session.commit()
    session.refresh(route)
    return route


@router.get("/routes/", response_model=List[RouteRead])
def list_routes(
    session: Session = Depends(get_session),
    _: Team = Depends(get_current_staff),
):
    return session.exec(select(Route)).all()


@router.get("/routes/{route_id}", response_model=RouteRead)
def get_route(
    route_id: int,
    session: Session = Depends(get_session),
    _: Team = Depends(get_current_staff),
):
    route = session.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.put("/routes/{route_id}", response_model=RouteRead)
def update_route(
    route_id: int,
    data: RouteUpdate,
    session: Session = Depends(get_session),
    _: Team = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    route = session.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(route, field, value)

    session.add(route)
    session.commit()
    session.refresh(route)
    return route


@router.delete("/routes/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(
    route_id: int,
    session: Session = Depends(get_session),
    _: Team = Depends(require_clearance(ClearanceLevel.LEVEL_1)),
):
    route = session.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    session.delete(route)
    session.commit()


# ── Student Transport Assignment ──────────────────────────────────────────────

@router.post("/students/{student_id}/transport", response_model=StudentRouteRead, status_code=status.HTTP_201_CREATED)
def assign_student_to_route(
    student_id: int,
    data: StudentRouteAssign,
    session: Session = Depends(get_session),
    _: Team = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    route = session.get(Route, data.route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    # Deactivate any current active assignment
    active = session.exec(
        select(StudentRoute).where(
            StudentRoute.student_id == student_id,
            StudentRoute.active == True,  # noqa: E712
        )
    ).all()
    for ar in active:
        ar.active = False
        session.add(ar)

    assignment = StudentRoute(
        student_id=student_id,
        route_id=data.route_id,
        direction=data.direction,
        use_daily_rate=data.use_daily_rate,
        active=True,
    )
    session.add(assignment)

    # Keep the denormalised FK on Student in sync
    student.transport_route_id = data.route_id
    session.add(student)

    session.commit()
    session.refresh(assignment)
    return assignment


@router.delete("/students/{student_id}/transport", status_code=status.HTTP_204_NO_CONTENT)
def remove_student_from_route(
    student_id: int,
    session: Session = Depends(get_session),
    _: Team = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    active = session.exec(
        select(StudentRoute).where(
            StudentRoute.student_id == student_id,
            StudentRoute.active == True,  # noqa: E712
        )
    ).all()
    for ar in active:
        ar.active = False
        session.add(ar)

    student.transport_route_id = None
    session.add(student)
    session.commit()


@router.get("/students/{student_id}/transport", response_model=StudentRouteRead)
def get_student_transport(
    student_id: int,
    session: Session = Depends(get_session),
    _: Team = Depends(get_current_staff),
):
    assignment = session.exec(
        select(StudentRoute).where(
            StudentRoute.student_id == student_id,
            StudentRoute.active == True,  # noqa: E712
        )
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="No active transport assignment for this student")
    return assignment
