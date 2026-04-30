from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.skill_assessment import SkillAssessment
from app.models.student_supply import StudentSupply
from app.models.team import Team
from app.dependencies import get_current_staff

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/teacher")
def teacher_dashboard(
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff),
):
    if current_staff.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access this dashboard",
        )

    students = session.exec(
        select(Student).where(Student.homeroom_teacher_id == current_staff.id)
    ).all()
    student_ids = [s.id for s in students]
    total_students = len(student_ids)

    today = date.today()
    attendance_records = session.exec(
        select(Attendance).where(
            Attendance.student_id.in_(student_ids),
            Attendance.attendance_date == today,
        )
    ).all() if student_ids else []

    present = sum(1 for r in attendance_records if r.status == "Present")
    absent = sum(1 for r in attendance_records if r.status == "Absent")
    late = sum(1 for r in attendance_records if r.status == "Late")
    unmarked = total_students - (present + absent + late)

    recent_assessments = []
    if student_ids:
        recent_assessments = session.exec(
            select(SkillAssessment)
            .where(SkillAssessment.student_id.in_(student_ids))
            .order_by(SkillAssessment.assessment_date.desc())
            .limit(5)
        ).all()

    low_supplies = []
    if student_ids:
        low_supplies = session.exec(
            select(StudentSupply).where(
                StudentSupply.student_id.in_(student_ids),
                StudentSupply.quantity <= 2,
            )
        ).all()

    return {
        "total_students": total_students,
        "attendance_today": {
            "present": present,
            "absent": absent,
            "late": late,
            "unmarked": unmarked,
        },
        "recent_assessments": [
            {
                "id": sa.id,
                "student_id": sa.student_id,
                "skill_id": sa.skill_id,
                "rating": sa.rating,
                "assessment_date": sa.assessment_date,
                "teacher_comment": sa.teacher_comment,
            }
            for sa in recent_assessments
        ],
        "low_supplies": [
            {
                "id": sup.id,
                "student_id": sup.student_id,
                "item_name": sup.item_name,
                "quantity": sup.quantity,
                "term": sup.term,
            }
            for sup in low_supplies
        ],
    }
