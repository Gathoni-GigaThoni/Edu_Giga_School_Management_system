from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class SchoolClassCreate(BaseModel):
    academic_level_id: int
    academic_year_id: int
    tuition_fee: float = Field(default=0.0, ge=0)
    homeroom_teacher_id: Optional[int] = None


class SchoolClassUpdate(BaseModel):
    tuition_fee: Optional[float] = Field(default=None, ge=0)
    homeroom_teacher_id: Optional[int] = None


class SchoolClassRead(BaseModel):
    id: int
    academic_level_id: int
    academic_year_id: int
    name: str
    tuition_fee: float
    homeroom_teacher_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
