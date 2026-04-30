from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.enums import InfractionSeverity


class DisciplinaryLogBase(BaseModel):
    student_id: int
    description: str
    action_taken: Optional[str] = None
    severity: InfractionSeverity


class DisciplinaryLogCreate(DisciplinaryLogBase):
    pass


class DisciplinaryLogRead(DisciplinaryLogBase):
    id: int
    reported_by_id: int
    incident_date: datetime
    is_resolved: bool
    resolution_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DisciplinaryLogUpdate(BaseModel):
    is_resolved: bool
    resolution_notes: Optional[str] = None
