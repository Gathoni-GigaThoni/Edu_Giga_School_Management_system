from fastapi import FastAPI
from app.database import init_db
from app.routers import team_router, students_router
from app.routers import auth
from app.routers import attendance
from app.routers import supplies

app = FastAPI(title="Seven Oak Kindergarten Management System")

# Include routers
app.include_router(team_router)
app.include_router(students_router)
app.include_router(attendance.router)
app.include_router(supplies.router)
app.include_router(auth.router)

@app.on_event("startup")
def on_startup():
    init_db()   # Create tables if they don't exist

@app.get("/")
def read_root():
    return {"message": "Welcome to Seven Oak Kindergarten System"}
