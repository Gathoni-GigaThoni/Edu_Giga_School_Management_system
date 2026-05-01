from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlmodel import Session, select
from typing import List, Optional

from app.database import get_session
from app.models.skill import Skill
from app.models.skill_assessment import SkillAssessment
from app.models.student import Student
from app.models.team import Team
from app.schemas.skill import SkillCreate, SkillRead
from app.schemas.skill_assessment import SkillAssessmentBulkEntry, SkillAssessmentRead
from app.models.enums import ClearanceLevel
from app.dependencies import get_current_staff, require_clearance

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.post("/catalog", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_data: SkillCreate,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    skill = Skill(**skill_data.model_dump())
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@router.get("/catalog", response_model=List[SkillRead])
def list_skills(
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff),
):
    return session.exec(select(Skill)).all()


@router.post("/assessments/bulk", status_code=status.HTTP_201_CREATED)
def bulk_skill_assessment(
    term: str = Query(...),
    academic_year: int = Query(...),
    entries: List[SkillAssessmentBulkEntry] = Body(...),
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff),
):
    if current_staff.role == "teacher":
        homeroom_ids = set(
            session.exec(
                select(Student.id).where(Student.homeroom_teacher_id == current_staff.id)
            ).all()
        )
        for entry in entries:
            if entry.student_id not in homeroom_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You are not the homeroom teacher of student ID {entry.student_id}",
                )

    saved = []
    for entry in entries:
        existing = session.exec(
            select(SkillAssessment).where(
                SkillAssessment.student_id == entry.student_id,
                SkillAssessment.skill_id == entry.skill_id,
                SkillAssessment.term == term,
                SkillAssessment.academic_year == academic_year,
            )
        ).first()
        if existing:
            existing.rating = entry.rating
            existing.teacher_comment = entry.teacher_comment
            session.add(existing)
            saved.append(existing)
        else:
            record = SkillAssessment(
                student_id=entry.student_id,
                skill_id=entry.skill_id,
                term=term,
                academic_year=academic_year,
                rating=entry.rating,
                teacher_comment=entry.teacher_comment,
            )
            session.add(record)
            saved.append(record)

    session.commit()
    return {"message": f"Saved {len(saved)} assessment(s) for {term} {academic_year}"}


@router.get("/assessments/student/{student_id}", response_model=List[SkillAssessmentRead])
def get_student_assessments(
    student_id: int,
    term: Optional[str] = Query(None),
    academic_year: Optional[int] = Query(None),
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff),
):
    query = select(SkillAssessment).where(SkillAssessment.student_id == student_id)
    if term:
        query = query.where(SkillAssessment.term == term)
    if academic_year:
        query = query.where(SkillAssessment.academic_year == academic_year)
    return session.exec(query).all()
