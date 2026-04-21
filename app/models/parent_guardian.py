from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class ParentGuardian(SQLModel, table=True):
    __tablename__ = "parent_guardian"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    full_name: str
    relationship: str   # e.g., "Mother", "Father", "Guardian"
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    is_emergency_contact: bool = Field(default=True)

    # Relationship back to student
    student: "Student" = Relationship(back_populates="parent_guardians")