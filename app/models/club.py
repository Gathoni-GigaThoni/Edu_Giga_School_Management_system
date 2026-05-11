"""
Club represents an extracurricular activity (e.g. Football, Art, Choir).
StudentClub is the join table implementing the many-to-many between Student and Club.
Each StudentClub record tracks when the student joined and whether they are still active.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from app.models.student import Student


class Club(SQLModel, table=True):
    __tablename__ = "club"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None

    student_clubs: List["StudentClub"] = Relationship(back_populates="club")


class StudentClub(SQLModel, table=True):
    __tablename__ = "student_club"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    club_id: int = Field(foreign_key="club.id", index=True)
    join_date: date = Field(default_factory=date.today)
    is_active: bool = Field(default=True)

    student: Optional["Student"] = Relationship(back_populates="clubs")
    club: Optional["Club"] = Relationship(back_populates="student_clubs")
