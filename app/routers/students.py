# app/routers/students.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import date, timedelta

from app.database import get_session
from app.models.student import Student
from app.models.team import Team
from app.models.parent_guardian import ParentGuardian
from app.models.medical import MedicalHistory
from app.models.attendance import Attendance
from app.models.skill_assessment import SkillAssessment
from app.models.skill import Skill
from app.models.discipline import DisciplinaryLog
from app.models.student_supply import StudentSupply
from app.schemas.student import StudentCreate, StudentRead
from app.schemas.student_with_teacher import StudentReadWithTeacher
from app.schemas.student_teacher import StudentReadTeacher
from app.models.enums import LevelCode, ClassSection, HouseName, ClearanceLevel
from app.services.student_id_generator import generate_student_id
from app.dependencies import get_current_staff, require_clearance, require_teacher_of_student
from app.serializers import filter_fields_by_clearance

router = APIRouter(prefix="/students", tags=["Students"])

LEVEL_TO_HOUSE = {
    LevelCode.BABY: HouseName.SUNFLOWER,
    LevelCode.PLAYGROUP: HouseName.BLUEBELL,
    LevelCode.PP1: HouseName.DAFFODIL,
    LevelCode.PP2: HouseName.MARIGOLD,
}


@router.post("/", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: StudentCreate,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(require_clearance(ClearanceLevel.LEVEL_2))
):
    """
    Create a new student. Only staff with clearance level 2 (manager) and above.
    """
    # 1. Validate homeroom teacher if provided
    if student_data.homeroom_teacher_id is not None:
        teacher = session.get(Team, student_data.homeroom_teacher_id)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Homeroom teacher not found",
            )
        if teacher.role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned staff member is not a teacher",
            )

    # 2. Generate student_id
    student_id = generate_student_id(
        session,
        student_data.level,
        student_data.section,
        student_data.enrollment_year,
    )

    # 3. Compute age in months
    today = date.today()
    dob = student_data.date_of_birth
    age_months = (today.year - dob.year) * 12 + (today.month - dob.month)

    # 4. Assign house based on level
    house = LEVEL_TO_HOUSE[student_data.level]

    # 5. Create Student instance
    student = Student(
        **student_data.model_dump(),
        student_id=student_id,
        age_months=age_months,
        house=house,
    )
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


@router.get("/", response_model=list[StudentRead])
def list_students(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff)
):
    """
    List all students. Any authenticated staff member can view the basic list.
    """
    students = session.exec(select(Student).offset(skip).limit(limit)).all()
    return students


@router.get("/with-teacher/", response_model=list[StudentReadWithTeacher])
def list_students_with_teacher(
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff)
):
    """
    List students with their homeroom teacher details.
    """
    statement = select(Student).join(
        Team, Student.homeroom_teacher_id == Team.id, isouter=True
    )
    students = session.exec(statement).all()
    return students


@router.get("/class/{level}/{section}/students", response_model=list[StudentRead])
def get_class_list(
    level: LevelCode,
    section: ClassSection,
    enrollment_year: int,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff),
):
    students = session.exec(
        select(Student).where(
            Student.level == level,
            Student.section == section,
            Student.enrollment_year == enrollment_year,
        )
    ).all()
    return students


@router.get("/demographics/")
def get_demographics(
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff),
):
    students = session.exec(select(Student)).all()

    gender_dist: dict = {}
    grade_dist: dict = {}
    house_dist: dict = {}

    for s in students:
        gender_key = s.gender or "Unknown"
        gender_dist[gender_key] = gender_dist.get(gender_key, 0) + 1

        grade_key = s.level.value
        grade_dist[grade_key] = grade_dist.get(grade_key, 0) + 1

        house_key = s.house.value
        house_dist[house_key] = house_dist.get(house_key, 0) + 1

    return {
        "gender_distribution": gender_dist,
        "grade_distribution": grade_dist,
        "house_distribution": house_dist,
    }


@router.get("/{student_id}/full-profile")
def get_full_profile(
    student_id: int,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff),
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_staff.role == "teacher" and student.homeroom_teacher_id != current_staff.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view profiles for your own homeroom students",
        )

    parents = session.exec(
        select(ParentGuardian).where(ParentGuardian.student_id == student_id)
    ).all()

    medical = session.exec(
        select(MedicalHistory).where(MedicalHistory.student_id == student_id)
    ).first()

    thirty_days_ago = date.today() - timedelta(days=30)
    attendance_records = session.exec(
        select(Attendance).where(
            Attendance.student_id == student_id,
            Attendance.attendance_date >= thirty_days_ago,
        )
    ).all()

    assessments_raw = session.exec(
        select(SkillAssessment)
        .where(SkillAssessment.student_id == student_id)
        .order_by(SkillAssessment.assessment_date.desc())
        .limit(5)
    ).all()

    discipline_logs = session.exec(
        select(DisciplinaryLog)
        .where(DisciplinaryLog.student_id == student_id)
        .order_by(DisciplinaryLog.incident_date.desc())
    ).all()

    supplies = session.exec(
        select(StudentSupply).where(StudentSupply.student_id == student_id)
    ).all()

    assessments = []
    for sa in assessments_raw:
        skill = session.get(Skill, sa.skill_id)
        assessments.append({
            "skill_name": skill.name if skill else None,
            "rating": sa.rating,
            "teacher_comment": sa.teacher_comment,
            "assessment_date": sa.assessment_date.isoformat(),
        })

    profile = {
        "id": student.id,
        "student_id": student.student_id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "date_of_birth": student.date_of_birth.isoformat(),
        "age_months": student.age_months,
        "gender": student.gender,
        "level": student.level.value,
        "section": student.section.value,
        "enrollment_year": student.enrollment_year,
        "house": student.house.value,
        "transport_route": student.transport_route,
        "parents": [
            {
                "id": p.id,
                "full_name": p.full_name,
                "relationship": p.relationship,
                "phone": p.phone,
                "email": p.email,
                "address": p.address,
                "is_emergency_contact": p.is_emergency_contact,
            }
            for p in parents
        ],
        "medical": {
            "allergies": medical.allergies,
            "medications": medical.medications,
            "doctor_name": medical.doctor_name,
            "doctor_phone": medical.doctor_phone,
            "notes": medical.notes,
        } if medical else None,
        "attendance": {
            "total_days": len(attendance_records),
            "present": sum(1 for r in attendance_records if r.status == "Present"),
            "absent": sum(1 for r in attendance_records if r.status == "Absent"),
            "late": sum(1 for r in attendance_records if r.status == "Late"),
        },
        "assessments": assessments,
        "discipline": [
            {
                "id": d.id,
                "description": d.description,
                "severity": d.severity,
                "incident_date": d.incident_date.isoformat(),
                "action_taken": d.action_taken,
                "is_resolved": d.is_resolved,
                "resolution_notes": d.resolution_notes,
            }
            for d in discipline_logs
        ],
        "supplies": [
            {
                "id": s.id,
                "item_name": s.item_name,
                "quantity": s.quantity,
                "term": s.term,
            }
            for s in supplies
        ],
    }

    return filter_fields_by_clearance(profile, current_staff.clearance_level)


@router.get("/{student_id}", response_model=StudentRead)
def get_student(
    student_id: int,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff)
):
    """
    Retrieve full details of a single student. Available to any authenticated staff.
    For teachers, use `/teacher-view/{student_id}` instead to see limited data.
    """
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    return student


@router.get("/teacher-view/{student_id}", response_model=StudentReadTeacher)
def get_student_for_teacher(
    student_id: int,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(require_teacher_of_student())  # ← no argument here
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student