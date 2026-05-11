"""
Seed router: creates representative demo data for development / first-run testing.
Includes an academic year (2025-2026), four academic levels, four classes,
two transport routes, two staff members, and one fully-populated sample student.
"""
from datetime import date

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.auth import get_password_hash
from app.models.team import Team
from app.models.academic_level import AcademicLevel
from app.models.academic_year import AcademicYear
from app.models.term import Term
from app.models.class_ import SchoolClass
from app.models.route import Route
from app.models.student import Student
from app.models.student_route import StudentRoute
from app.models.previous_education import PreviousEducation
from app.models.medical_information import MedicalInformation
from app.models.parent_info import ParentInfo
from app.models.attendance import Attendance
from app.models.student_supply import StudentSupply
from app.models.enums import (
    StaffRole, ClearanceLevel, AttendanceStatus,
    TermName, TransportDirection, ParentRelationship,
)
from app.services.student_id_generator import generate_student_id

router = APIRouter(prefix="/seed", tags=["Seed"])


@router.post("/demo")
def seed_demo(session: Session = Depends(get_session)):  # noqa: C901
    # ── Staff ────────────────────────────────────────────────────────────────
    admin = Team(
        first_name="Admin",
        last_name="SevenOak",
        email="admin@sevenoak.edu",
        hashed_password=get_password_hash("admin123"),
        role=StaffRole.SUPER_ADMIN,
        clearance_level=ClearanceLevel.LEVEL_1,
        location="Admin Office",
    )
    session.add(admin)

    teacher = Team(
        first_name="Jane",
        last_name="Doe",
        email="teacher@sevenoak.edu",
        hashed_password=get_password_hash("teacher123"),
        role=StaffRole.TEACHER,
        clearance_level=ClearanceLevel.LEVEL_4,
        location="Maple Class",
    )
    session.add(teacher)
    session.flush()

    # ── Academic Levels ──────────────────────────────────────────────────────
    levels_data = [
        {"name": "Acorn",  "code": "A", "description": "Baby Class"},
        {"name": "Willow", "code": "W", "description": "Playgroup"},
        {"name": "Maple",  "code": "M", "description": "Pre-Primary 1"},
        {"name": "Oak",    "code": "O", "description": "Pre-Primary 2"},
    ]
    levels: dict[str, AcademicLevel] = {}
    for ld in levels_data:
        level = AcademicLevel(**ld)
        session.add(level)
        levels[ld["name"]] = level
    session.flush()

    # ── Academic Year 2025-2026 ──────────────────────────────────────────────
    acad_year = AcademicYear(
        name="2025-2026",
        start_date=date(2025, 9, 1),
        end_date=date(2026, 7, 17),
    )
    session.add(acad_year)
    session.flush()

    terms_data = [
        {"name": TermName.TERM_1, "automatic_start": date(2025, 9, 1),  "automatic_end": date(2025, 12, 12)},
        {"name": TermName.TERM_2, "automatic_start": date(2026, 1, 8),  "automatic_end": date(2026, 4, 3)},
        {"name": TermName.TERM_3, "automatic_start": date(2026, 4, 23), "automatic_end": date(2026, 7, 17)},
    ]
    for td in terms_data:
        session.add(Term(academic_year_id=acad_year.id, **td))

    # ── Classes ──────────────────────────────────────────────────────────────
    classes: dict[str, SchoolClass] = {}
    for level_name, level_obj in levels.items():
        sc = SchoolClass(
            academic_level_id=level_obj.id,
            academic_year_id=acad_year.id,
            name=f"{level_name} 2026",
            tuition_fee=35000.0,
            homeroom_teacher_id=teacher.id if level_name == "Maple" else None,
        )
        session.add(sc)
        classes[level_name] = sc
    session.flush()

    # ── Transport Routes ─────────────────────────────────────────────────────
    westlands_route = Route(
        name="Westlands",
        one_way_morning_price=1500.0,
        one_way_evening_price=1500.0,
        two_way_price=2500.0,
        daily_rate=600.0,
    )
    session.add(westlands_route)

    karen_route = Route(
        name="Karen",
        one_way_morning_price=2000.0,
        one_way_evening_price=2000.0,
        two_way_price=3500.0,
        daily_rate=800.0,
    )
    session.add(karen_route)
    session.flush()

    # ── Sample Student (Maple class, East stream) ────────────────────────────
    maple_class = classes["Maple"]
    maple_level = levels["Maple"]

    student_id = generate_student_id(
        session,
        level_code=maple_level.code,
        stream="East",
        class_id=maple_class.id,
    )

    liam_dob = date(2021, 5, 15)
    age_months = (date.today().year - liam_dob.year) * 12 + (date.today().month - liam_dob.month)

    liam = Student(
        student_id=student_id,
        first_name="Liam",
        last_name="Ochieng",
        date_of_birth=liam_dob,
        age_months=age_months,
        gender="Male",
        is_active=True,
        stream="East",
        academic_level_id=maple_level.id,
        class_id=maple_class.id,
        transport_route_id=westlands_route.id,
    )
    session.add(liam)
    session.flush()

    # Previous education
    session.add(PreviousEducation(
        student_id=liam.id,
        has_previous=True,
        school_name="Sunshine Nursery",
        level_completed="Baby Class",
        document_path=None,
    ))

    # Medical information
    session.add(MedicalInformation(
        student_id=liam.id,
        allergies="Peanuts",
        allergies_document=None,
        chronic_symptoms=None,
        chronic_document=None,
        vaccination_document=None,
    ))

    # Parents
    session.add(ParentInfo(
        student_id=liam.id,
        full_name="Grace Ochieng",
        email="grace.ochieng@example.com",
        phone="+254700111222",
        relationship=ParentRelationship.MOTHER,
        is_primary=True,
        id_document="id_scans/grace_ochieng.pdf",
        pickup_authorized=True,
    ))
    session.add(ParentInfo(
        student_id=liam.id,
        full_name="Peter Ochieng",
        email="peter.ochieng@example.com",
        phone="+254700333444",
        relationship=ParentRelationship.FATHER,
        is_primary=False,
        id_document="id_scans/peter_ochieng.pdf",
        pickup_authorized=True,
    ))

    # Transport assignment record
    session.add(StudentRoute(
        student_id=liam.id,
        route_id=westlands_route.id,
        direction=TransportDirection.TWO_WAY,
        use_daily_rate=False,
        active=True,
    ))

    # Attendance today
    session.add(Attendance(
        student_id=liam.id,
        attendance_date=date.today(),
        status=AttendanceStatus.PRESENT,
    ))

    # Supplies
    session.add(StudentSupply(
        student_id=liam.id,
        item_name="Pencils (pack of 12)",
        quantity=2,
        term="Term 1 2026",
    ))

    session.commit()

    return {
        "message": "Demo data seeded successfully.",
        "credentials": {
            "super_admin": {"email": "admin@sevenoak.edu", "password": "admin123"},
            "teacher": {"email": "teacher@sevenoak.edu", "password": "teacher123"},
        },
        "academic_year": "2025-2026",
        "classes_created": list(classes.keys()),
        "student": {
            "name": "Liam Ochieng",
            "student_id": student_id,
            "class": "Maple 2026",
            "stream": "East",
        },
    }
