from pydantic import BaseModel, validator, Field
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

    @validator('date_of_birth')
    def dob_must_be_in_past(cls, v):
        if v >= date.today():
            raise ValueError('Date of birth must be in the past')
        # Kindergarten students are typically 3-6 years old
        age = date.today().year - v.year
        if age < 2 or age > 7:
            raise ValueError('Student age must be between 2 and 7 years')
        return v

    @validator('transport_route')
    def route_required_if_uses_transport(cls, v, values):
        if values.get('uses_transport') and not v:
            raise ValueError('Transport route is required when uses_transport is True')
        return v

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