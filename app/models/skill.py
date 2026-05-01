from sqlmodel import SQLModel, Field
from typing import Optional


class Skill(SQLModel, table=True):
    __tablename__ = "skill"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    category: str
    applicable_level: str
