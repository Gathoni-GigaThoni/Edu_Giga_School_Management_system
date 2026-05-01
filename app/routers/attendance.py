# app/routers/attendance.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlmodel import Session, select
from datetime import date
from typing import List, Optional

from app.database import get_session
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.team import Team
from app.schemas.attendance import AttendanceCreate, AttendanceRead, AttendanceBulkEntry
from app.models.enums import ClearanceLevel
from app.dependencies import get_current_staff, require_clearance

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/", response_model=AttendanceRead, status_code=status.HTTP_201_CREATED)
def create_attendance_single(
    record: AttendanceCreate,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(require_clearance(ClearanceLevel.LEVEL_3))
):
    """
    Create a single attendance record. Only managers (level 3) and above.
    """
    # Verify student exists
    student = session.get(Student, record.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    db_record = Attendance.from_orm(record)
    session.add(db_record)
    session.commit()
    session.refresh(db_record)
    return db_record


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def bulk_attendance_entry(
    class_date: date = Query(..., description="Date for which attendance is being recorded"),
    entries: List[AttendanceBulkEntry] = Body(..., min_items=1, embed=False),
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff)
):
    """
    Bulk attendance entry for a whole class. Teachers can only mark their own students.
    Managers and above can mark any student.
    """
    # Teachers must only submit entries for students they are homeroom teacher of
    if current_staff.role == "teacher":
        # Get the list of student IDs the teacher is responsible for
        homeroom_student_ids = session.exec(
            select(Student.id).where(Student.homeroom_teacher_id == current_staff.id)
        ).all()

        # Validate that every submitted student is in the teacher's class
        for entry in entries:
            if entry.student_id not in homeroom_student_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You are not the homeroom teacher of student ID {entry.student_id}",
                )

    # Upsert logic: if a record already exists for this student+date, update it; else create new
    created_or_updated = []
    for entry in entries:
        existing = session.exec(
            select(Attendance).where(
                Attendance.student_id == entry.student_id,
                Attendance.attendance_date == class_date
            )
        ).first()
        if existing:
            existing.status = entry.status
            existing.notes = entry.notes
            session.add(existing)
            created_or_updated.append(existing)
        else:
            new_record = Attendance(
                student_id=entry.student_id,
                attendance_date=class_date,
                status=entry.status,
                notes=entry.notes,
            )
            session.add(new_record)
            created_or_updated.append(new_record)

    session.commit()
    return {
        "message": f"Attendance recorded for {len(created_or_updated)} students on {class_date}"
    }


@router.get("/student/{student_id}", response_model=List[AttendanceRead])
def get_student_attendance(
    student_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff)
):
    """
    Retrieve attendance records for a student, optionally filtered by date range.
    Any authenticated staff can view.
    """
    query = select(Attendance).where(Attendance.student_id == student_id)
    if start_date:
        query = query.where(Attendance.attendance_date >= start_date)
    if end_date:
        query = query.where(Attendance.attendance_date <= end_date)
    records = session.exec(query).all()
    return records


@router.get("/summary/{student_id}")
def get_attendance_summary(
    student_id: int,
    term_start: date = Query(..., description="Start date of the term"),
    term_end: date = Query(..., description="End date of the term"),
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff)
):
    """
    Returns a summary of attendance (present, absent, late counts) for a student within a date range.
    Useful for report cards.
    """
    records = session.exec(
        select(Attendance).where(
            Attendance.student_id == student_id,
            Attendance.attendance_date >= term_start,
            Attendance.attendance_date <= term_end,
        )
    ).all()

    total = len(records)
    present = sum(1 for r in records if r.status == "Present")
    absent = sum(1 for r in records if r.status == "Absent")
    late = sum(1 for r in records if r.status == "Late")

    return {
        "student_id": student_id,
        "term_start": term_start,
        "term_end": term_end,
        "total_days": total,
        "present_days": present,
        "absent_days": absent,
        "late_days": late,
    }

@router.get("/class-sheet")
def get_teacher_class_sheet(
    class_date: date = Query(..., description="Date to view attendance for"),
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff),
):
    """
    Returns the attendance sheet for the current teacher's homeroom class.
    For each student, shows their ID, name, and current status for the given date.
    """
    # Only teachers can access this endpoint; others get a 403
    if current_staff.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can view their class sheet",
        )

    # Fetch all students in the teacher's class
    students = session.exec(
        select(Student).where(Student.homeroom_teacher_id == current_staff.id)
    ).all()

    # For each student, get today's attendance record (if any)
    sheet = []
    for student in students:
        attendance = session.exec(
            select(Attendance).where(
                Attendance.student_id == student.id,
                Attendance.attendance_date == class_date,
            )
        ).first()
        sheet.append(
            {
                "student_id": student.id,
                "student_name": f"{student.first_name} {student.last_name}",
                "current_status": attendance.status if attendance else None,
                "notes": attendance.notes if attendance else None,
            }
        )

    return {
        "class_date": class_date,
        "teacher": f"{current_staff.first_name} {current_staff.last_name}",
        "students": sheet,
    }