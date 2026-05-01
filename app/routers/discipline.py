from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models.discipline import DisciplinaryLog
from app.models.student import Student
from app.models.team import Team
from app.schemas.discipline import DisciplinaryLogCreate, DisciplinaryLogRead, DisciplinaryLogUpdate
from app.models.enums import ClearanceLevel
from app.dependencies import get_current_staff, require_clearance

router = APIRouter(prefix="/discipline", tags=["Discipline"])


@router.post("/", response_model=DisciplinaryLogRead, status_code=status.HTTP_201_CREATED)
def create_log(
    data: DisciplinaryLogCreate,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(require_clearance(ClearanceLevel.LEVEL_3)),
):
    student = session.get(Student, data.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    log = DisciplinaryLog(
        **data.model_dump(),
        reported_by_id=current_staff.id,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


@router.get("/student/{student_id}", response_model=List[DisciplinaryLogRead])
def get_student_logs(
    student_id: int,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff),
):
    return session.exec(
        select(DisciplinaryLog)
        .where(DisciplinaryLog.student_id == student_id)
        .order_by(DisciplinaryLog.incident_date.desc())
    ).all()


@router.patch("/{log_id}/resolve", response_model=DisciplinaryLogRead)
def resolve_log(
    log_id: int,
    data: DisciplinaryLogUpdate,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(require_clearance(ClearanceLevel.LEVEL_3)),
):
    log = session.get(DisciplinaryLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Disciplinary log not found")

    log.is_resolved = data.is_resolved
    log.resolution_notes = data.resolution_notes
    session.add(log)
    session.commit()
    session.refresh(log)
    return log
