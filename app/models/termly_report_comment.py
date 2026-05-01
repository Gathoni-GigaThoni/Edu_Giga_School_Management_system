from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.student import Student


class TermlyReportComment(SQLModel, table=True):
    __tablename__ = "termly_report_comment"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    term: str
    academic_year: int
    homeroom_teacher_comment: Optional[str] = None
    principal_comment: Optional[str] = None

    student: Optional["Student"] = Relationship()
