"""
Finance router — all fee, payment, receipt, reporting and sibling-group endpoints.
"""
from datetime import date as date_type
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from sqlalchemy import func, select as sa_select

from app.database import get_session
from app.dependencies import require_clearance
from app.models.enums import ClearanceLevel
from app.schemas.finance import (
    DailyCollectionReport,
    FeeItemCreate,
    FeeItemRead,
    FeeItemUpdate,
    FeeScheduleCreate,
    FeeScheduleRead,
    OutstandingBalanceResponse,
    PaymentCreate,
    PaymentRead,
    PaymentAllocationRead,
    SiblingGroupCreate,
    SiblingGroupRead,
    StudentFeeRead,
    TriggerTermlyFeesRequest,
    WaiverRequest,
    SurchargeRequest,
)
from app.services.finance import (
    apply_full_year_waiver,
    apply_surcharge,
    generate_receipt,
    get_outstanding_balance,
    post_one_off_fees,
    post_termly_fees,
    post_yearly_fees,
    record_payment,
)

router = APIRouter(prefix="/finance", tags=["Finance"])


# ── Fee-posting triggers ──────────────────────────────────────────────────────

@router.post("/trigger-termly-fees")
def trigger_termly_fees(
    body: TriggerTermlyFeesRequest,
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    try:
        result = post_termly_fees(body.term_id, session)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/trigger-yearly-fees")
def trigger_yearly_fees(
    body: TriggerTermlyFeesRequest,
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    try:
        result = post_yearly_fees(body.term_id, session)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/trigger-oneoff-fees/{student_id}")
def trigger_oneoff_fees(
    student_id: int,
    term_id: int = Query(...),
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    try:
        result = post_one_off_fees(student_id, term_id, session)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ── Payments ──────────────────────────────────────────────────────────────────

@router.post("/payments", response_model=PaymentRead)
def create_payment(
    body: PaymentCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    try:
        payment = record_payment(
            student_id=body.student_id,
            amount=body.amount,
            payment_method=body.payment_method,
            reference_number=body.reference_number,
            payment_date=body.payment_date,
            allocations_in=body.allocations,
            recorded_by_id=body.recorded_by_id,
            session=session,
        )
    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Payment recording failed: {exc}")

    from app.models.student import Student
    from app.models.payment_allocation import PaymentAllocation

    student = session.get(Student, payment.student_id)
    allocations = session.exec(
        select(PaymentAllocation).where(PaymentAllocation.payment_id == payment.id)
    ).all()

    alloc_reads = [
        PaymentAllocationRead(
            id=a.id,
            payment_id=a.payment_id,
            student_fee_id=a.student_fee_id,
            amount_allocated=a.amount_allocated,
        )
        for a in allocations
    ]

    return PaymentRead(
        id=payment.id,
        student_id=payment.student_id,
        student_name=(
            f"{student.first_name} {student.last_name}" if student else None
        ),
        amount=payment.amount,
        payment_date=payment.payment_date,
        payment_method=payment.payment_method,
        reference_number=payment.reference_number,
        recorded_by_id=payment.recorded_by_id,
        receipt_number=payment.receipt_number,
        allocations=alloc_reads,
    )


@router.get("/payments/student/{student_id}", response_model=List[PaymentRead])
def list_payments_for_student(
    student_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_3)),
):
    from app.models.payment import Payment
    from app.models.payment_allocation import PaymentAllocation
    from app.models.student import Student

    payments = session.exec(
        select(Payment).where(Payment.student_id == student_id).order_by(Payment.payment_date.desc())
    ).all()

    result = []
    for pmt in payments:
        student = session.get(Student, pmt.student_id)
        allocations = session.exec(
            select(PaymentAllocation).where(PaymentAllocation.payment_id == pmt.id)
        ).all()
        alloc_reads = [
            PaymentAllocationRead(
                id=a.id,
                payment_id=a.payment_id,
                student_fee_id=a.student_fee_id,
                amount_allocated=a.amount_allocated,
            )
            for a in allocations
        ]
        result.append(
            PaymentRead(
                id=pmt.id,
                student_id=pmt.student_id,
                student_name=(
                    f"{student.first_name} {student.last_name}" if student else None
                ),
                amount=pmt.amount,
                payment_date=pmt.payment_date,
                payment_method=pmt.payment_method,
                reference_number=pmt.reference_number,
                recorded_by_id=pmt.recorded_by_id,
                receipt_number=pmt.receipt_number,
                allocations=alloc_reads,
            )
        )
    return result


# ── Balance & Receipt ─────────────────────────────────────────────────────────

@router.get("/balance/{student_id}", response_model=OutstandingBalanceResponse)
def outstanding_balance(
    student_id: int,
    term_id: int = Query(...),
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_3)),
):
    data = get_outstanding_balance(student_id, term_id, session)
    return OutstandingBalanceResponse(
        student_id=student_id,
        term_id=term_id,
        **data,
    )


