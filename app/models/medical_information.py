"""
MedicalInformation holds a student's current health conditions with document paths.
One-to-one with Student (unique FK). Document paths are references only; actual
file storage is handled externally (e.g. cloud storage).
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.student import Student


class MedicalInformation(SQLModel, table=True):
    __tablename__ = "medical_information"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", unique=True, index=True)
    allergies: Optional[str] = None
    allergies_document: Optional[str] = None
    chronic_symptoms: Optional[str] = None
    chronic_document: Optional[str] = None
    vaccination_document: Optional[str] = None

    student: Optional["Student"] = Relationship(back_populates="medical_info")
