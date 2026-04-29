# app/schemas/student_teacher.py

from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from app.models.enums import LevelCode, ClassSection, HouseName

class StudentReadTeacher(BaseModel):
    """Student information visible to homeroom teachers (no parent details)."""
    id: int
    student_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    age_months: int
    gender: Optional[str] = None
    level: LevelCode
    section: ClassSection
    enrollment_year: int
    house: HouseName
    uses_transport: bool
    transport_route: Optional[str] = None
    homeroom_teacher_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)