# app/routers/supplies.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from datetime import date
from typing import List, Optional

from app.database import get_session
from app.models.student_supply import StudentSupply
from app.models.student import Student
from app.models.team import Team
from app.schemas.student_supply import StudentSupplyCreate, StudentSupplyRead
from app.dependencies import get_current_staff, require_clearance
from app.models.enums import ClearanceLevel

router = APIRouter(prefix="/supplies", tags=["Supplies"])


@router.post("/", response_model=StudentSupplyRead, status_code=status.HTTP_201_CREATED)
def add_supply(
    supply_data: StudentSupplyCreate,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff)
):
    """
    Add a supply item for a student. Only the homeroom teacher (or higher roles)
    can add supplies. Teachers can only add for their own homeroom students.
    """
    # 1. Verify student exists
    student = session.get(Student, supply_data.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    # 2. Access control: only homeroom teacher (or manager/admin) can add
    if current_staff.role == "teacher":
        if student.homeroom_teacher_id != current_staff.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only add supplies for your own students",
            )

    # 3. Create the supply record
    db_supply = StudentSupply(
        **supply_data.dict(),
        date_recorded=date.today()
    )
    session.add(db_supply)
    session.commit()
    session.refresh(db_supply)
    return db_supply


@router.get("/student/{student_id}", response_model=List[StudentSupplyRead])
def get_student_supplies(
    student_id: int,
    term: Optional[str] = Query(None, description="Filter by term, e.g., 'Term 1 2026'"),
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff)
):
    """
    Retrieve all supply records for a student, optionally filtered by term.
    Any authenticated staff can view.
    """
    query = select(StudentSupply).where(StudentSupply.student_id == student_id)
    if term:
        query = query.where(StudentSupply.term == term)
    supplies = session.exec(query).all()
    return supplies


@router.get("/my-class-supplies")
def get_my_class_supplies(
    term: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff)
):
    """
    Get supplies for all students in the current teacher's homeroom class.
    Only accessible by teachers.
    """
    if current_staff.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access their class supplies",
        )

    query = select(StudentSupply).join(Student).where(
        Student.homeroom_teacher_id == current_staff.id
    )
    if term:
        query = query.where(StudentSupply.term == term)

    supplies = session.exec(query).all()
    return supplies