from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: str = Field(..., min_length=1)
    applicable_level: str = Field(..., min_length=1)


class SkillCreate(SkillBase):
    pass


class SkillRead(SkillBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
