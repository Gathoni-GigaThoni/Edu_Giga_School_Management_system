"""
AcademicLevel is a database-backed grade level (e.g. Maple, Acorn, Willow, Oak).
Using a table (instead of a static enum) allows levels to be added or renamed
without a code change. The short code is used in student ID generation.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.class_ import SchoolClass
    from app.models.student import Student


class AcademicLevel(SQLModel, table=True):
    __tablename__ = "academic_level"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)   # e.g. "Maple"
    code: str = Field(max_length=2)              # e.g. "M"
    description: Optional[str] = None

    classes: List["SchoolClass"] = Relationship(back_populates="academic_level")
    students: List["Student"] = Relationship(back_populates="academic_level")
