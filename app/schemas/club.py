from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from typing import Optional


class ClubCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class ClubRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StudentClubRead(BaseModel):
    id: int
    student_id: int
    club_id: int
    join_date: date
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
