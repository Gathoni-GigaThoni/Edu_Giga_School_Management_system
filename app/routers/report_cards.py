from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.student import Student
from app.models.team import Team
from app.models.attendance import Attendance
from app.models.skill_assessment import SkillAssessment
from app.models.skill import Skill
from app.models.termly_report_comment import TermlyReportComment
from app.schemas.termly_comment import TermlyCommentCreate, TermlyCommentRead
from app.schemas.report_card import StudentReportCard, SkillItem, AttendanceSummary
from app.dependencies import get_current_staff

router = APIRouter(prefix="/report-cards", tags=["Report Cards"])


@router.post("/comments", response_model=TermlyCommentRead, status_code=status.HTTP_201_CREATED)
def save_termly_comment(
    data: TermlyCommentCreate,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff),
):
    student = session.get(Student, data.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_staff.role == "teacher" and student.homeroom_teacher_id != current_staff.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only comment on your own homeroom students",
        )

    existing = session.exec(
        select(TermlyReportComment).where(
            TermlyReportComment.student_id == data.student_id,
            TermlyReportComment.term == data.term,
            TermlyReportComment.academic_year == data.academic_year,
        )
    ).first()

    if existing:
        if data.homeroom_teacher_comment is not None:
            existing.homeroom_teacher_comment = data.homeroom_teacher_comment
        if data.principal_comment is not None:
            existing.principal_comment = data.principal_comment
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    record = TermlyReportComment(**data.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.get("/{student_id}", response_model=StudentReportCard)
def get_report_card(
    student_id: int,
    term: str = Query(...),
    academic_year: int = Query(...),
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff),
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_staff.role == "teacher" and student.homeroom_teacher_id != current_staff.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view report cards for your own homeroom students",
        )

    # Skill assessments for this term
    assessments = session.exec(
        select(SkillAssessment).where(
            SkillAssessment.student_id == student_id,
            SkillAssessment.term == term,
            SkillAssessment.academic_year == academic_year,
        )
    ).all()

    skills = []
    for sa in assessments:
        skill = session.get(Skill, sa.skill_id)
        if skill:
            skills.append(SkillItem(
                skill_name=skill.name,
                category=skill.category,
                rating=sa.rating,
                teacher_comment=sa.teacher_comment,
            ))

    # Attendance summary (all records for the student in this academic year)
    attendance_records = session.exec(
        select(Attendance).where(Attendance.student_id == student_id)
    ).all()
    total = len(attendance_records)
    present = sum(1 for r in attendance_records if r.status == "Present")
    absent = sum(1 for r in attendance_records if r.status == "Absent")
    late = sum(1 for r in attendance_records if r.status == "Late")

    # Termly comments
    comment_record = session.exec(
        select(TermlyReportComment).where(
            TermlyReportComment.student_id == student_id,
            TermlyReportComment.term == term,
            TermlyReportComment.academic_year == academic_year,
        )
    ).first()

    return StudentReportCard(
        student_id=student.student_id,
        full_name=f"{student.first_name} {student.last_name}",
        level=student.level.value,
        section=student.section.value,
        term=term,
        academic_year=academic_year,
        skills=skills,
        attendance=AttendanceSummary(
            total_days=total,
            present_days=present,
            absent_days=absent,
            late_days=late,
        ),
        homeroom_teacher_comment=comment_record.homeroom_teacher_comment if comment_record else None,
        principal_comment=comment_record.principal_comment if comment_record else None,
    )
