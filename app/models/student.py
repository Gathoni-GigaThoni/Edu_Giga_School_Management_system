from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date
from app.models.enums import LevelCode, ClassSection, HouseName

if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.parent_guardian import ParentGuardian
    from app.models.medical import MedicalHistory
    from app.models.attendance import Attendance
    from app.models.skill_assessment import SkillAssessment
    from app.models.student_supply import StudentSupply

class Student(SQLModel, table=True):
    __tablename__ = "student"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: str = Field(unique=True, index=True)
    first_name: str
    last_name: str
    date_of_birth: date
    age_months: Optional[int] = None
    gender: Optional[str] = None
    level: LevelCode
    section: ClassSection
    enrollment_year: int
    house: HouseName

    uses_transport: bool = Field(default=False)
    transport_route: Optional[str] = None

    homeroom_teacher_id: Optional[int] = Field(default=None, foreign_key="team.id")

    # Relationships
    homeroom_teacher: Optional["Team"] = Relationship()
    parent_guardians: List["ParentGuardian"] = Relationship(back_populates="student")
    medical_history: Optional["MedicalHistory"] = Relationship(back_populates="student")
    
    attendance_records: List["Attendance"] = Relationship(back_populates="student")
    skill_assessments: List["SkillAssessment"] = Relationship(back_populates="student")
    supplies: List["StudentSupply"] = Relationship(back_populates="student")

    def compute_age_months(self) -> int:
        """Calculate age in months from date_of_birth to today."""
        today = date.today()
        return (today.year - self.date_of_birth.year) * 12 + (today.month - self.date_of_birth.month)