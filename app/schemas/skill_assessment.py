from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from app.models.enums import SkillRating


class SkillAssessmentBase(BaseModel):
    student_id: int
    skill_id: int
    term: str
    academic_year: int
    rating: SkillRating
    teacher_comment: Optional[str] = None


class SkillAssessmentCreate(SkillAssessmentBase):
    pass


class SkillAssessmentRead(SkillAssessmentBase):
    id: int
    assessment_date: date

    model_config = ConfigDict(from_attributes=True)


class SkillAssessmentBulkEntry(BaseModel):
    student_id: int
    skill_id: int
    rating: SkillRating
    teacher_comment: Optional[str] = None
