"""
Finance service layer.
All model imports are inside functions to avoid circular import issues at module load time.
"""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import Optional
from sqlmodel import Session, select
from sqlalchemy import func, or_


def generate_receipt_number(session: Session, year: int) -> str:
    """Format: RCPT-{YYYY}-{SEQ:05d}"""
    from app.models.payment import Payment

    prefix = f"RCPT-{year}-"
    last = session.exec(
        select(Payment.receipt_number)
        .where(Payment.receipt_number.like(f"{prefix}%"))
        .order_by(Payment.receipt_number.desc())
    ).first()
    seq = int(last.split("-")[2]) + 1 if last else 1
    return f"{prefix}{seq:05d}"


def _get_fee_item_by_name(name: str, session: Session) -> Optional["object"]:
    from app.models.fee_item import FeeItem

    return session.exec(
        select(FeeItem).where(FeeItem.name == name, FeeItem.is_active == True)
    ).first()


def _get_route_transport_amount(route, student_route) -> Decimal:
    from app.models.enums import TransportDirection

    if student_route.use_daily_rate:
        return Decimal(str(route.daily_rate))
    d = student_route.direction
    if d == TransportDirection.ONE_WAY_MORNING:
        return Decimal(str(route.one_way_morning_price))
    elif d == TransportDirection.ONE_WAY_EVENING:
        return Decimal(str(route.one_way_evening_price))
    return Decimal(str(route.two_way_price))


def calculate_sibling_discount(student, session: Session) -> Decimal:
    """Returns discount percentage (0, 5, or 10) as a Decimal."""
    if not student.sibling_group_id:
        return Decimal("0")

    from app.models.student import Student

    siblings = session.exec(
        select(Student)
        .where(
            Student.sibling_group_id == student.sibling_group_id,
            Student.is_active == True,
        )
        .order_by(Student.date_of_birth.asc())  # oldest first
    ).all()

    if len(siblings) <= 1:
        return Decimal("0")

    for idx, sib in enumerate(siblings):
        if sib.id == student.id:
            if idx == 0:
                return Decimal("0")
            elif idx == 1:
                return Decimal("5")
            else:
                return Decimal("10")

    return Decimal("0")


