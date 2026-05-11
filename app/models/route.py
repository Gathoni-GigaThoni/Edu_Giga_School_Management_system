"""
Route represents a transport route the school operates.
Pricing is split into one-way morning, one-way evening, two-way, and daily options.
StudentRoute records track each student's individual transport arrangement.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.student_route import StudentRoute


class Route(SQLModel, table=True):
    __tablename__ = "route"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    one_way_morning_price: float
    one_way_evening_price: float
    two_way_price: float
    daily_rate: float

    student_routes: List["StudentRoute"] = Relationship(back_populates="route")
