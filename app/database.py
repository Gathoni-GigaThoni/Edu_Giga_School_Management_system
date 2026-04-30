# app/database.py
from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(DATABASE_URL, echo=True)

# Import all models so SQLModel.metadata knows about them
# This must happen before create_all()
from app.models import Team, Student, ParentGuardian, MedicalHistory, Skill, SkillAssessment, TermlyReportComment

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session