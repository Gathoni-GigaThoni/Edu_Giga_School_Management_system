from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date
from typing import Optional
from app.models.enums import LevelCode, ClassSection, HouseName

class StudentBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    gender: Optional[str] = None
    level: LevelCode
    section: ClassSection
    enrollment_year: int = Field(..., ge=2020, le=2100)
    uses_transport: bool = False
    transport_route: Optional[str] = None
    homeroom_teacher_id: Optional[int] = None

    @field_validator('date_of_birth')
    @classmethod
    def dob_must_be_in_past(cls, v):
        if v >= date.today():
            raise ValueError('Date of birth must be in the past')
        age = date.today().year - v.year
        if age < 2 or age > 7:
            raise ValueError('Student age must be between 2 and 7 years')
        return v

    @field_validator('transport_route')
    @classmethod
    def route_required_if_uses_transport(cls, v):
        return v

    @field_validator('enrollment_year')
    @classmethod
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

    model_config = ConfigDict(from_attributes=True)
