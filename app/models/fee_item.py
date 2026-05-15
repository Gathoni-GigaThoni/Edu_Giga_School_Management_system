from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from app.models.enums import FeeCategory

if TYPE_CHECKING:
    from app.models.fee_schedule import FeeSchedule
    from app.models.student_fee import StudentFee


class FeeItem(SQLModel, table=True):
    __tablename__ = "fee_item"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    category: FeeCategory = Field(index=True)
    default_amount: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    is_active: bool = Field(default=True)

    fee_schedules: List["FeeSchedule"] = Relationship(back_populates="fee_item")
    student_fees: List["StudentFee"] = Relationship(back_populates="fee_item")
