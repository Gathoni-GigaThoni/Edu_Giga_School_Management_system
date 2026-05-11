"""
SchoolClass is one class group for a given AcademicLevel in a given AcademicYear.
Its name is auto-generated as "{level.name} {academic_year.end_year}" (e.g. "Maple 2026").
The homeroom teacher is assigned here; student IDs are partially derived from the level code.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.academic_level import AcademicLevel
    from app.models.academic_year import AcademicYear
    from app.models.team import Team
    from app.models.student import Student


class SchoolClass(SQLModel, table=True):
    __tablename__ = "school_class"

    id: Optional[int] = Field(default=None, primary_key=True)
    academic_level_id: int = Field(foreign_key="academic_level.id", index=True)
    academic_year_id: int = Field(foreign_key="academic_year.id", index=True)
    name: str = Field(index=True)           # e.g. "Maple 2026" — set by service
    tuition_fee: float = Field(default=0.0)
    homeroom_teacher_id: Optional[int] = Field(default=None, foreign_key="team.id")

    academic_level: Optional["AcademicLevel"] = Relationship(back_populates="classes")
    academic_year: Optional["AcademicYear"] = Relationship(back_populates="classes")
    homeroom_teacher: Optional["Team"] = Relationship(back_populates="homeroom_classes")
    students: List["Student"] = Relationship(back_populates="school_class")
