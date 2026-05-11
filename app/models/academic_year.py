"""
AcademicYear represents one full school year (e.g. "2025-2026").
Creating an AcademicYear automatically generates its three Terms with default dates.
SchoolClasses are linked to an AcademicYear so cohort history is preserved.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from app.models.term import Term
    from app.models.class_ import SchoolClass


class AcademicYear(SQLModel, table=True):
    __tablename__ = "academic_year"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)   # e.g. "2025-2026"
    start_date: date                              # typically Sept 1
    end_date: date                                # typically July 31

    terms: List["Term"] = Relationship(back_populates="academic_year")
    classes: List["SchoolClass"] = Relationship(back_populates="academic_year")

    @property
    def start_year(self) -> int:
        return self.start_date.year

    @property
    def end_year(self) -> int:
        return self.end_date.year
