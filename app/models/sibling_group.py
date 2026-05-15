from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.student import Student


class SiblingGroup(SQLModel, table=True):
    __tablename__ = "sibling_group"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    students: List["Student"] = Relationship(back_populates="sibling_group")
