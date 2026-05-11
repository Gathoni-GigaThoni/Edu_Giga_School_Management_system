"""
ParentInfo stores contact and identity details for a student's parent or guardian.
Exactly one record per student must have is_primary=True; this is enforced at the
router level. The primary contact's full_name, email, phone, and id_document are
mandatory. Any additional parent must also supply email, phone, and id_document.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from app.models.enums import ParentRelationship

if TYPE_CHECKING:
    from app.models.student import Student


class ParentInfo(SQLModel, table=True):
    __tablename__ = "parent_info"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    full_name: str
    email: str
    phone: str
    relationship: ParentRelationship
    is_primary: bool = Field(default=False)
    id_document: Optional[str] = None      # path to scanned ID
    pickup_authorized: bool = Field(default=True)

    student: Optional["Student"] = Relationship(back_populates="parents")
