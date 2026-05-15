from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric, CheckConstraint
from typing import Optional, TYPE_CHECKING
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.fee_item import FeeItem
    from app.models.academic_level import AcademicLevel
    from app.models.class_ import SchoolClass
    from app.models.student import Student
    from app.models.term import Term


class FeeSchedule(SQLModel, table=True):
    __tablename__ = "fee_schedule"

    __table_args__ = (
        CheckConstraint(
            "(CASE WHEN academic_level_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN class_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN student_id IS NOT NULL THEN 1 ELSE 0 END) = 1",
            name="chk_fee_schedule_scope"
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    fee_item_id: int = Field(foreign_key="fee_item.id", index=True)
    academic_level_id: Optional[int] = Field(default=None, foreign_key="academic_level.id", index=True)
    class_id: Optional[int] = Field(default=None, foreign_key="school_class.id", index=True)
    student_id: Optional[int] = Field(default=None, foreign_key="student.id", index=True)
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    term_id: Optional[int] = Field(default=None, foreign_key="term.id", index=True)

    fee_item: Optional["FeeItem"] = Relationship(back_populates="fee_schedules")
    academic_level: Optional["AcademicLevel"] = Relationship()
    school_class: Optional["SchoolClass"] = Relationship()
    student: Optional["Student"] = Relationship()
    term: Optional["Term"] = Relationship()
