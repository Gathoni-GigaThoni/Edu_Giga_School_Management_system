from sqlmodel import Session, select, func
from app.models.student import Student
from app.models.enums import LevelCode, ClassSection

def generate_student_id(
    session: Session,
    level: LevelCode,
    section: ClassSection,
    enrollment_year: int
) -> str:
    """
    Generate a unique student ID in the format:
    OS-{sequential:03d}-{level}-{section}-{year}

    The sequential number is based on existing students in the same level and year.
    """
    # Count existing students with same level and enrollment year
    count = session.exec(
        select(func.count()).select_from(Student).where(
            Student.level == level,
            Student.enrollment_year == enrollment_year
        )
    ).one()

    sequential = f"{count + 1:03d}"
    return f"OS-{sequential}-{level.value}-{section.value}-{enrollment_year}"