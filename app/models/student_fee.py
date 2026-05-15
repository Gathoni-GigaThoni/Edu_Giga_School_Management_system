from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from datetime import date

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.fee_item import FeeItem
    from app.models.term import Term
    from app.models.academic_year import AcademicYear
    from app.models.payment_allocation import PaymentAllocation


class StudentFee(SQLModel, table=True):
    __tablename__ = "student_fee"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    fee_item_id: int = Field(foreign_key="fee_item.id", index=True)
    term_id: Optional[int] = Field(default=None, foreign_key="term.id", index=True)
    academic_year_id: int = Field(foreign_key="academic_year.id", index=True)
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    is_paid: bool = Field(default=False)
    date_charged: date = Field(default_factory=date.today)
    date_paid: Optional[date] = Field(default=None)
    source_ref: Optional[str] = Field(default=None)

    student: Optional["Student"] = Relationship()
    fee_item: Optional["FeeItem"] = Relationship(back_populates="student_fees")
    term: Optional["Term"] = Relationship()
    academic_year: Optional["AcademicYear"] = Relationship()
    allocations: List["PaymentAllocation"] = Relationship(back_populates="student_fee")
