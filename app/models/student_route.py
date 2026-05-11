"""
StudentRoute joins a Student to a Route with direction and pricing details.
A student may have multiple records (history), but only one should be active at a time.
The service layer enforces the single-active-route constraint on assignment.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date
from app.models.enums import TransportDirection

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.route import Route


class StudentRoute(SQLModel, table=True):
    __tablename__ = "student_route"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    route_id: int = Field(foreign_key="route.id", index=True)
    direction: TransportDirection
    use_daily_rate: bool = Field(default=False)
    active: bool = Field(default=True)
    start_date: date = Field(default_factory=date.today)

    student: Optional["Student"] = Relationship(back_populates="student_routes")
    route: Optional["Route"] = Relationship(back_populates="student_routes")
