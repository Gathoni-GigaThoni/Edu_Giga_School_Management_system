from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date
from app.models.enums import LevelCode, ClassSection, HouseName

if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.parent_guardian import ParentGuardian
    from app.models.medical import MedicalHistory

class Student(SQLModel, table=True):
    __tablename__ = "student"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Human‑readable unique ID, e.g., OS-001-Okra-A-2026
    student_id: str = Field(unique=True, index=True)
    first_name: str
    last_name: str
    date_of_birth: date
    age_months: Optional[int] = None   # Will be computed on creation/update
    gender: Optional[str] = None
    level: LevelCode
    section: ClassSection
    enrollment_year: int   # The academic year they joined this level
    house: HouseName

    # Transport
    uses_transport: bool = Field(default=False)
    transport_route: Optional[str] = None

    # Foreign key to homeroom teacher (optional initially)
    homeroom_teacher_id: Optional[int] = Field(default=None, foreign_key="team.id")

    # Relationships
    homeroom_teacher: Optional["Team"] = Relationship()
    parent_guardians: List["ParentGuardian"] = Relationship(back_populates="student")
    medical_history: Optional["MedicalHistory"] = Relationship(back_populates="student")
    # Attendance and assessments will be added later

    def compute_age_months(self) -> int:
        """Calculate age in months from date_of_birth to today."""
        today = date.today()
        return (today.year - self.date_of_birth.year) * 12 + (today.month - self.date_of_birth.month)