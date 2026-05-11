# app/models/team.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from app.models.enums import StaffRole, ClearanceLevel

if TYPE_CHECKING:
    from app.models.class_ import SchoolClass


class Team(SQLModel, table=True):
    __tablename__ = "team"

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: StaffRole
    clearance_level: ClearanceLevel = Field(default=ClearanceLevel.LEVEL_5)
    location: str
    is_active: bool = Field(default=True)

    # A teacher can be the homeroom teacher for multiple classes
    homeroom_classes: List["SchoolClass"] = Relationship(back_populates="homeroom_teacher")
