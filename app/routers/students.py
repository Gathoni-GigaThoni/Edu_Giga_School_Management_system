from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date

from app.database import get_session
from app.models.student import Student
from app.models.team import Team
from app.schemas.student import StudentCreate, StudentRead
from app.models.enums import LevelCode, HouseName
from app.services.student_id_generator import generate_student_id
from app.schemas.student_with_teacher import StudentReadWithTeacher

router = APIRouter(prefix="/students", tags=["Students"])

# Mapping from level to house
LEVEL_TO_HOUSE = {
    LevelCode.BABY: HouseName.SUNFLOWER,
    LevelCode.PLAYGROUP: HouseName.BLUEBELL,
    LevelCode.PP1: HouseName.DAFFODIL,
    LevelCode.PP2: HouseName.MARIGOLD,
}

@router.post("/", response_model=StudentRead)
def create_student(student_data: StudentCreate, session: Session = Depends(get_session)):
    # 1. Validate homeroom teacher if provided
    if student_data.homeroom_teacher_id is not None:
        teacher = session.get(Team, student_data.homeroom_teacher_id)
        if not teacher:
            raise HTTPException(status_code=400, detail="Homeroom teacher not found")
        if teacher.role != "teacher":
            raise HTTPException(status_code=400, detail="Assigned staff member is not a teacher")

    # 2. Generate student_id (uses session to count existing students)
    student_id = generate_student_id(
        session,
        student_data.level,
        student_data.section,
        student_data.enrollment_year
    )

    # 3. Compute age in months
    today = date.today()
    dob = student_data.date_of_birth
    age_months = (today.year - dob.year) * 12 + (today.month - dob.month)

    # 4. Assign house based on level
    house = LEVEL_TO_HOUSE[student_data.level]

    # 5. Create Student instance
    student = Student(
        **student_data.dict(),
        student_id=student_id,
        age_months=age_months,
        house=house
    )
    session.add(student)
    session.commit()
    session.refresh(student)
    return student

@router.get("/", response_model=list[StudentRead])
def list_students(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    students = session.exec(select(Student).offset(skip).limit(limit)).all()
    return students

@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: int, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.get("/with-teacher/", response_model=list[StudentReadWithTeacher])
def list_students_with_teacher(session: Session = Depends(get_session)):
    # Join Student with Team to get teacher details
    statement = select(Student).join(Team, Student.homeroom_teacher_id == Team.id, isouter=True)
    students = session.exec(statement).all()
    return students