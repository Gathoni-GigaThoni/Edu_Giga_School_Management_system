"""
Document is a generic file registry linking uploaded documents to a student.
The category field distinguishes purpose (medical, parent ID, previous education, etc.).
Actual file bytes are managed externally; this table records metadata only.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date
from app.models.enums import DocumentCategory

if TYPE_CHECKING:
    from app.models.student import Student


class Document(SQLModel, table=True):
    __tablename__ = "document"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    category: DocumentCategory
    file_path: str
    file_name: str
    upload_date: date = Field(default_factory=date.today)

    student: Optional["Student"] = Relationship(back_populates="documents")
