"""Initial schema – all tables

Revision ID: 0001
Revises:
Create Date: 2026-05-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('team',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('SUPER_ADMIN', 'MANAGER', 'TEACHER', 'KITCHEN', 'UTILITY', name='staffrole'), nullable=False),
        sa.Column('clearance_level', sa.Enum('LEVEL_1', 'LEVEL_2', 'LEVEL_3', 'LEVEL_4', 'LEVEL_5', name='clearancelevel'), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_team_email'), 'team', ['email'], unique=True)

    op.create_table('skill',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('applicable_level', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_skill_name'), 'skill', ['name'], unique=True)

    op.create_table('student',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('age_months', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(), nullable=True),
        sa.Column('level', sa.Enum('BABY', 'PLAYGROUP', 'PP1', 'PP2', name='levelcode'), nullable=False),
        sa.Column('section', sa.Enum('A', 'B', name='classsection'), nullable=False),
        sa.Column('enrollment_year', sa.Integer(), nullable=False),
        sa.Column('house', sa.Enum('SUNFLOWER', 'BLUEBELL', 'DAFFODIL', 'MARIGOLD', name='housename'), nullable=False),
        sa.Column('uses_transport', sa.Boolean(), nullable=False),
        sa.Column('transport_route', sa.String(), nullable=True),
        sa.Column('homeroom_teacher_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['homeroom_teacher_id'], ['team.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_student_student_id'), 'student', ['student_id'], unique=True)

    op.create_table('parent_guardian',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('relationship', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('is_emergency_contact', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('medical_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('allergies', sa.String(), nullable=True),
        sa.Column('medications', sa.String(), nullable=True),
        sa.Column('doctor_name', sa.String(), nullable=True),
        sa.Column('doctor_phone', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['student.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id'),
    )

    op.create_table('attendance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('attendance_date', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('PRESENT', 'ABSENT', 'LATE', name='attendancestatus'), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['student.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_attendance_attendance_date'), 'attendance', ['attendance_date'], unique=False)
    op.create_index(op.f('ix_attendance_student_id'), 'attendance', ['student_id'], unique=False)

    op.create_table('student_supply',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('item_name', sa.String(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('term', sa.String(), nullable=False),
        sa.Column('date_recorded', sa.Date(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['student.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_student_supply_student_id'), 'student_supply', ['student_id'], unique=False)

    op.create_table('skill_assessment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('term', sa.String(), nullable=False),
        sa.Column('academic_year', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Enum('EXCEEDING', 'MEETING', 'APPROACHING', 'NEEDS_INTERVENTION', name='skillrating'), nullable=False),
        sa.Column('teacher_comment', sa.String(), nullable=True),
        sa.Column('assessment_date', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['skill_id'], ['skill.id']),
        sa.ForeignKeyConstraint(['student_id'], ['student.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_skill_assessment_skill_id'), 'skill_assessment', ['skill_id'], unique=False)
    op.create_index(op.f('ix_skill_assessment_student_id'), 'skill_assessment', ['student_id'], unique=False)

    op.create_table('termly_report_comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('term', sa.String(), nullable=False),
        sa.Column('academic_year', sa.Integer(), nullable=False),
        sa.Column('homeroom_teacher_comment', sa.String(), nullable=True),
        sa.Column('principal_comment', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['student.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_termly_report_comment_student_id'), 'termly_report_comment', ['student_id'], unique=False)

    op.create_table('disciplinary_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('reported_by_id', sa.Integer(), nullable=False),
        sa.Column('incident_date', sa.DateTime(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('action_taken', sa.String(), nullable=True),
        sa.Column('severity', sa.Enum('MINOR', 'MODERATE', 'MAJOR', name='infractionseverity'), nullable=False),
        sa.Column('is_resolved', sa.Boolean(), nullable=False),
        sa.Column('resolution_notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['reported_by_id'], ['team.id']),
        sa.ForeignKeyConstraint(['student_id'], ['student.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_disciplinary_log_student_id'), 'disciplinary_log', ['student_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_disciplinary_log_student_id'), table_name='disciplinary_log')
    op.drop_table('disciplinary_log')
    op.drop_index(op.f('ix_termly_report_comment_student_id'), table_name='termly_report_comment')
    op.drop_table('termly_report_comment')
    op.drop_index(op.f('ix_skill_assessment_student_id'), table_name='skill_assessment')
    op.drop_index(op.f('ix_skill_assessment_skill_id'), table_name='skill_assessment')
    op.drop_table('skill_assessment')
    op.drop_index(op.f('ix_student_supply_student_id'), table_name='student_supply')
    op.drop_table('student_supply')
    op.drop_index(op.f('ix_attendance_student_id'), table_name='attendance')
    op.drop_index(op.f('ix_attendance_attendance_date'), table_name='attendance')
    op.drop_table('attendance')
    op.drop_table('medical_history')
    op.drop_table('parent_guardian')
    op.drop_index(op.f('ix_student_student_id'), table_name='student')
    op.drop_table('student')
    op.drop_index(op.f('ix_skill_name'), table_name='skill')
    op.drop_table('skill')
    op.drop_index(op.f('ix_team_email'), table_name='team')
    op.drop_table('team')
    op.execute('DROP TYPE IF EXISTS infractionseverity')
    op.execute('DROP TYPE IF EXISTS skillrating')
    op.execute('DROP TYPE IF EXISTS attendancestatus')
    op.execute('DROP TYPE IF EXISTS housename')
    op.execute('DROP TYPE IF EXISTS classsection')
    op.execute('DROP TYPE IF EXISTS levelcode')
    op.execute('DROP TYPE IF EXISTS clearancelevel')
    op.execute('DROP TYPE IF EXISTS staffrole')
