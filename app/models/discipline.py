from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.models.enums import InfractionSeverity

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.team import Team


class DisciplinaryLog(SQLModel, table=True):
    __tablename__ = "disciplinary_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    reported_by_id: int = Field(foreign_key="team.id")
    incident_date: datetime = Field(default_factory=datetime.utcnow)
    description: str
    action_taken: Optional[str] = None
    severity: InfractionSeverity
    is_resolved: bool = Field(default=False)
    resolution_notes: Optional[str] = None

    student: Optional["Student"] = Relationship(back_populates="disciplinary_logs")
    reported_by: Optional["Team"] = Relationship()
