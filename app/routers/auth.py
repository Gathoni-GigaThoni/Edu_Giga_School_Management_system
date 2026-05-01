# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_session
from app.models.team import Team
from app.schemas.auth import LoginRequest, Token
from app.auth import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    # form_data.username is the email the user typed
    statement = select(Team).where(Team.email == form_data.username)
    user = session.exec(statement).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")

@router.post("/create-super-admin", response_model=Token)
def create_super_admin(
    email: str,
    password: str,
    first_name: str = "Super",
    last_name: str = "Admin",
    session: Session = Depends(get_session)
):
    # Check if already exists
    existing = session.exec(select(Team).where(Team.email == email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    from app.auth import get_password_hash
    from app.models.enums import StaffRole, ClearanceLevel

    admin = Team(
        first_name=first_name,
        last_name=last_name,
        email=email,
        hashed_password=get_password_hash(password),
        role=StaffRole.SUPER_ADMIN,
        clearance_level=ClearanceLevel.LEVEL_1,
        location="Main Campus",
        is_active=True
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)

    access_token = create_access_token(data={"sub": str(admin.id)})
    return Token(access_token=access_token, token_type="bearer")