@router.get("/receipt/{payment_id}")
def download_receipt(
    payment_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_3)),
):
    import os
    from app.models.payment import Payment

    payment = session.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Build expected path
    year = payment.payment_date.year
    from app.services import finance as finance_svc

    receipts_dir = os.path.join(
        os.path.dirname(finance_svc.__file__), "..", "..", "receipts", str(year)
    )
    pdf_path = os.path.join(receipts_dir, f"{payment.receipt_number}.pdf")

    if not os.path.exists(pdf_path):
        try:
            pdf_path = generate_receipt(payment_id, session)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Receipt generation failed: {exc}")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{payment.receipt_number}.pdf",
    )


# ── is_reported_back ──────────────────────────────────────────────────────────

@router.patch("/set-reported-back/{student_id}")
def set_reported_back(
    student_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_3)),
):
    from app.models.student import Student

    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.is_reported_back = True
    session.add(student)
    session.commit()
    session.refresh(student)
    return {"student_id": student_id, "is_reported_back": student.is_reported_back}


# ── Waivers & Surcharges ──────────────────────────────────────────────────────

@router.post("/apply-full-year-waiver/{student_id}")
def apply_waiver(
    student_id: int,
    academic_year_id: int = Query(...),
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    try:
        result = apply_full_year_waiver(student_id, academic_year_id, session)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/apply-surcharge")
def run_surcharge(
    body: SurchargeRequest,
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    try:
        result = apply_surcharge(body.term_id, session)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ── Reports ───────────────────────────────────────────────────────────────────

@router.get("/reports/daily-collections", response_model=DailyCollectionReport)
def report_daily_collections(
    date: date_type = Query(...),
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    from app.models.payment import Payment

    payments = session.exec(
        select(Payment).where(Payment.payment_date == date)
    ).all()

    total = sum(p.amount for p in payments)
    by_method: dict = {}
    for pmt in payments:
        key = pmt.payment_method.value
        by_method[key] = by_method.get(key, Decimal("0")) + pmt.amount

    return DailyCollectionReport(
        date=date,
        total_collected=total,
        payment_count=len(payments),
        by_method=by_method,
    )


@router.get("/reports/outstanding-by-class")
def report_outstanding_by_class(
    term_id: int = Query(...),
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    from app.models.student import Student
    from app.models.class_ import SchoolClass
    from app.models.student_fee import StudentFee
    from app.models.payment_allocation import PaymentAllocation

    classes = session.exec(select(SchoolClass)).all()
    result = []

    for cls in classes:
        students = session.exec(
            select(Student).where(Student.class_id == cls.id, Student.is_active == True)
        ).all()

        total_charged = Decimal("0")
        total_paid = Decimal("0")
        for student in students:
            balance_data = get_outstanding_balance(student.id, term_id, session)
            total_charged += balance_data["total_charged"]
            total_paid += balance_data["total_paid"]

        result.append(
            {
                "class_id": cls.id,
                "class_name": cls.name,
                "total_charged": total_charged,
                "total_paid": total_paid,
                "balance_due": total_charged - total_paid,
                "student_count": len(students),
            }
        )

    return result


@router.get("/reports/debtors")
def report_debtors(
    term_id: int = Query(...),
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    from app.models.student import Student

    students = session.exec(select(Student).where(Student.is_active == True)).all()
    debtors = []

    for student in students:
        balance_data = get_outstanding_balance(student.id, term_id, session)
        if balance_data["balance_due"] > 0:
            debtors.append(
                {
                    "student_id": student.id,
                    "student_code": student.student_id,
                    "student_name": f"{student.first_name} {student.last_name}",
                    "class_id": student.class_id,
                    "total_charged": balance_data["total_charged"],
                    "total_paid": balance_data["total_paid"],
                    "balance_due": balance_data["balance_due"],
                }
            )

    debtors.sort(key=lambda x: x["balance_due"], reverse=True)
    return debtors


@router.get("/reports/income-summary")
def report_income_summary(
    term_id: int = Query(...),
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    from app.models.payment import Payment
    from app.models.payment_allocation import PaymentAllocation
    from app.models.student_fee import StudentFee
    from app.models.fee_item import FeeItem

    # Total collected this term via allocations on term-level fees
    total_collected = session.execute(
        sa_select(
            func.coalesce(func.sum(PaymentAllocation.amount_allocated), 0)
        )
        .join(StudentFee, PaymentAllocation.student_fee_id == StudentFee.id)
        .where(StudentFee.term_id == term_id)
    ).scalar()

    # Total charged
    total_charged = session.execute(
        sa_select(
            func.coalesce(func.sum(StudentFee.amount), 0)
        ).where(StudentFee.term_id == term_id)
    ).scalar()

    # Breakdown by fee item
    fee_items = session.exec(select(FeeItem)).all()
    breakdown = []
    for item in fee_items:
        charged = session.execute(
            sa_select(
                func.coalesce(func.sum(StudentFee.amount), 0)
            ).where(StudentFee.term_id == term_id, StudentFee.fee_item_id == item.id)
        ).scalar()
        collected = session.execute(
            sa_select(
                func.coalesce(func.sum(PaymentAllocation.amount_allocated), 0)
            )
            .join(StudentFee, PaymentAllocation.student_fee_id == StudentFee.id)
            .where(StudentFee.term_id == term_id, StudentFee.fee_item_id == item.id)
        ).scalar()
        if Decimal(str(charged)) > 0:
            breakdown.append(
                {
                    "fee_item_id": item.id,
                    "fee_item_name": item.name,
                    "category": item.category.value,
                    "total_charged": Decimal(str(charged)),
                    "total_collected": Decimal(str(collected)),
                    "outstanding": Decimal(str(charged)) - Decimal(str(collected)),
                }
            )

    return {
        "term_id": term_id,
        "total_charged": Decimal(str(total_charged)),
        "total_collected": Decimal(str(total_collected)),
        "total_outstanding": Decimal(str(total_charged)) - Decimal(str(total_collected)),
        "breakdown_by_fee_item": breakdown,
    }


# ── Fee Items CRUD ────────────────────────────────────────────────────────────

@router.get("/fee-items", response_model=List[FeeItemRead])
def list_fee_items(
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_3)),
):
    from app.models.fee_item import FeeItem

    return session.exec(select(FeeItem)).all()


@router.post("/fee-items", response_model=FeeItemRead)
def create_fee_item(
    body: FeeItemCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    from app.models.fee_item import FeeItem

    item = FeeItem(**body.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


# ── Fee Schedules CRUD ────────────────────────────────────────────────────────

@router.get("/fee-schedules", response_model=List[FeeScheduleRead])
def list_fee_schedules(
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_3)),
):
    from app.models.fee_schedule import FeeSchedule

    return session.exec(select(FeeSchedule)).all()


@router.post("/fee-schedules", response_model=FeeScheduleRead)
def create_fee_schedule(
    body: FeeScheduleCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    from app.models.fee_schedule import FeeSchedule

    schedule = FeeSchedule(**body.model_dump())
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return schedule


# ── Student Fees ──────────────────────────────────────────────────────────────

@router.get("/student-fees/{student_id}", response_model=List[StudentFeeRead])
def list_student_fees(
    student_id: int,
    term_id: Optional[int] = Query(default=None),
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_3)),
):
    from app.models.student_fee import StudentFee
    from app.models.payment_allocation import PaymentAllocation

    query = select(StudentFee).where(StudentFee.student_id == student_id)
    if term_id is not None:
        query = query.where(StudentFee.term_id == term_id)

    fees = session.exec(query).all()

    result = []
    for fee in fees:
        already_paid = session.execute(
            sa_select(
                func.coalesce(func.sum(PaymentAllocation.amount_allocated), 0)
            ).where(PaymentAllocation.student_fee_id == fee.id)
        ).scalar()
        balance = fee.amount - Decimal(str(already_paid))
        result.append(
            StudentFeeRead(
                id=fee.id,
                student_id=fee.student_id,
                fee_item_id=fee.fee_item_id,
                term_id=fee.term_id,
                academic_year_id=fee.academic_year_id,
                amount=fee.amount,
                is_paid=fee.is_paid,
                date_charged=fee.date_charged,
                date_paid=fee.date_paid,
                source_ref=fee.source_ref,
                balance_due=balance,
            )
        )
    return result


# ── Sibling Groups ────────────────────────────────────────────────────────────

@router.post("/sibling-groups", response_model=SiblingGroupRead)
def create_sibling_group(
    body: SiblingGroupCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    from app.models.sibling_group import SiblingGroup

    group = SiblingGroup(name=body.name)
    session.add(group)
    session.commit()
    session.refresh(group)
    return SiblingGroupRead(
        id=group.id,
        name=group.name,
        student_ids=[s.id for s in group.students],
    )


@router.get("/sibling-groups/{group_id}", response_model=SiblingGroupRead)
def get_sibling_group(
    group_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    from app.models.sibling_group import SiblingGroup

    group = session.get(SiblingGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Sibling group not found")
    return SiblingGroupRead(
        id=group.id,
        name=group.name,
        student_ids=[s.id for s in group.students],
    )


@router.post("/sibling-groups/{group_id}/add-student/{student_id}")
def add_student_to_sibling_group(
    group_id: int,
    student_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    from app.models.sibling_group import SiblingGroup
    from app.models.student import Student

    group = session.get(SiblingGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Sibling group not found")

    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.sibling_group_id = group_id
    session.add(student)
    session.commit()
    session.refresh(group)

    return {
        "group_id": group_id,
        "student_id": student_id,
        "message": f"Student {student_id} added to sibling group {group_id}",
        "group_members": [s.id for s in group.students],
    }
