# app/routers/team.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamRead
from app.models.enums import ClearanceLevel
from app.dependencies import get_current_staff, require_clearance
from app.auth import get_password_hash

router = APIRouter(prefix="/team", tags=["Team"])


@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team_member(
    member: TeamCreate,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(require_clearance(ClearanceLevel.LEVEL_1))
):
    """
    Create a new staff member. Only super admins (clearance level 1) are allowed.
    """
    # Check if email already exists
    existing = session.exec(select(Team).where(Team.email == member.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A staff member with this email already exists",
        )

    # Create the team member with hashed password
    db_member = Team(
        first_name=member.first_name,
        last_name=member.last_name,
        email=member.email,
        hashed_password=get_password_hash(member.password),
        role=member.role,
        clearance_level=member.clearance_level,
        location=member.location,
        is_active=member.is_active,
    )
    session.add(db_member)
    session.commit()
    session.refresh(db_member)
    return db_member


@router.get("/", response_model=list[TeamRead])
def list_team_members(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(require_clearance(ClearanceLevel.LEVEL_3))
):
    """
    List all staff members. Only managers (clearance ≤3) and above.
    """
    members = session.exec(select(Team).offset(skip).limit(limit)).all()
    return members


@router.get("/{member_id}", response_model=TeamRead)
def get_team_member(
    member_id: int,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(require_clearance(ClearanceLevel.LEVEL_3))
):
    """
    Retrieve a single staff member by ID. Managers and above.
    """
    member = session.get(Team, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found",
        )
    return member


@router.patch("/{member_id}", response_model=TeamRead)
def update_team_member(
    member_id: int,
    member_update: TeamCreate,   # Reuses the same schema; password is optional here? We'll address later.
    session: Session = Depends(get_session),
    current_staff: Team = Depends(require_clearance(ClearanceLevel.LEVEL_1))
):
    """
    Update a staff member's details. Only super admins.
    """
    member = session.get(Team, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    update_data = member_update.dict(exclude_unset=True)
    # If password is being updated, hash it
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    elif "password" in update_data:
        del update_data["password"]   # remove None or empty

    for key, value in update_data.items():
        setattr(member, key, value)

    session.add(member)
    session.commit()
    session.refresh(member)
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team_member(
    member_id: int,
    session: Session = Depends(get_session),
    current_staff: Team = Depends(require_clearance(ClearanceLevel.LEVEL_1))
):
    """
    Delete a staff member. Only super admins.
    """
    member = session.get(Team, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    session.delete(member)
    session.commit()
    # No content returned
    return