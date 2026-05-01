# app/schemas/team.py

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.enums import StaffRole, ClearanceLevel

class TeamBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    role: StaffRole
    clearance_level: ClearanceLevel = ClearanceLevel.LEVEL_5
    location: str = Field(..., min_length=1)
    is_active: bool = True

class TeamCreate(TeamBase):
    password: str = Field(..., min_length=8)   # plain password, never stored

class TeamRead(TeamBase):
    id: int
    # password is never returned

    model_config = ConfigDict(from_attributes=True)