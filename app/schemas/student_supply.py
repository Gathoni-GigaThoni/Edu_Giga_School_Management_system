# app/schemas/student_supply.py

from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from typing import Optional

class StudentSupplyBase(BaseModel):
    student_id: int
    item_name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(default=1, ge=1)
    term: str = Field(..., min_length=1)
    notes: Optional[str] = None

class StudentSupplyCreate(StudentSupplyBase):
    pass

class StudentSupplyRead(StudentSupplyBase):
    id: int
    date_recorded: date

    model_config = ConfigDict(from_attributes=True)