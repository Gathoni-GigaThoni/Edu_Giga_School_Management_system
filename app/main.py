from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from app.database import init_db
from app.routers import team_router, students_router
from app.routers import auth
from app.routers import attendance
from app.routers import supplies
from app.routers import seed
from app.exception_handlers import integrity_error_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Seven Oak Kindergarten Management System", lifespan=lifespan)

app.add_exception_handler(IntegrityError, integrity_error_handler)

# Include routers
app.include_router(team_router)
app.include_router(students_router)
app.include_router(attendance.router)
app.include_router(supplies.router)
app.include_router(auth.router)
app.include_router(seed.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Seven Oak Kindergarten System"}
