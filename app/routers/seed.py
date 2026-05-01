from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.auth import get_password_hash
from app.models.team import Team
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.student_supply import StudentSupply
from app.models.enums import (
    StaffRole, ClearanceLevel, LevelCode, ClassSection, HouseName, AttendanceStatus
)
from app.services.student_id_generator import generate_student_id

router = APIRouter(prefix="/seed", tags=["Seed"])


@router.post("/demo")
def seed_demo(session: Session = Depends(get_session)):
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
        location="Playgroup - Section A",
    )
    session.add(teacher)
    session.flush()

    liam_dob = date(2020, 5, 15)
    liam_id = generate_student_id(session, LevelCode.PLAYGROUP, ClassSection.A, 2026)
    liam = Student(
        student_id=liam_id,
        first_name="Liam",
        last_name="Ochieng",
        date_of_birth=liam_dob,
        level=LevelCode.PLAYGROUP,
        section=ClassSection.A,
        enrollment_year=2026,
        house=HouseName.BLUEBELL,
        homeroom_teacher_id=teacher.id,
    )
    liam.age_months = liam.compute_age_months()
    session.add(liam)
    session.flush()

    amani_dob = date(2020, 8, 20)
    amani_id = generate_student_id(session, LevelCode.PLAYGROUP, ClassSection.A, 2026)
    amani = Student(
        student_id=amani_id,
        first_name="Amani",
        last_name="Wanjiru",
        date_of_birth=amani_dob,
        level=LevelCode.PLAYGROUP,
        section=ClassSection.A,
        enrollment_year=2026,
        house=HouseName.BLUEBELL,
        homeroom_teacher_id=teacher.id,
    )
    amani.age_months = amani.compute_age_months()
    session.add(amani)
    session.flush()

    today = date.today()
    session.add(Attendance(
        student_id=liam.id,
        attendance_date=today,
        status=AttendanceStatus.PRESENT,
    ))
    session.add(Attendance(
        student_id=amani.id,
        attendance_date=today,
        status=AttendanceStatus.ABSENT,
        notes="Sick",
    ))

    session.add(StudentSupply(
        student_id=liam.id,
        item_name="Pencils (pack)",
        quantity=2,
        term="Term 1 2026",
    ))
    session.add(StudentSupply(
        student_id=amani.id,
        item_name="Crayons",
        quantity=1,
        term="Term 1 2026",
    ))

    session.commit()

    return {
        "message": "Demo data seeded successfully.",
        "credentials": {
            "super_admin": {"email": "admin@sevenoak.edu", "password": "admin123"},
            "teacher": {"email": "teacher@sevenoak.edu", "password": "teacher123"},
        },
        "students": [
            {"name": "Liam Ochieng", "student_id": liam_id},
            {"name": "Amani Wanjiru", "student_id": amani_id},
        ],
    }
