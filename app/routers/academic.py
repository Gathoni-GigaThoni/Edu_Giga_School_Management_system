# app/routers/academic.py
"""
Endpoints for academic structure: AcademicLevel, AcademicYear, Term, SchoolClass.

Permissions matrix
──────────────────
Endpoint                             Min clearance
POST   /academic-levels/             LEVEL_1
GET    /academic-levels/             LEVEL_5 (any staff)
POST   /academic-years/              LEVEL_1
GET    /academic-years/              LEVEL_5
GET    /academic-years/{id}          LEVEL_5
PATCH  /academic-years/{id}/terms/{term_id}  LEVEL_2
POST   /classes/                     LEVEL_2
GET    /classes/                     LEVEL_5
GET    /classes/{id}                 LEVEL_5
PATCH  /classes/{id}                 LEVEL_2
"""
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models.academic_level import AcademicLevel
from app.models.academic_year import AcademicYear
from app.models.term import Term
from app.models.class_ import SchoolClass
from app.models.team import Team
from app.models.enums import ClearanceLevel, TermName
from app.schemas.academic_level import AcademicLevelCreate, AcademicLevelRead
from app.schemas.academic_year import AcademicYearCreate, AcademicYearRead, AcademicYearReadSimple
from app.schemas.term import TermRead, TermActualDatesUpdate
from app.schemas.school_class import SchoolClassCreate, SchoolClassRead, SchoolClassUpdate
from app.dependencies import get_current_staff, require_clearance

router = APIRouter(tags=["Academic Setup"])


# ── Academic Levels ─────────────────────────────────────────────────────────

