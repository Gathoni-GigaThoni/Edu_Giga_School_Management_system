from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class AcademicLevelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=1, max_length=2)
    description: Optional[str] = None


class AcademicLevelRead(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
