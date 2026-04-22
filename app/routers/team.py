from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamRead

router = APIRouter(prefix="/team", tags=["Team"])

@router.post("/", response_model=TeamRead)
def create_team_member(member: TeamCreate, session: Session = Depends(get_session)):
    # Convert Pydantic schema to SQLModel instance
    db_member = Team.from_orm(member)
    session.add(db_member)
    session.commit()
    session.refresh(db_member)
    return db_member

@router.get("/", response_model=list[TeamRead])
def list_team_members(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    members = session.exec(select(Team).offset(skip).limit(limit)).all()
    return members

@router.get("/{member_id}", response_model=TeamRead)
def get_team_member(member_id: int, session: Session = Depends(get_session)):
    member = session.get(Team, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    return member