from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from app.models.enums import StaffRole, ClearanceLevel

if TYPE_CHECKING:
    from app.models.student import Student

class Team(SQLModel, table=True):
    __tablename__ = "team"

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str = Field(unique=True, index=True)
    role: StaffRole
    clearance_level: ClearanceLevel = Field(default=ClearanceLevel.LEVEL_5)
    location: str
    is_active: bool = Field(default=True)

    # Relationship: a teacher can be homeroom for many students
    students: List["Student"] = Relationship(back_populates="homeroom_teacher")