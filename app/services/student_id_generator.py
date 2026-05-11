"""
Student ID format:  SOIS-{level_code}-{stream_code}-{seq:03d}

  SOIS        = Seven Oak International School (school code)
  level_code  = AcademicLevel.code, e.g. "M" for Maple
  stream_code = first letter of stream, upper-cased, e.g. "E" for East
                (defaults to "X" when no stream is provided)
  seq         = 1-based count of students already in the same class + stream

Example: SOIS-M-E-001 is the first Maple-East student.
"""
from sqlmodel import Session, select, func
from app.models.student import Student


def generate_student_id(
    session: Session,
    level_code: str,
    stream: str | None,
    class_id: int,
) -> str:
    stream_code = (stream[0].upper() if stream else "X")

    count = session.exec(
        select(func.count()).select_from(Student).where(
            Student.class_id == class_id,
            Student.stream == stream,
        )
    ).one()

    seq = f"{count + 1:03d}"
    return f"SOIS-{level_code.upper()}-{stream_code}-{seq}"
