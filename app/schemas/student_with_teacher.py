from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.models.enums import LevelCode, ClassSection, HouseName
from app.schemas.team import TeamRead

class StudentReadWithTeacher(BaseModel):
    id: int
    student_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    age_months: int
    gender: Optional[str]
    level: LevelCode
    section: ClassSection
    enrollment_year: int
    house: HouseName
    uses_transport: bool
    transport_route: Optional[str]
    homeroom_teacher_id: Optional[int]
    homeroom_teacher: Optional[TeamRead]  # Nested teacher details

    class Config:
        from_attributes = True