from pydantic import BaseModel, EmailStr
from app.models.enums import StaffRole, ClearanceLevel

class TeamBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr   # Built‑in email validation
    role: StaffRole
    clearance_level: ClearanceLevel = ClearanceLevel.LEVEL_5
    location: str
    is_active: bool = True

class TeamCreate(TeamBase):
    pass

class TeamRead(TeamBase):
    id: int

    class Config:
        from_attributes = True   # Allows conversion from SQLModel objects