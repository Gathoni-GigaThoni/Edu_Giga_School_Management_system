# app/routers/students.py
"""
Endpoints for student registration and profile access.

Permissions matrix
──────────────────
Endpoint                              Min clearance
POST   /students/                     LEVEL_2
GET    /students/                     LEVEL_5 (any staff)
GET    /students/demographics/        LEVEL_5
GET    /students/class/{id}/students  LEVEL_5
GET    /students/{id}                 LEVEL_5
GET    /students/{id}/full-profile    LEVEL_5 (teachers: own class only)
GET    /students/teacher-view/{id}    teacher of student (own class only)
"""
from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.student import Student
from app.models.academic_level import AcademicLevel
from app.models.class_ import SchoolClass
from app.models.team import Team
from app.models.route import Route
from app.models.student_route import StudentRoute
from app.models.previous_education import PreviousEducation
from app.models.medical_information import MedicalInformation
from app.models.parent_info import ParentInfo
from app.models.attendance import Attendance
from app.models.skill_assessment import SkillAssessment
from app.models.skill import Skill
from app.models.discipline import DisciplinaryLog
from app.models.student_supply import StudentSupply
from app.models.enums import ClearanceLevel
from app.schemas.student import StudentRegisterRequest, StudentRead
from app.services.student_id_generator import generate_student_id
from app.dependencies import get_current_staff, require_clearance, require_teacher_of_student
from app.serializers import filter_fields_by_clearance

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def register_student(
    payload: StudentRegisterRequest,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    """
    Full student registration: creates the Student record plus nested
    PreviousEducation, MedicalInformation, and ParentInfo records atomically.
    """
    level = session.get(AcademicLevel, payload.academic_level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Academic level not found")

    school_class = session.get(SchoolClass, payload.class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")

    if school_class.academic_level_id != level.id:
        raise HTTPException(status_code=400, detail="Class does not belong to the specified academic level")

    if payload.transport_route_id:
        if not session.get(Route, payload.transport_route_id):
            raise HTTPException(status_code=404, detail="Transport route not found")

    student_id = generate_student_id(session, level.code, payload.stream, payload.class_id)

    dob = payload.date_of_birth
    age_months = (date.today().year - dob.year) * 12 + (date.today().month - dob.month)

    student = Student(
        student_id=student_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        date_of_birth=dob,
        age_months=age_months,
        gender=payload.gender,
        is_active=payload.is_active,
        stream=payload.stream,
        academic_level_id=payload.academic_level_id,
        class_id=payload.class_id,
        transport_route_id=payload.transport_route_id,
    )
    session.add(student)
    session.flush()  # get student.id before committing

    if payload.previous_education:
        session.add(PreviousEducation(
            student_id=student.id,
            **payload.previous_education.model_dump(),
        ))

    if payload.medical_info:
        session.add(MedicalInformation(
            student_id=student.id,
            **payload.medical_info.model_dump(),
        ))

    for p in payload.parents:
        session.add(ParentInfo(
            student_id=student.id,
            full_name=p.full_name,
            email=p.email,
            phone=p.phone,
            relationship=p.relationship,
            is_primary=p.is_primary,
            id_document=p.id_document,
            pickup_authorized=p.pickup_authorized,
        ))

    # If transport is specified, also create a detailed StudentRoute record
    if payload.transport_route_id:
        session.add(StudentRoute(
            student_id=student.id,
            route_id=payload.transport_route_id,
            direction="two_way",
            active=True,
        ))

    session.commit()
    session.refresh(student)
    return student


@router.get("/", response_model=List[StudentRead])
def list_students(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    _: Team = Depends(get_current_staff),
):
    return session.exec(select(Student).offset(skip).limit(limit)).all()


@router.get("/demographics/")
def get_demographics(
    session: Session = Depends(get_session),
    _: Team = Depends(get_current_staff),
):
    students = session.exec(select(Student)).all()
    gender_dist: dict = {}
    level_dist: dict = {}
    stream_dist: dict = {}

    for s in students:
        gender_dist[s.gender or "Unknown"] = gender_dist.get(s.gender or "Unknown", 0) + 1

        level = session.get(AcademicLevel, s.academic_level_id) if s.academic_level_id else None
        level_key = level.name if level else "Unknown"
        level_dist[level_key] = level_dist.get(level_key, 0) + 1

        stream_key = s.stream or "Unassigned"
        stream_dist[stream_key] = stream_dist.get(stream_key, 0) + 1

    return {
        "total_students": len(students),
        "gender_distribution": gender_dist,
        "level_distribution": level_dist,
        "stream_distribution": stream_dist,
    }


@router.get("/class/{class_id}/students", response_model=List[StudentRead])
def get_class_list(
    class_id: int,
    session: Session = Depends(get_session),
    _: Team = Depends(get_current_staff),
):
    if not session.get(SchoolClass, class_id):
        raise HTTPException(status_code=404, detail="Class not found")
    return session.exec(select(Student).where(Student.class_id == class_id)).all()


@router.get("/{student_id}/full-profile")
def get_full_profile(
    student_id: int,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(get_current_staff),
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_staff.role.value == "teacher":
        if not student.class_id:
            raise HTTPException(status_code=403, detail="Student has no class assigned")
        sc = session.get(SchoolClass, student.class_id)
        if not sc or sc.homeroom_teacher_id != current_staff.id:
            raise HTTPException(status_code=403, detail="You can only view profiles for students in your class")

    level = session.get(AcademicLevel, student.academic_level_id) if student.academic_level_id else None
    sc = session.get(SchoolClass, student.class_id) if student.class_id else None
    parents = session.exec(select(ParentInfo).where(ParentInfo.student_id == student_id)).all()
    medical = session.exec(select(MedicalInformation).where(MedicalInformation.student_id == student_id)).first()
    prev_edu = session.exec(select(PreviousEducation).where(PreviousEducation.student_id == student_id)).first()

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

    supplies = session.exec(select(StudentSupply).where(StudentSupply.student_id == student_id)).all()

    assessments = [
        {
            "skill_name": (session.get(Skill, sa.skill_id).name if session.get(Skill, sa.skill_id) else None),
            "rating": sa.rating,
            "teacher_comment": sa.teacher_comment,
            "assessment_date": sa.assessment_date.isoformat(),
        }
        for sa in assessments_raw
    ]

    profile = {
        "id": student.id,
        "student_id": student.student_id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "date_of_birth": student.date_of_birth.isoformat(),
        "age_months": student.age_months,
        "gender": student.gender,
        "is_active": student.is_active,
        "stream": student.stream,
        "level": level.name if level else None,
        "class_name": sc.name if sc else None,
        "transport_route_id": student.transport_route_id,
        "parents": [
            {
                "id": p.id,
                "full_name": p.full_name,
                "relationship": p.relationship,
                "phone": p.phone,
                "email": p.email,
                "is_primary": p.is_primary,
                "pickup_authorized": p.pickup_authorized,
            }
            for p in parents
        ],
        "medical": {
            "allergies": medical.allergies,
            "chronic_symptoms": medical.chronic_symptoms,
            "allergies_document": medical.allergies_document,
            "chronic_document": medical.chronic_document,
            "vaccination_document": medical.vaccination_document,
        } if medical else None,
        "previous_education": {
            "has_previous": prev_edu.has_previous,
            "school_name": prev_edu.school_name,
            "level_completed": prev_edu.level_completed,
            "document_path": prev_edu.document_path,
        } if prev_edu else None,
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
            {"id": s.id, "item_name": s.item_name, "quantity": s.quantity, "term": s.term}
            for s in supplies
        ],
    }

    return filter_fields_by_clearance(profile, current_staff.clearance_level)


@router.get("/{student_id}", response_model=StudentRead)
def get_student(
    student_id: int,
    session: Session = Depends(get_session),
    _: Team = Depends(get_current_staff),
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.get("/teacher-view/{student_id}", response_model=StudentRead)
def get_student_for_teacher(
    student_id: int,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(require_teacher_of_student()),
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
