from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional, TYPE_CHECKING
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.payment import Payment
    from app.models.student_fee import StudentFee


class PaymentAllocation(SQLModel, table=True):
    __tablename__ = "payment_allocation"

    id: Optional[int] = Field(default=None, primary_key=True)
    payment_id: int = Field(foreign_key="payment.id", index=True)
    student_fee_id: int = Field(foreign_key="student_fee.id", index=True)
    amount_allocated: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))

    payment: Optional["Payment"] = Relationship(back_populates="allocations")
    student_fee: Optional["StudentFee"] = Relationship(back_populates="allocations")
