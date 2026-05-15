from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from datetime import date
from app.models.enums import PaymentMethod

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.team import Team
    from app.models.payment_allocation import PaymentAllocation


class Payment(SQLModel, table=True):
    __tablename__ = "payment"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    payment_date: date = Field(default_factory=date.today)
    payment_method: PaymentMethod
    reference_number: Optional[str] = Field(default=None)
    recorded_by_id: int = Field(foreign_key="team.id", index=True)
    receipt_number: str = Field(unique=True, index=True)

    student: Optional["Student"] = Relationship()
    recorded_by: Optional["Team"] = Relationship()
    allocations: List["PaymentAllocation"] = Relationship(back_populates="payment")
