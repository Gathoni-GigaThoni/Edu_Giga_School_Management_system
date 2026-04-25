# app/dependencies.py

from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.auth import oauth2_scheme, decode_access_token
from app.models.team import Team
from app.models.student import Student
from app.models.enums import ClearanceLevel


async def get_current_staff(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> Team:
    """
    Decode the JWT, extract the user ID, and return the corresponding
    active staff member. Raises 401 if the token is invalid, expired,
    or the user no longer exists / is inactive.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid subject claim",
        )

    staff = session.get(Team, user_id)
    if staff is None or not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return staff


def require_clearance(min_level: ClearanceLevel):
    """
    Dependency factory that ensures the current staff member has at least
    the specified clearance level.
    """
    async def checker(
        current_staff: Team = Depends(get_current_staff),
    ) -> Team:
        if current_staff.clearance_level.value > min_level.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires clearance level {min_level.value} or higher",
            )
        return current_staff
    return checker


def require_teacher_of_student():
    """
    Dependency that checks if the current staff member is a teacher
    and is the homeroom teacher of the student given in the path parameter.
    """
    async def checker(
        student_id: int,                                 # ← injected from path
        current_staff: Team = Depends(get_current_staff),
        session: Session = Depends(get_session),
    ) -> Team:
        if current_staff.role == "teacher":
            student = session.get(Student, student_id)
            if student is None:
                raise HTTPException(status_code=404, detail="Student not found")
            if student.homeroom_teacher_id != current_staff.id:
                raise HTTPException(
                    status_code=403,
                    detail="You can only access students in your own class",
                )
        return current_staff
    return checker