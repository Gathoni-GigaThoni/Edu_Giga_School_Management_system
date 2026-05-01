# app/models/attendance.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date
from app.models.enums import AttendanceStatus

if TYPE_CHECKING:
    from app.models.student import Student

class Attendance(SQLModel, table=True):
    __tablename__ = "attendance"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    attendance_date: date = Field(index=True)
    status: AttendanceStatus
    notes: Optional[str] = None

    # Relationship back to Student
    student: "Student" = Relationship(back_populates="attendance_records")