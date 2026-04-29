from pydantic import BaseModel, ConfigDict
from typing import Optional

class MedicalHistoryBase(BaseModel):
    student_id: int
    allergies: Optional[str] = None
    medications: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None
    notes: Optional[str] = None

class MedicalHistoryCreate(MedicalHistoryBase):
    pass

class MedicalHistoryRead(MedicalHistoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)