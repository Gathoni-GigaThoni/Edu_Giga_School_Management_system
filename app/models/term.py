"""
Term represents one of three academic terms within an AcademicYear.
automatic_start/end are the planned dates set when the academic year is created.
actual_start/end can be patched later to reflect real-world date adjustments.
Actual dates are validated to fall within the automatic window at the service layer.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date
from app.models.enums import TermName

if TYPE_CHECKING:
    from app.models.academic_year import AcademicYear


class Term(SQLModel, table=True):
    __tablename__ = "term"

    id: Optional[int] = Field(default=None, primary_key=True)
    academic_year_id: int = Field(foreign_key="academic_year.id", index=True)
    name: TermName
    automatic_start: date
    automatic_end: date
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None

    academic_year: Optional["AcademicYear"] = Relationship(back_populates="terms")

    @property
    def effective_start(self) -> date:
        return self.actual_start or self.automatic_start

    @property
    def effective_end(self) -> date:
        return self.actual_end or self.automatic_end
