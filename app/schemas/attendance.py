# app/schemas/attendance.py

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from app.models.enums import AttendanceStatus

class AttendanceBase(BaseModel):
    student_id: int
    attendance_date: date
    status: AttendanceStatus
    notes: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceRead(AttendanceBase):
    id: int

    class Config:
        from_attributes = True

# Schema for bulk entry – teacher submits a list of these
class AttendanceBulkEntry(BaseModel):
    student_id: int
    status: AttendanceStatus
    notes: Optional[str] = None