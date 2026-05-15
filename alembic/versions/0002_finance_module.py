"""Finance module – sibling groups, club fee_amount, fee tables, payment tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-15 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add RECEIPT to documentcategory enum (create the type first if it was never
    #    created by 0001, e.g. when the DB was bootstrapped via create_all + stamp)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'documentcategory') THEN
                CREATE TYPE documentcategory AS ENUM (
                    'previous_education','medical_allergy','medical_chronic',
                    'medical_vaccination','parent_id','other','receipt'
                );
            ELSE
                ALTER TYPE documentcategory ADD VALUE IF NOT EXISTS 'receipt';
            END IF;
        END $$;
    """)

    # 2. Create sibling_group table
    op.create_table(
        "sibling_group",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # 3. Alter student table: add sibling_group_id FK and is_reported_back
    op.add_column(
        "student",
        sa.Column("sibling_group_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_student_sibling_group_id",
        "student",
        "sibling_group",
        ["sibling_group_id"],
        ["id"],
    )
    op.add_column(
        "student",
        sa.Column(
            "is_reported_back",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # 4. Alter club table: add fee_amount
    op.add_column(
        "club",
        sa.Column("fee_amount", sa.Numeric(12, 2), nullable=True),
    )

    # 5. Create fee_item table
    op.create_table(
        "fee_item",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("default_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fee_item_name", "fee_item", ["name"])
    op.create_index("ix_fee_item_category", "fee_item", ["category"])

    # 6. Create fee_schedule table
    op.create_table(
        "fee_schedule",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("fee_item_id", sa.Integer(), nullable=False),
        sa.Column("academic_level_id", sa.Integer(), nullable=True),
        sa.Column("class_id", sa.Integer(), nullable=True),
        sa.Column("student_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("term_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["fee_item_id"], ["fee_item.id"]),
        sa.ForeignKeyConstraint(["academic_level_id"], ["academic_level.id"]),
        sa.ForeignKeyConstraint(["class_id"], ["school_class.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.ForeignKeyConstraint(["term_id"], ["term.id"]),
        sa.CheckConstraint(
            "(CASE WHEN academic_level_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN class_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN student_id IS NOT NULL THEN 1 ELSE 0 END) = 1",
            name="chk_fee_schedule_scope",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fee_schedule_fee_item_id", "fee_schedule", ["fee_item_id"])
    op.create_index("ix_fee_schedule_academic_level_id", "fee_schedule", ["academic_level_id"])
    op.create_index("ix_fee_schedule_class_id", "fee_schedule", ["class_id"])
    op.create_index("ix_fee_schedule_student_id", "fee_schedule", ["student_id"])
    op.create_index("ix_fee_schedule_term_id", "fee_schedule", ["term_id"])

    # 7. Create student_fee table
    op.create_table(
        "student_fee",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("fee_item_id", sa.Integer(), nullable=False),
        sa.Column("term_id", sa.Integer(), nullable=True),
        sa.Column("academic_year_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "is_paid",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "date_charged",
            sa.Date(),
            nullable=False,
            server_default=sa.text("CURRENT_DATE"),
        ),
        sa.Column("date_paid", sa.Date(), nullable=True),
        sa.Column("source_ref", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.ForeignKeyConstraint(["fee_item_id"], ["fee_item.id"]),
        sa.ForeignKeyConstraint(["term_id"], ["term.id"]),
        sa.ForeignKeyConstraint(["academic_year_id"], ["academic_year.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_student_fee_student_id", "student_fee", ["student_id"])
    op.create_index("ix_student_fee_fee_item_id", "student_fee", ["fee_item_id"])
    op.create_index("ix_student_fee_term_id", "student_fee", ["term_id"])
    op.create_index("ix_student_fee_academic_year_id", "student_fee", ["academic_year_id"])

    # 8. Create payment table
    op.create_table(
        "payment",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("payment_method", sa.String(), nullable=False),
        sa.Column("reference_number", sa.String(), nullable=True),
        sa.Column("recorded_by_id", sa.Integer(), nullable=False),
        sa.Column("receipt_number", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"]),
        sa.ForeignKeyConstraint(["recorded_by_id"], ["team.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("receipt_number"),
    )
    op.create_index("ix_payment_student_id", "payment", ["student_id"])
    op.create_index("ix_payment_recorded_by_id", "payment", ["recorded_by_id"])
    op.create_index("ix_payment_receipt_number", "payment", ["receipt_number"], unique=True)

    # 9. Create payment_allocation table
    op.create_table(
        "payment_allocation",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("payment_id", sa.Integer(), nullable=False),
        sa.Column("student_fee_id", sa.Integer(), nullable=False),
        sa.Column("amount_allocated", sa.Numeric(12, 2), nullable=False),
        sa.ForeignKeyConstraint(["payment_id"], ["payment.id"]),
        sa.ForeignKeyConstraint(["student_fee_id"], ["student_fee.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payment_allocation_payment_id", "payment_allocation", ["payment_id"])
    op.create_index("ix_payment_allocation_student_fee_id", "payment_allocation", ["student_fee_id"])


def downgrade() -> None:
    op.drop_table("payment_allocation")
    op.drop_table("payment")
    op.drop_table("student_fee")
    op.drop_table("fee_schedule")
    op.drop_table("fee_item")
    op.drop_column("club", "fee_amount")
    op.drop_constraint("fk_student_sibling_group_id", "student", type_="foreignkey")
    op.drop_column("student", "is_reported_back")
    op.drop_column("student", "sibling_group_id")
    op.drop_table("sibling_group")
    # Note: PostgreSQL does not support removing enum values,
    # so the 'receipt' value added to documentcategory cannot be reverted here.
