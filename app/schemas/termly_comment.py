from pydantic import BaseModel, ConfigDict
from typing import Optional


class TermlyCommentBase(BaseModel):
    student_id: int
    term: str
    academic_year: int
    homeroom_teacher_comment: Optional[str] = None
    principal_comment: Optional[str] = None


class TermlyCommentCreate(TermlyCommentBase):
    pass


class TermlyCommentRead(TermlyCommentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