@router.post("/academic-levels/", response_model=AcademicLevelRead, status_code=status.HTTP_201_CREATED)
def create_academic_level(
    data: AcademicLevelCreate,
    session: Session = Depends(get_session),
    _: Team = Depends(require_clearance(ClearanceLevel.LEVEL_1)),
):
    existing = session.exec(select(AcademicLevel).where(AcademicLevel.name == data.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="An academic level with this name already exists")

    level = AcademicLevel(**data.model_dump())
    session.add(level)
    session.commit()
    session.refresh(level)
    return level


@router.get("/academic-levels/", response_model=List[AcademicLevelRead])
def list_academic_levels(
    session: Session = Depends(get_session),
    _: Team = Depends(get_current_staff),
):
    return session.exec(select(AcademicLevel)).all()


# ── Academic Years ───────────────────────────────────────────────────────────

def _default_term_dates(start_year: int) -> list[dict]:
    """Return the three standard terms for a year that starts in September."""
    return [
        {
            "name": TermName.TERM_1,
            "automatic_start": date(start_year, 9, 1),
            "automatic_end": date(start_year, 12, 12),
        },
        {
            "name": TermName.TERM_2,
            "automatic_start": date(start_year + 1, 1, 8),
            "automatic_end": date(start_year + 1, 4, 3),
        },
        {
            "name": TermName.TERM_3,
            "automatic_start": date(start_year + 1, 4, 23),
            "automatic_end": date(start_year + 1, 7, 17),
        },
    ]


@router.post("/academic-years/", response_model=AcademicYearRead, status_code=status.HTTP_201_CREATED)
def create_academic_year(
    data: AcademicYearCreate,
    session: Session = Depends(get_session),
    _: Team = Depends(require_clearance(ClearanceLevel.LEVEL_1)),
):
    existing = session.exec(select(AcademicYear).where(AcademicYear.name == data.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Academic year already exists")

    year = AcademicYear(**data.model_dump())
    session.add(year)
    session.flush()   # get year.id without committing

    for td in _default_term_dates(year.start_date.year):
        session.add(Term(academic_year_id=year.id, **td))

    session.commit()
    session.refresh(year)
    return year


@router.get("/academic-years/", response_model=List[AcademicYearReadSimple])
def list_academic_years(
    session: Session = Depends(get_session),
    _: Team = Depends(get_current_staff),
):
    return session.exec(select(AcademicYear)).all()


@router.get("/academic-years/{year_id}", response_model=AcademicYearRead)
def get_academic_year(
    year_id: int,
    session: Session = Depends(get_session),
    _: Team = Depends(get_current_staff),
):
    year = session.get(AcademicYear, year_id)
    if not year:
        raise HTTPException(status_code=404, detail="Academic year not found")
    return year


@router.patch("/academic-years/{year_id}/terms/{term_id}", response_model=TermRead)
def update_term_actual_dates(
    year_id: int,
    term_id: int,
    data: TermActualDatesUpdate,
    session: Session = Depends(get_session),
    _: Team = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    term = session.get(Term, term_id)
    if not term or term.academic_year_id != year_id:
        raise HTTPException(status_code=404, detail="Term not found in this academic year")

    if data.actual_start and not (term.automatic_start <= data.actual_start <= term.automatic_end):
        raise HTTPException(
            status_code=400,
            detail=f"actual_start must be within {term.automatic_start} – {term.automatic_end}",
        )
    if data.actual_end and not (term.automatic_start <= data.actual_end <= term.automatic_end):
        raise HTTPException(
            status_code=400,
            detail=f"actual_end must be within {term.automatic_start} – {term.automatic_end}",
        )

    if data.actual_start is not None:
        term.actual_start = data.actual_start
    if data.actual_end is not None:
        term.actual_end = data.actual_end

    session.add(term)
    session.commit()
    session.refresh(term)
    return term


# ── Classes ──────────────────────────────────────────────────────────────────

@router.post("/classes/", response_model=SchoolClassRead, status_code=status.HTTP_201_CREATED)
def create_class(
    data: SchoolClassCreate,
    session: Session = Depends(get_session),
    _: Team = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    level = session.get(AcademicLevel, data.academic_level_id)
    if not level:
        raise HTTPException(status_code=404, detail="Academic level not found")

    year = session.get(AcademicYear, data.academic_year_id)
    if not year:
        raise HTTPException(status_code=404, detail="Academic year not found")

    if data.homeroom_teacher_id:
        teacher = session.get(Team, data.homeroom_teacher_id)
        if not teacher or teacher.role.value != "teacher":
            raise HTTPException(status_code=400, detail="homeroom_teacher_id must reference an active teacher")

    # Auto-generate class name
    name = f"{level.name} {year.end_year}"

    # Prevent duplicates
    existing = session.exec(
        select(SchoolClass).where(
            SchoolClass.academic_level_id == data.academic_level_id,
            SchoolClass.academic_year_id == data.academic_year_id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Class '{name}' already exists for this academic year")

    school_class = SchoolClass(
        academic_level_id=data.academic_level_id,
        academic_year_id=data.academic_year_id,
        name=name,
        tuition_fee=data.tuition_fee,
        homeroom_teacher_id=data.homeroom_teacher_id,
    )
    session.add(school_class)
    session.commit()
    session.refresh(school_class)
    return school_class


@router.get("/classes/", response_model=List[SchoolClassRead])
def list_classes(
    academic_year_id: Optional[int] = Query(default=None),
    session: Session = Depends(get_session),
    _: Team = Depends(get_current_staff),
):
    query = select(SchoolClass)
    if academic_year_id:
        query = query.where(SchoolClass.academic_year_id == academic_year_id)
    return session.exec(query).all()


@router.get("/classes/{class_id}", response_model=SchoolClassRead)
def get_class(
    class_id: int,
    session: Session = Depends(get_session),
    _: Team = Depends(get_current_staff),
):
    school_class = session.get(SchoolClass, class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return school_class


@router.patch("/classes/{class_id}", response_model=SchoolClassRead)
def update_class(
    class_id: int,
    data: SchoolClassUpdate,
    session: Session = Depends(get_session),
    _: Team = Depends(require_clearance(ClearanceLevel.LEVEL_2)),
):
    school_class = session.get(SchoolClass, class_id)
    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")

    if data.homeroom_teacher_id is not None:
        teacher = session.get(Team, data.homeroom_teacher_id)
        if not teacher or teacher.role.value != "teacher":
            raise HTTPException(status_code=400, detail="homeroom_teacher_id must reference an active teacher")
        school_class.homeroom_teacher_id = data.homeroom_teacher_id

    if data.tuition_fee is not None:
        school_class.tuition_fee = data.tuition_fee

    session.add(school_class)
    session.commit()
    session.refresh(school_class)
    return school_class
