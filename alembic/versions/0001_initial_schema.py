"""Initial schema – all tables

Revision ID: 0001
Revises:
Create Date: 2026-05-12 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Enum types ────────────────────────────────────────────────────────────
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE staffrole AS ENUM (
                'super_admin','manager','teacher','kitchen','utility'
            );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE clearancelevel AS ENUM (
                'LEVEL_1','LEVEL_2','LEVEL_3','LEVEL_4','LEVEL_5'
            );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE skillrating AS ENUM (
                'Exceeding Expectation','Meeting Expectation',
                'Approaching Expectation','Needs Intervention'
            );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE attendancestatus AS ENUM ('Present','Absent','Late');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE infractionSeverity AS ENUM ('minor','moderate','major');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE termname AS ENUM ('Term 1','Term 2','Term 3');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE transportdirection AS ENUM (
                'one_way_morning','one_way_evening','two_way'
            );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE parentrelationship AS ENUM ('mother','father','guardian');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE documentcategory AS ENUM (
                'previous_education','medical_allergy','medical_chronic',
                'medical_vaccination','parent_id','other'
            );
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)

    # ── team ──────────────────────────────────────────────────────────────────
    op.create_table(
        "team",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("clearance_level", sa.Integer(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_team_email"), "team", ["email"], unique=True)

    # ── skill ─────────────────────────────────────────────────────────────────
    op.create_table(
        "skill",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("applicable_level", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_skill_name"), "skill", ["name"], unique=True)

    # ── academic_level ────────────────────────────────────────────────────────
    op.create_table(
        "academic_level",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("code", sa.String(length=2), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_academic_level_name"), "academic_level", ["name"], unique=True)

    # ── club ──────────────────────────────────────────────────────────────────
    op.create_table(
        "club",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_club_name"), "club", ["name"], unique=True)

    # ── route ─────────────────────────────────────────────────────────────────
    op.create_table(
        "route",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("one_way_morning_price", sa.Float(), nullable=False),
        sa.Column("one_way_evening_price", sa.Float(), nullable=False),
        sa.Column("two_way_price", sa.Float(), nullable=False),
        sa.Column("daily_rate", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_route_name"), "route", ["name"], unique=True)

    # ── academic_year ─────────────────────────────────────────────────────────
    op.create_table(
        "academic_year",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_academic_year_name"), "academic_year", ["name"], unique=True)

    # ── term ──────────────────────────────────────────────────────────────────
    op.create_table(
        "term",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("academic_year_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("automatic_start", sa.Date(), nullable=False),
        sa.Column("automatic_end", sa.Date(), nullable=False),
        sa.Column("actual_start", sa.Date(), nullable=True),
        sa.Column("actual_end", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["academic_year_id"], ["academic_year.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_term_academic_year_id"), "term", ["academic_year_id"])

    # ── school_class ──────────────────────────────────────────────────────────
    op.create_table(
        "school_class",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("academic_level_id", sa.Integer(), nullable=False),
        sa.Column("academic_year_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("tuition_fee", sa.Float(), nullable=False),
        sa.Column("homeroom_teacher_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["academic_level_id"], ["academic_level.id"]),
        sa.ForeignKeyConstraint(["academic_year_id"], ["academic_year.id"]),
        sa.ForeignKeyConstraint(["homeroom_teacher_id"], ["team.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_school_class_academic_level_id"), "school_class", ["academic_level_id"])
    op.create_index(op.f("ix_school_class_academic_year_id"), "school_class", ["academic_year_id"])
    op.create_index(op.f("ix_school_class_name"), "school_class", ["name"])

    # ── student ───────────────────────────────────────────────────────────────
    op.create_table(
        "student",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.String(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("age_months", sa.Integer(), nullable=True),
        sa.Column("gender", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("stream", sa.String(), nullable=True),
        sa.Column("academic_level_id", sa.Integer(), nullable=True),
        sa.Column("class_id", sa.Integer(), nullable=True),
        sa.Column("transport_route_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["academic_level_id"], ["academic_level.id"]),
        sa.ForeignKeyConstraint(["class_id"], ["school_class.id"]),
        sa.ForeignKeyConstraint(["transport_route_id"], ["route.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_student_id"), "student", ["student_id"], unique=True)

    # ── parent_guardian (legacy) ──────────────────────────────────────────────
    op.create_table(
        "parent_guardian",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("relationship", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("is_emergency_contact", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── medical_history (legacy) ──────────────────────────────────────────────
    op.create_table(
        "medical_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("allergies", sa.String(), nullable=True),
        sa.Column("medications", sa.String(), nullable=True),
        sa.Column("doctor_name", sa.String(), nullable=True),
        sa.Column("doctor_phone", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id"),
    )

    # ── attendance ────────────────────────────────────────────────────────────
    op.create_table(
        "attendance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_attendance_student_id"), "attendance", ["student_id"])
    op.create_index(op.f("ix_attendance_attendance_date"), "attendance", ["attendance_date"])

    # ── student_supply ────────────────────────────────────────────────────────
    op.create_table(
        "student_supply",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("item_name", sa.String(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(), nullable=False),
        sa.Column("date_recorded", sa.Date(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_supply_student_id"), "student_supply", ["student_id"])

    # ── skill_assessment ──────────────────────────────────────────────────────
    op.create_table(
        "skill_assessment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(), nullable=False),
        sa.Column("academic_year", sa.Integer(), nullable=False),
        sa.Column("rating", sa.String(), nullable=False),
        sa.Column("teacher_comment", sa.String(), nullable=True),
        sa.Column("assessment_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["skill_id"], ["skill.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_skill_assessment_student_id"), "skill_assessment", ["student_id"])
    op.create_index(op.f("ix_skill_assessment_skill_id"), "skill_assessment", ["skill_id"])

    # ── termly_report_comment ─────────────────────────────────────────────────
    op.create_table(
        "termly_report_comment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(), nullable=False),
        sa.Column("academic_year", sa.Integer(), nullable=False),
        sa.Column("homeroom_teacher_comment", sa.String(), nullable=True),
        sa.Column("principal_comment", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_termly_report_comment_student_id"), "termly_report_comment", ["student_id"])

    # ── disciplinary_log ──────────────────────────────────────────────────────
    op.create_table(
        "disciplinary_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("reported_by_id", sa.Integer(), nullable=False),
        sa.Column("incident_date", sa.DateTime(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("action_taken", sa.String(), nullable=True),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("is_resolved", sa.Boolean(), nullable=False),
        sa.Column("resolution_notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["reported_by_id"], ["team.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_disciplinary_log_student_id"), "disciplinary_log", ["student_id"])

    # ── previous_education ────────────────────────────────────────────────────
    op.create_table(
        "previous_education",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("has_previous", sa.Boolean(), nullable=False),
        sa.Column("school_name", sa.String(), nullable=True),
        sa.Column("level_completed", sa.String(), nullable=True),
        sa.Column("document_path", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id"),
    )
    op.create_index(op.f("ix_previous_education_student_id"), "previous_education", ["student_id"])

    # ── medical_information ───────────────────────────────────────────────────
    op.create_table(
        "medical_information",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("allergies", sa.String(), nullable=True),
        sa.Column("allergies_document", sa.String(), nullable=True),
        sa.Column("chronic_symptoms", sa.String(), nullable=True),
        sa.Column("chronic_document", sa.String(), nullable=True),
        sa.Column("vaccination_document", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id"),
    )
    op.create_index(op.f("ix_medical_information_student_id"), "medical_information", ["student_id"])

    # ── parent_info ───────────────────────────────────────────────────────────
    op.create_table(
        "parent_info",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=False),
        sa.Column("relationship", sa.String(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("id_document", sa.String(), nullable=True),
        sa.Column("pickup_authorized", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_parent_info_student_id"), "parent_info", ["student_id"])

    # ── document ──────────────────────────────────────────────────────────────
    op.create_table(
        "document",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("file_name", sa.String(), nullable=False),
        sa.Column("upload_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_student_id"), "document", ["student_id"])

    # ── student_club ──────────────────────────────────────────────────────────
    op.create_table(
        "student_club",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("club_id", sa.Integer(), nullable=False),
        sa.Column("join_date", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["club_id"], ["club.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_club_student_id"), "student_club", ["student_id"])
    op.create_index(op.f("ix_student_club_club_id"), "student_club", ["club_id"])

    # ── student_route ─────────────────────────────────────────────────────────
    op.create_table(
        "student_route",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("direction", sa.String(), nullable=False),
        sa.Column("use_daily_rate", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["route_id"], ["route.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_route_student_id"), "student_route", ["student_id"])
    op.create_index(op.f("ix_student_route_route_id"), "student_route", ["route_id"])


def downgrade() -> None:
    op.drop_table("student_route")
    op.drop_table("student_club")
    op.drop_table("document")
    op.drop_table("parent_info")
    op.drop_table("medical_information")
    op.drop_table("previous_education")
    op.drop_table("disciplinary_log")
    op.drop_table("termly_report_comment")
    op.drop_table("skill_assessment")
    op.drop_table("student_supply")
    op.drop_table("attendance")
    op.drop_table("medical_history")
    op.drop_table("parent_guardian")
    op.drop_table("student")
    op.drop_table("school_class")
    op.drop_table("term")
    op.drop_table("academic_year")
    op.drop_table("route")
    op.drop_table("club")
    op.drop_table("academic_level")
    op.drop_table("skill")
    op.drop_table("team")
