from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from datetime import date
from app.database import get_session
from app.models.student import Student
from app.models.team import Team   # To verify teacher exists
from app.schemas.student import StudentCreate, StudentRead
from app.models.enums import LevelCode, HouseName

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
    # 1. Check if homeroom_teacher_id points to a valid teacher (if provided)
    if student_data.homeroom_teacher_id:
        teacher = session.get(Team, student_data.homeroom_teacher_id)
        if not teacher or teacher.role != "teacher":
            raise HTTPException(status_code=400, detail="Invalid homeroom teacher ID")

    # 2. Determine next sequential number for this level + enrollment_year
    existing_count = session.exec(
        select(func.count()).select_from(Student).where(
            Student.level == student_data.level,
            Student.enrollment_year == student_data.enrollment_year
        )
    ).one()
    sequential = f"{existing_count + 1:03d}"

    # 3. Build the student_id
    student_id = f"OS-{sequential}-{student_data.level.value}-{student_data.section.value}-{student_data.enrollment_year}"

    # 4. Compute age in months
    today = date.today()
    dob = student_data.date_of_birth
    age_months = (today.year - dob.year) * 12 + (today.month - dob.month)

    # 5. Assign house based on level
    house = LEVEL_TO_HOUSE[student_data.level]

    # 6. Create Student instance
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