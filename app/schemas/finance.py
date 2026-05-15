from pydantic import BaseModel, ConfigDict, model_validator
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import date
from app.models.enums import FeeCategory, PaymentMethod


# ── FeeItem Schemas ───────────────────────────────────────────────────────────

class FeeItemCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    category: FeeCategory
    default_amount: Decimal
    is_active: bool = True


class FeeItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: FeeCategory
    default_amount: Decimal
    is_active: bool


class FeeItemUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    category: Optional[FeeCategory] = None
    default_amount: Optional[Decimal] = None
    is_active: Optional[bool] = None


# ── FeeSchedule Schemas ───────────────────────────────────────────────────────

class FeeScheduleCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fee_item_id: int
    academic_level_id: Optional[int] = None
    class_id: Optional[int] = None
    student_id: Optional[int] = None
    amount: Decimal
    term_id: Optional[int] = None

    @model_validator(mode="after")
    def check_exactly_one_scope(self) -> "FeeScheduleCreate":
        scope_count = sum([
            self.academic_level_id is not None,
            self.class_id is not None,
            self.student_id is not None,
        ])
        if scope_count != 1:
            raise ValueError(
                "Exactly one of academic_level_id, class_id, or student_id must be provided."
            )
        return self


class FeeScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fee_item_id: int
    academic_level_id: Optional[int]
    class_id: Optional[int]
    student_id: Optional[int]
    amount: Decimal
    term_id: Optional[int]


# ── StudentFee Schemas ────────────────────────────────────────────────────────

class StudentFeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    fee_item_id: int
    term_id: Optional[int]
    academic_year_id: int
    amount: Decimal
    is_paid: bool
    date_charged: date
    date_paid: Optional[date]
    source_ref: Optional[str]
    balance_due: Optional[Decimal] = None


# ── PaymentAllocation Schemas ─────────────────────────────────────────────────

class PaymentAllocationIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_fee_id: int
    amount_allocated: Decimal


class PaymentAllocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payment_id: int
    student_fee_id: int
    amount_allocated: Decimal


# ── Payment Schemas ───────────────────────────────────────────────────────────

class PaymentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    amount: Decimal
    payment_date: date
    payment_method: PaymentMethod
    reference_number: Optional[str] = None
    recorded_by_id: int
    allocations: List[PaymentAllocationIn]


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    student_name: Optional[str] = None
    amount: Decimal
    payment_date: date
    payment_method: PaymentMethod
    reference_number: Optional[str]
    recorded_by_id: int
    receipt_number: str
    allocations: List[PaymentAllocationRead] = []


# ── SiblingGroup Schemas ──────────────────────────────────────────────────────

class SiblingGroupCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class SiblingGroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    student_ids: List[int] = []


# ── Trigger / Request Schemas ─────────────────────────────────────────────────

class TriggerTermlyFeesRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    term_id: int


class WaiverRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    academic_year_id: int
    note: Optional[str] = None


class SurchargeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    term_id: int


# ── Report Schemas ────────────────────────────────────────────────────────────

class OutstandingBalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: int
    term_id: int
    total_charged: Decimal
    total_paid: Decimal
    balance_due: Decimal


class DailyCollectionReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    total_collected: Decimal
    payment_count: int
    by_method: Dict[str, Decimal]
