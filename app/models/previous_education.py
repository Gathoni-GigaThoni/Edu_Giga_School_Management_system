"""
PreviousEducation stores a student's schooling history before joining Seven Oak.
One-to-one with Student (unique FK). If has_previous is False all detail fields
should be null; this is enforced at the schema/router level.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.student import Student


class PreviousEducation(SQLModel, table=True):
    __tablename__ = "previous_education"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", unique=True, index=True)
    has_previous: bool = Field(default=False)
    school_name: Optional[str] = None
    level_completed: Optional[str] = None
    document_path: Optional[str] = None   # path to uploaded transfer certificate

    student: Optional["Student"] = Relationship(back_populates="previous_education")
