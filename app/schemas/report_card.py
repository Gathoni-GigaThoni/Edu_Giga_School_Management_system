from pydantic import BaseModel
from typing import Optional, List
from app.models.enums import SkillRating


class SkillItem(BaseModel):
    skill_name: str
    category: str
    rating: SkillRating
    teacher_comment: Optional[str] = None


class AttendanceSummary(BaseModel):
    total_days: int
    present_days: int
    absent_days: int
    late_days: int


class StudentReportCard(BaseModel):
    student_id: str
    full_name: str
    level: str
    section: str
    term: str
    academic_year: int
    skills: List[SkillItem]
    attendance: AttendanceSummary
    homeroom_teacher_comment: Optional[str] = None
    principal_comment: Optional[str] = None
