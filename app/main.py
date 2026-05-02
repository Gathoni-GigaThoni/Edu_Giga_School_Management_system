from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from app.database import init_db
from app.routers import team_router, students_router
from app.routers import auth
from app.routers import attendance
from app.routers import supplies
from app.routers import seed
from app.routers import skills
from app.routers import report_cards
from app.routers import dashboard
from app.routers import discipline
from app.exception_handlers import integrity_error_handler

from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Seven Oak Kindergarten Management System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://edugiga-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(IntegrityError, integrity_error_handler)

# Include routers
app.include_router(team_router)
app.include_router(students_router)
app.include_router(attendance.router)
app.include_router(supplies.router)
app.include_router(auth.router)
app.include_router(seed.router)
app.include_router(skills.router)
app.include_router(report_cards.router)
app.include_router(dashboard.router)
app.include_router(discipline.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Seven Oak Kindergarten System"}
