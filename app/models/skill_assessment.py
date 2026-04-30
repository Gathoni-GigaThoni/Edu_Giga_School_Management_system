from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date
from app.models.enums import SkillRating

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.skill import Skill


class SkillAssessment(SQLModel, table=True):
    __tablename__ = "skill_assessment"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    skill_id: int = Field(foreign_key="skill.id", index=True)
    term: str
    academic_year: int
    rating: SkillRating
    teacher_comment: Optional[str] = None
    assessment_date: date = Field(default_factory=date.today)

    student: Optional["Student"] = Relationship(back_populates="skill_assessments")
    skill: Optional["Skill"] = Relationship()
