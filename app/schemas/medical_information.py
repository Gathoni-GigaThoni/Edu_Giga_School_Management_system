from pydantic import BaseModel, ConfigDict
from typing import Optional


class MedicalInformationCreate(BaseModel):
    allergies: Optional[str] = None
    allergies_document: Optional[str] = None
    chronic_symptoms: Optional[str] = None
    chronic_document: Optional[str] = None
    vaccination_document: Optional[str] = None


class MedicalInformationRead(BaseModel):
    id: int
    student_id: int
    allergies: Optional[str] = None
    allergies_document: Optional[str] = None
    chronic_symptoms: Optional[str] = None
    chronic_document: Optional[str] = None
    vaccination_document: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
