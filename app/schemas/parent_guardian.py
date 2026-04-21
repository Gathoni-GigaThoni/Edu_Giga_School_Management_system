from pydantic import BaseModel
from typing import Optional

class ParentGuardianBase(BaseModel):
    student_id: int
    full_name: str
    relationship: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    is_emergency_contact: bool = True

class ParentGuardianCreate(ParentGuardianBase):
    pass

class ParentGuardianRead(ParentGuardianBase):
    id: int

    class Config:
        from_attributes = True