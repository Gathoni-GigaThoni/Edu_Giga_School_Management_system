from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import date
from typing import Optional, List

from app.models.enums import ParentRelationship
from app.schemas.parent_info import ParentInfoCreate, ParentInfoRead
from app.schemas.previous_education import PreviousEducationCreate, PreviousEducationRead
from app.schemas.medical_information import MedicalInformationCreate, MedicalInformationRead


class StudentRegisterRequest(BaseModel):
    """Full registration payload including nested parent, medical, and education data."""

    # Core identity
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    gender: Optional[str] = None
    is_active: bool = True
    stream: Optional[str] = Field(default=None, max_length=50)  # e.g. "East"

    # Placement
    academic_level_id: int
    class_id: int
    transport_route_id: Optional[int] = None

    # Nested sections
    previous_education: Optional[PreviousEducationCreate] = None
    medical_info: Optional[MedicalInformationCreate] = None
    parents: List[ParentInfoCreate] = Field(default_factory=list)

    @field_validator("date_of_birth")
    @classmethod
    def dob_must_be_in_past(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError("Date of birth must be in the past")
        age_years = (date.today() - v).days / 365.25
        if age_years < 2 or age_years > 10:
            raise ValueError("Student age must be between 2 and 10 years")
        return v

    @model_validator(mode="after")
    def validate_parents(self) -> "StudentRegisterRequest":
        parents = self.parents
        if not parents:
            raise ValueError("At least one parent or guardian is required")

        primary = [p for p in parents if p.is_primary]
        if len(primary) != 1:
            raise ValueError("Exactly one parent must be marked as primary")

        # Primary parent: all contact fields mandatory
        p = primary[0]
        missing = [f for f, v in [("email", p.email), ("phone", p.phone), ("id_document", p.id_document)] if not v]
        if missing:
            raise ValueError(f"Primary parent is missing: {', '.join(missing)}")

        # Non-primary parents: email, phone, and ID mandatory
        for np in [x for x in parents if not x.is_primary]:
            missing = [f for f, v in [("email", np.email), ("phone", np.phone), ("id_document", np.id_document)] if not v]
            if missing:
                raise ValueError(f"Additional parent '{np.full_name}' is missing: {', '.join(missing)}")

        return self


class StudentRead(BaseModel):
    id: int
    student_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    age_months: Optional[int] = None
    gender: Optional[str] = None
    is_active: bool
    stream: Optional[str] = None
    academic_level_id: Optional[int] = None
    class_id: Optional[int] = None
    transport_route_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class StudentReadFull(StudentRead):
    """Expanded read schema that includes nested relationships."""
    previous_education: Optional[PreviousEducationRead] = None
    medical_info: Optional[MedicalInformationRead] = None
    parents: List[ParentInfoRead] = []