def post_termly_fees(term_id: int, session: Session) -> dict:
    from app.models.term import Term
    from app.models.student import Student
    from app.models.fee_item import FeeItem
    from app.models.fee_schedule import FeeSchedule
    from app.models.student_fee import StudentFee
    from app.models.student_route import StudentRoute
    from app.models.route import Route
    from app.models.club import Club, StudentClub
    from app.models.enums import FeeCategory

    term = session.get(Term, term_id)
    if not term:
        raise ValueError(f"Term {term_id} not found")

    students = session.exec(
        select(Student).where(Student.is_active == True, Student.is_reported_back == True)
    ).all()

    fees_posted = 0
    students_processed = 0

    for student in students:
        # Schedule-based TERMLY fees
        scope_conds = [FeeSchedule.student_id == student.id]
        if student.academic_level_id is not None:
            scope_conds.append(FeeSchedule.academic_level_id == student.academic_level_id)
        if student.class_id is not None:
            scope_conds.append(FeeSchedule.class_id == student.class_id)

        schedules = session.exec(
            select(FeeSchedule).join(FeeItem, FeeSchedule.fee_item_id == FeeItem.id)
            .where(
                FeeItem.category == FeeCategory.TERMLY,
                FeeItem.is_active == True,
                or_(*scope_conds),
                or_(FeeSchedule.term_id == None, FeeSchedule.term_id == term_id),
            )
        ).all()

        for schedule in schedules:
            amount = schedule.amount
            # Apply sibling discount to tuition fees
            fee_item = session.get(FeeItem, schedule.fee_item_id)
            if fee_item and "tuition" in fee_item.name.lower():
                discount_pct = calculate_sibling_discount(student, session)
                if discount_pct > 0:
                    amount = (amount * (1 - discount_pct / 100)).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )

            existing = session.exec(
                select(StudentFee).where(
                    StudentFee.student_id == student.id,
                    StudentFee.fee_item_id == schedule.fee_item_id,
                    StudentFee.term_id == term_id,
                    StudentFee.source_ref == None,
                )
            ).first()
            if not existing:
                session.add(
                    StudentFee(
                        student_id=student.id,
                        fee_item_id=schedule.fee_item_id,
                        term_id=term_id,
                        academic_year_id=term.academic_year_id,
                        amount=amount,
                    )
                )
                fees_posted += 1

        # Transport fees
        active_route = session.exec(
            select(StudentRoute).where(
                StudentRoute.student_id == student.id,
                StudentRoute.active == True,
            )
        ).first()
        if active_route:
            route = session.get(Route, active_route.route_id)
            if route:
                transport_amount = _get_route_transport_amount(route, active_route)
                transport_item = _get_fee_item_by_name("Transport Fee", session)
                if transport_item:
                    source = f"route:{route.id}"
                    existing = session.exec(
                        select(StudentFee).where(
                            StudentFee.student_id == student.id,
                            StudentFee.fee_item_id == transport_item.id,
                            StudentFee.term_id == term_id,
                            StudentFee.source_ref == source,
                        )
                    ).first()
                    if not existing:
                        session.add(
                            StudentFee(
                                student_id=student.id,
                                fee_item_id=transport_item.id,
                                term_id=term_id,
                                academic_year_id=term.academic_year_id,
                                amount=transport_amount,
                                source_ref=source,
                            )
                        )
                        fees_posted += 1

        # Club fees
        active_sc = session.exec(
            select(StudentClub).where(
                StudentClub.student_id == student.id,
                StudentClub.is_active == True,
            )
        ).all()
        for sc in active_sc:
            club = session.get(Club, sc.club_id)
            if club and club.fee_amount and club.fee_amount > 0:
                club_item = _get_fee_item_by_name("Club Fee", session)
                if club_item:
                    source = f"club:{club.id}"
                    existing = session.exec(
                        select(StudentFee).where(
                            StudentFee.student_id == student.id,
                            StudentFee.fee_item_id == club_item.id,
                            StudentFee.term_id == term_id,
                            StudentFee.source_ref == source,
                        )
                    ).first()
                    if not existing:
                        session.add(
                            StudentFee(
                                student_id=student.id,
                                fee_item_id=club_item.id,
                                term_id=term_id,
                                academic_year_id=term.academic_year_id,
                                amount=Decimal(str(club.fee_amount)),
                                source_ref=source,
                            )
                        )
                        fees_posted += 1

        student.is_reported_back = False
        session.add(student)
        students_processed += 1

    session.commit()
    return {"students_processed": students_processed, "fees_posted": fees_posted}


def post_yearly_fees(term_id: int, session: Session) -> dict:
    """Posts YEARLY fees. Only runs if the term is Term 1 of its academic year."""
    from app.models.term import Term
    from app.models.student import Student
    from app.models.fee_item import FeeItem
    from app.models.fee_schedule import FeeSchedule
    from app.models.student_fee import StudentFee
    from app.models.enums import FeeCategory, TermName

    term = session.get(Term, term_id)
    if not term:
        raise ValueError(f"Term {term_id} not found")
    if term.name != TermName.TERM_1:
        return {"message": "Yearly fees only posted in Term 1", "fees_posted": 0}

    students = session.exec(select(Student).where(Student.is_active == True)).all()
    fees_posted = 0

    for student in students:
        scope_conds = [FeeSchedule.student_id == student.id]
        if student.academic_level_id is not None:
            scope_conds.append(FeeSchedule.academic_level_id == student.academic_level_id)
        if student.class_id is not None:
            scope_conds.append(FeeSchedule.class_id == student.class_id)

        schedules = session.exec(
            select(FeeSchedule).join(FeeItem, FeeSchedule.fee_item_id == FeeItem.id)
            .where(
                FeeItem.category == FeeCategory.YEARLY,
                FeeItem.is_active == True,
                or_(*scope_conds),
            )
        ).all()

        for schedule in schedules:
            existing = session.exec(
                select(StudentFee).where(
                    StudentFee.student_id == student.id,
                    StudentFee.fee_item_id == schedule.fee_item_id,
                    StudentFee.academic_year_id == term.academic_year_id,
                    StudentFee.term_id == None,
                )
            ).first()
            if not existing:
                session.add(
                    StudentFee(
                        student_id=student.id,
                        fee_item_id=schedule.fee_item_id,
                        term_id=None,
                        academic_year_id=term.academic_year_id,
                        amount=schedule.amount,
                    )
                )
                fees_posted += 1

    session.commit()
    return {"students_processed": len(students), "fees_posted": fees_posted}


