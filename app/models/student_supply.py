# app/models/student_supply.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from app.models.student import Student

class StudentSupply(SQLModel, table=True):
    __tablename__ = "student_supply"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    item_name: str                          # e.g. "Pencils (pack of 12)"
    quantity: int = Field(default=1, ge=1)  # at least 1
    term: str                                # e.g. "Term 1 2026"
    date_recorded: date = Field(default_factory=date.today)
    notes: Optional[str] = None              # e.g. "brought extra eraser"

    # Relationship back to Student
    student: "Student" = Relationship(back_populates="supplies")