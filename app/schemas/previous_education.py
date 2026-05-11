from pydantic import BaseModel, ConfigDict, model_validator
from typing import Optional


class PreviousEducationCreate(BaseModel):
    has_previous: bool = False
    school_name: Optional[str] = None
    level_completed: Optional[str] = None
    document_path: Optional[str] = None

    @model_validator(mode="after")
    def details_required_when_has_previous(self) -> "PreviousEducationCreate":
        if self.has_previous and not self.school_name:
            raise ValueError("school_name is required when has_previous is True")
        if not self.has_previous:
            self.school_name = None
            self.level_completed = None
            self.document_path = None
        return self


class PreviousEducationRead(BaseModel):
    id: int
    student_id: int
    has_previous: bool
    school_name: Optional[str] = None
    level_completed: Optional[str] = None
    document_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