def post_one_off_fees(student_id: int, term_id: int, session: Session) -> dict:
    from app.models.term import Term
    from app.models.student import Student
    from app.models.fee_item import FeeItem
    from app.models.fee_schedule import FeeSchedule
    from app.models.student_fee import StudentFee
    from app.models.enums import FeeCategory

    student = session.get(Student, student_id)
    if not student:
        raise ValueError(f"Student {student_id} not found")
    term = session.get(Term, term_id)
    if not term:
        raise ValueError(f"Term {term_id} not found")

    scope_conds = [FeeSchedule.student_id == student.id]
    if student.academic_level_id is not None:
        scope_conds.append(FeeSchedule.academic_level_id == student.academic_level_id)
    if student.class_id is not None:
        scope_conds.append(FeeSchedule.class_id == student.class_id)

    schedules = session.exec(
        select(FeeSchedule).join(FeeItem, FeeSchedule.fee_item_id == FeeItem.id)
        .where(
            FeeItem.category == FeeCategory.ONE_OFF,
            FeeItem.is_active == True,
            or_(*scope_conds),
        )
    ).all()

    fees_posted = 0
    for schedule in schedules:
        # ONE_OFF: check if ever charged before (regardless of year/term)
        existing = session.exec(
            select(StudentFee).where(
                StudentFee.student_id == student.id,
                StudentFee.fee_item_id == schedule.fee_item_id,
            )
        ).first()
        if not existing:
            session.add(
                StudentFee(
                    student_id=student.id,
                    fee_item_id=schedule.fee_item_id,
                    term_id=None,
                    academic_year_id=term.academic_year_id,
                    amount=schedule.amount,
                )
            )
            fees_posted += 1

    session.commit()
    return {"fees_posted": fees_posted}


def record_payment(
    student_id: int,
    amount: Decimal,
    payment_method,
    reference_number: Optional[str],
    payment_date: date,
    allocations_in: list,
    recorded_by_id: int,
    session: Session,
):
    from sqlalchemy import select as sa_select
    from app.models.payment import Payment
    from app.models.payment_allocation import PaymentAllocation
    from app.models.student_fee import StudentFee

    receipt_number = generate_receipt_number(session, payment_date.year)

    payment = Payment(
        student_id=student_id,
        amount=amount,
        payment_date=payment_date,
        payment_method=payment_method,
        reference_number=reference_number,
        recorded_by_id=recorded_by_id,
        receipt_number=receipt_number,
    )
    session.add(payment)
    session.flush()  # get payment.id

    for alloc in allocations_in:
        fee = session.get(StudentFee, alloc.student_fee_id)
        if not fee:
            raise ValueError(f"StudentFee {alloc.student_fee_id} not found")

        # Calculate remaining balance
        already_allocated = session.execute(
            sa_select(func.sum(PaymentAllocation.amount_allocated))
            .where(PaymentAllocation.student_fee_id == fee.id)
        ).scalar() or Decimal("0")

        remaining = fee.amount - Decimal(str(already_allocated))
        if alloc.amount_allocated > remaining:
            raise ValueError(
                f"Allocated amount {alloc.amount_allocated} exceeds remaining balance "
                f"{remaining} on fee {fee.id}"
            )

        pa = PaymentAllocation(
            payment_id=payment.id,
            student_fee_id=fee.id,
            amount_allocated=alloc.amount_allocated,
        )
        session.add(pa)

        # Mark fee as paid if fully covered
        new_allocated = Decimal(str(already_allocated)) + alloc.amount_allocated
        if new_allocated >= fee.amount:
            fee.is_paid = True
            fee.date_paid = payment_date
            session.add(fee)

    session.commit()
    session.refresh(payment)
    return payment


