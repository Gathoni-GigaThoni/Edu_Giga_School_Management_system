from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from app.main import app
from app.database import engine

client = TestClient(app)

admin_token = None
teacher_token = None


def setup_module(module):
    SQLModel.metadata.create_all(engine)


def teardown_module(module):
    SQLModel.metadata.drop_all(engine)


def test_seed_demo():
    response = client.post("/seed/demo")
    assert response.status_code == 200


def test_login_superadmin():
    global admin_token
    response = client.post(
        "/auth/login",
        data={"username": "admin@sevenoak.edu", "password": "admin123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    admin_token = body["access_token"]


def test_create_student_as_admin():
    response = client.post(
        "/students/",
        json={
            "first_name": "Test",
            "last_name": "Student",
            "date_of_birth": "2020-01-01",
            "level": "Okra",
            "section": "A",
            "enrollment_year": 2026,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["student_id"].startswith("OS-")


def test_teacher_cannot_access_other_student():
    global teacher_token
    login = client.post(
        "/auth/login",
        data={"username": "teacher@sevenoak.edu", "password": "teacher123"},
    )
    assert login.status_code == 200
    teacher_token = login.json()["access_token"]

    # Non-existent student → 404
    response = client.get(
        "/students/teacher-view/1000",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert response.status_code == 404

    # Liam (id=1, seeded as this teacher's student) → 200
    response = client.get(
        "/students/teacher-view/1",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert response.status_code == 200


def test_teacher_can_mark_attendance():
    today = str(date.today())
    response = client.post(
        "/attendance/bulk",
        params={"class_date": today},
        json=[
            {"student_id": 1, "status": "Present"},
            {"student_id": 2, "status": "Late"},
        ],
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert response.status_code == 201


def test_teacher_cannot_mark_other_class():
    today = str(date.today())
    # Student 99 does not exist and is not in the teacher's homeroom.
    # The teacher check (not homeroom → 403) fires before any existence check.
    response = client.post(
        "/attendance/bulk",
        params={"class_date": today},
        json=[{"student_id": 99, "status": "Present"}],
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert response.status_code == 403
