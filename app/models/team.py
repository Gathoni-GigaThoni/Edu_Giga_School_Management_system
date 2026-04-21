from sqlmodel import SQLModel, Field
from typing import Optional
from app.models.enums import StaffRole, ClearanceLevel

class Team(SQLModel, table=True):
    __tablename__ = "team"   # Optional: explicitly name the table

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str = Field(unique=True, index=True)
    role: StaffRole
    clearance_level: ClearanceLevel = Field(default=ClearanceLevel.LEVEL_5)
    location: str   # e.g., "Main Campus"
    is_active: bool = Field(default=True)