def get_outstanding_balance(student_id: int, term_id: int, session: Session) -> dict:
    from sqlalchemy import select as sa_select
    from app.models.student_fee import StudentFee
    from app.models.payment_allocation import PaymentAllocation

    total_charged = session.execute(
        sa_select(func.coalesce(func.sum(StudentFee.amount), 0))
        .where(StudentFee.student_id == student_id, StudentFee.term_id == term_id)
    ).scalar()

    total_paid = session.execute(
        sa_select(func.coalesce(func.sum(PaymentAllocation.amount_allocated), 0))
        .join(StudentFee, PaymentAllocation.student_fee_id == StudentFee.id)
        .where(StudentFee.student_id == student_id, StudentFee.term_id == term_id)
    ).scalar()

    charged = Decimal(str(total_charged))
    paid = Decimal(str(total_paid))
    return {"total_charged": charged, "total_paid": paid, "balance_due": charged - paid}


def apply_full_year_waiver(student_id: int, academic_year_id: int, session: Session) -> dict:
    """Apply 8% discount on all tuition fees for the academic year."""
    from app.models.student_fee import StudentFee
    from app.models.fee_item import FeeItem

    tuition_fees = session.exec(
        select(StudentFee).join(FeeItem, StudentFee.fee_item_id == FeeItem.id)
        .where(
            StudentFee.student_id == student_id,
            StudentFee.academic_year_id == academic_year_id,
            FeeItem.name.ilike("%tuition%"),
            StudentFee.is_paid == False,
        )
    ).all()

    discount_item = _get_fee_item_by_name("Full Year Waiver", session)
    if not discount_item:
        raise ValueError("'Full Year Waiver' FeeItem not found. Run seed first.")

    total_tuition = sum(f.amount for f in tuition_fees)
    waiver_amount = -(total_tuition * Decimal("0.08")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Check if already applied
    existing = session.exec(
        select(StudentFee).where(
            StudentFee.student_id == student_id,
            StudentFee.fee_item_id == discount_item.id,
            StudentFee.academic_year_id == academic_year_id,
        )
    ).first()
    if existing:
        raise ValueError("Full year waiver already applied for this academic year")

    session.add(
        StudentFee(
            student_id=student_id,
            fee_item_id=discount_item.id,
            term_id=None,
            academic_year_id=academic_year_id,
            amount=waiver_amount,
        )
    )
    session.commit()
    return {"waiver_applied": True, "discount_amount": waiver_amount}


def apply_surcharge(term_id: int, session: Session) -> dict:
    """Apply 3% surcharge on all unpaid fees for the term."""
    from sqlalchemy import select as sa_select
    from app.models.student_fee import StudentFee
    from app.models.payment_allocation import PaymentAllocation
    from app.models.term import Term

    term = session.get(Term, term_id)
    if not term:
        raise ValueError(f"Term {term_id} not found")

    surcharge_item = _get_fee_item_by_name("Late Payment Surcharge", session)
    if not surcharge_item:
        raise ValueError("'Late Payment Surcharge' FeeItem not found. Run seed first.")

    unpaid_fees = session.exec(
        select(StudentFee).where(
            StudentFee.term_id == term_id,
            StudentFee.is_paid == False,
            StudentFee.fee_item_id != surcharge_item.id,
        )
    ).all()

    surcharges_created = 0
    for fee in unpaid_fees:
        # Calculate remaining balance
        paid_on_fee = session.execute(
            sa_select(func.coalesce(func.sum(PaymentAllocation.amount_allocated), 0))
            .where(PaymentAllocation.student_fee_id == fee.id)
        ).scalar()
        balance = fee.amount - Decimal(str(paid_on_fee))
        if balance <= 0:
            continue

        surcharge_amount = (balance * Decimal("0.03")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        # Avoid double-surcharging
        source = f"surcharge_of:{fee.id}"
        existing = session.exec(
            select(StudentFee).where(
                StudentFee.student_id == fee.student_id,
                StudentFee.fee_item_id == surcharge_item.id,
                StudentFee.term_id == term_id,
                StudentFee.source_ref == source,
            )
        ).first()
        if not existing:
            session.add(
                StudentFee(
                    student_id=fee.student_id,
                    fee_item_id=surcharge_item.id,
                    term_id=term_id,
                    academic_year_id=term.academic_year_id,
                    amount=surcharge_amount,
                    source_ref=source,
                )
            )
            surcharges_created += 1

    session.commit()
    return {"surcharges_created": surcharges_created}


def generate_receipt(payment_id: int, session: Session) -> str:
    """Generate PDF receipt using WeasyPrint. Returns file path."""
    import os
    from app.models.payment import Payment
    from app.models.payment_allocation import PaymentAllocation
    from app.models.student_fee import StudentFee
    from app.models.fee_item import FeeItem
    from app.models.student import Student

    payment = session.get(Payment, payment_id)
    if not payment:
        raise ValueError(f"Payment {payment_id} not found")

    student = session.get(Student, payment.student_id)
    allocations = session.exec(
        select(PaymentAllocation).where(PaymentAllocation.payment_id == payment_id)
    ).all()

    line_items = []
    for alloc in allocations:
        fee = session.get(StudentFee, alloc.student_fee_id)
        fee_item = session.get(FeeItem, fee.fee_item_id) if fee else None
        line_items.append(
            {
                "description": fee_item.name if fee_item else "Fee",
                "amount": float(alloc.amount_allocated),
            }
        )

    context = {
        "receipt_number": payment.receipt_number,
        "payment_date": payment.payment_date.strftime("%d %B %Y"),
        "student_name": (
            f"{student.first_name} {student.last_name}" if student else "Unknown"
        ),
        "student_id": student.student_id if student else "",
        "payment_method": payment.payment_method.value,
        "reference_number": payment.reference_number or "—",
        "line_items": line_items,
        "total_paid": float(payment.amount),
        "school_name": "Seven Oak International School",
    }

    # Render HTML template
    from jinja2 import Environment, FileSystemLoader

    template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("receipt.html")
    html_content = template.render(**context)

    # Convert to PDF
    from weasyprint import HTML

    year = payment.payment_date.year
    receipts_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "receipts", str(year)
    )
    os.makedirs(receipts_dir, exist_ok=True)

    pdf_filename = f"{payment.receipt_number}.pdf"
    pdf_path = os.path.join(receipts_dir, pdf_filename)
    HTML(string=html_content).write_pdf(pdf_path)

    # Record in Document table
    from app.models.document import Document
    from app.models.enums import DocumentCategory

    existing_doc = session.exec(
        select(Document).where(Document.file_path == pdf_path)
    ).first()
    if not existing_doc:
        doc = Document(
            student_id=payment.student_id,
            category=DocumentCategory.RECEIPT,
            file_path=pdf_path,
            file_name=pdf_filename,
        )
        session.add(doc)
        session.commit()

    return pdf_path
