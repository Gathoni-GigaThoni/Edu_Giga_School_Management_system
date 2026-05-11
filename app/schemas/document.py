from pydantic import BaseModel, ConfigDict
from datetime import date
from app.models.enums import DocumentCategory


class DocumentCreate(BaseModel):
    student_id: int
    category: DocumentCategory
    file_path: str
    file_name: str


class DocumentRead(BaseModel):
    id: int
    student_id: int
    category: DocumentCategory
    file_path: str
    file_name: str
    upload_date: date

    model_config = ConfigDict(from_attributes=True)
