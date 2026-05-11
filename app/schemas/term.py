from pydantic import BaseModel, ConfigDict, model_validator
from datetime import date
from typing import Optional
from app.models.enums import TermName


class TermRead(BaseModel):
    id: int
    academic_year_id: int
    name: TermName
    automatic_start: date
    automatic_end: date
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class TermActualDatesUpdate(BaseModel):
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None

    @model_validator(mode="after")
    def validate_dates(self) -> "TermActualDatesUpdate":
        if self.actual_start and self.actual_end:
            if self.actual_end <= self.actual_start:
                raise ValueError("actual_end must be after actual_start")
        return self
