from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from app.models.enums import ParentRelationship


class ParentInfoCreate(BaseModel):
    full_name: str = Field(..., min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None
    relationship: ParentRelationship
    is_primary: bool = False
    id_document: Optional[str] = None
    pickup_authorized: bool = True


class ParentInfoRead(BaseModel):
    id: int
    student_id: int
    full_name: str
    email: str
    phone: str
    relationship: ParentRelationship
    is_primary: bool
    id_document: Optional[str] = None
    pickup_authorized: bool

    model_config = ConfigDict(from_attributes=True)
