from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class MedicalHistory(SQLModel, table=True):
    __tablename__ = "medical_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", unique=True)   # One‑to‑one
    allergies: Optional[str] = None
    medications: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None
    notes: Optional[str] = None

    student: "Student" = Relationship(back_populates="medical_history")