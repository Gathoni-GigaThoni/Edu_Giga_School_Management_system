from pydantic import BaseModel, validator
from datetime import date
from typing import Optional
from app.models.enums import LevelCode, ClassSection, HouseName

class StudentBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Optional[str] = None
    level: LevelCode
    section: ClassSection
    enrollment_year: int
    uses_transport: bool = False
    transport_route: Optional[str] = None
    homeroom_teacher_id: Optional[int] = None

    @validator('enrollment_year')
    def year_must_be_reasonable(cls, v):
        current_year = date.today().year
        if v < current_year - 1 or v > current_year + 1:
            raise ValueError('Enrollment year must be within one year of current year')
        return v

class StudentCreate(StudentBase):
    pass

class StudentRead(StudentBase):
    id: int
    student_id: str
    age_months: int
    house: HouseName

    class Config:
        from_attributes = True