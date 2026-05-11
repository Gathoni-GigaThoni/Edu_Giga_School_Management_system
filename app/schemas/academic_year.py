from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date
from typing import Optional, List
from app.schemas.term import TermRead


class AcademicYearCreate(BaseModel):
    name: str                   # e.g. "2025-2026"
    start_date: date
    end_date: date

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v: date, info) -> date:
        start = info.data.get("start_date")
        if start and v <= start:
            raise ValueError("end_date must be after start_date")
        return v


class AcademicYearRead(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    terms: List[TermRead] = []

    model_config = ConfigDict(from_attributes=True)


class AcademicYearReadSimple(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date

    model_config = ConfigDict(from_attributes=True)
